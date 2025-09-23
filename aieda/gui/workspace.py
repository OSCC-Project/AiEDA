# -*- encoding: utf-8 -*-
"""
@File : workspace.py
@Author : yell
@Desc : Workspace UI for AiEDA system
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                             QMessageBox, QGroupBox, QGridLayout, QCheckBox,QGraphicsView)
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtCore import Qt

from aieda.gui.chip import ChipLayout
from aieda.gui.net import NetLayout
from aieda.gui.patch import PatchLayout
from aieda.gui.patches import PatchesLayout
from aieda.gui.layer import LayerLayout
from aieda.workspace import Workspace


class WorkspaceUI(QWidget):
    """workspace ui"""
    
    def __init__(self, workspace, parent=None):
        # Call the superclass constructor first
        super().__init__(parent)
        
        # Initialize workspace and data processing variables
        self.workspace = workspace
        self.vec_instances = None
        self.vec_cells = None
        self.vec_nets = None
        self.vec_patch = None
        self.vec_layers = None
        
        # UI components initialization
        self.chip_ui = None
        self.patches_ui = None
        self.patch_ui = None
        self.layer_ui = None
        self.net_ui = None
        self.widgets_grid = {}
        
        # Layout configuration
        self.left_width_ratio = 0.9  # 90% width for left side
        self.right_width_ratio = 0.1  # 10% width for right side
        self.main_layout = QGridLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Colors for different cell types in the layout
        self.color_list = self._generate_colors()
        
        # Status tracking for synchronization
        self._is_syncing = False  # Flag to prevent infinite recursion during synchronization
        
        # Initialize the UI and load data
        self.load_data()
        self.load_layout()
    
    def _init_ui(self):
        pass
        
    def _generate_colors(self):
        """Generate high contrast colors for different cell types"""
        color_list = {}
        
        # Use a combination of predefined high-contrast colors and algorithmically generated colors
        predefined_colors = [
            # Primary colors with high contrast
            (255, 0, 0, 255),   # Red
            (0, 255, 0, 255),   # Green
            (0, 0, 255, 255),   # Blue
            (255, 255, 0, 255), # Yellow
            (255, 0, 255, 255), # Magenta
            (0, 255, 255, 255), # Cyan
            # Secondary colors
            (255, 128, 0, 255), # Orange
            (128, 0, 255, 255), # Purple
            (0, 255, 128, 255), # Bright Green
            (255, 0, 128, 255), # Pink
            (128, 255, 0, 255), # Lime
            (0, 128, 255, 255), # Sky Blue
        ]
        
        # Add predefined high-contrast colors
        for idx, (r, g, b, a) in enumerate(predefined_colors):
            color_list[idx] = QColor(r, g, b, a)
        
        # Generate additional high-contrast colors with systematic hue distribution
        num_additional_colors = 200  # Total colors will be predefined + additional
        
        # Generate a spread of hue values that are evenly distributed around the color wheel
        for i in range(len(predefined_colors), num_additional_colors):
            # Use golden ratio for more visually balanced hue distribution
            hue = (i * 0.618033988749895) % 1.0  # Golden ratio conjugate
            
            # Vary saturation and value slightly to increase contrast
            saturation = 0.7 + 0.2 * ((i * 0.381966011250105) % 1.0)  # 0.7-0.9
            value = 0.8 + 0.15 * ((i * 0.2360679775) % 1.0)  # 0.8-0.95
            alpha = 0.9  # Keep high opacity for visibility
            
            color = QColor.fromHsvF(hue, saturation, value, alpha)
            color_list[i] = color
        
        # Add default color for unknown cell types
        color_list[None] = QColor(192, 192, 192, 200)  # Default gray
        
        return color_list
        
    def add_widget_to_grid(self, widget, row, col, rowspan=1, colspan=1, stretch=None):
        """Add a widget to the grid layout with specified position and size
        
        Args:
            widget: The QWidget to add
            row: Starting row index
            col: Starting column index
            rowspan: Number of rows the widget should occupy
            colspan: Number of columns the widget should occupy
            stretch: Tuple of (row_stretch, col_stretch) for resizing behavior
        """
        if widget is None:
            return
            
        # Add widget to grid layout
        self.main_layout.addWidget(widget, row, col, rowspan, colspan)
        
        # Store widget information for later reference
        self.widgets_grid[widget] = {
            'row': row,
            'col': col,
            'rowspan': rowspan,
            'colspan': colspan,
            "stretch" : stretch
        }
        
        # Set stretch factors if provided
        if stretch:
            row_stretch, col_stretch = stretch
            # Ensure row stretch factor is set
            while self.main_layout.rowStretch(row + rowspan - 1) < row_stretch:
                self.main_layout.setRowStretch(row + rowspan - 1, row_stretch)
            # Ensure column stretch factor is set
            while self.main_layout.columnStretch(col + colspan - 1) < col_stretch:
                self.main_layout.setColumnStretch(col + colspan - 1, col_stretch)
                
    def set_widget_position(self, widget, row, col, rowspan=1, colspan=1):
        """Set the position and size of an existing widget in the grid"""
        if widget not in self.widgets_grid:
            return
            
        # Remove widget from current position
        self.main_layout.removeWidget(widget)
        
        # Update widget information
        self.widgets_grid[widget] = {
            'row': row,
            'col': col,
            'rowspan': rowspan,
            'colspan': colspan
        }
        
        # Add widget back to grid at new position
        self.main_layout.addWidget(widget, row, col, rowspan, colspan)
        
    def load_data(self):
        from ..data import DataVectors
        data_loader = DataVectors(self.workspace)
        self.vec_instances = data_loader.load_instances()
        self.vec_cells = data_loader.load_cells()
        self.vec_nets = data_loader.load_nets()
        self.vec_patch = data_loader.load_patchs()
        self.vec_layers = data_loader.load_layers()

    def load_layout(self):
        """Load chip layout"""
        if not self.workspace:
            QMessageBox.warning(self, "Warning", "Please select a workspace first")
            return
        
        try:
            # Clear previous display
            for i in reversed(range(self.main_layout.count())):
                widget = self.main_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            # Clear widgets grid dictionary
            self.widgets_grid.clear()
            
            # Create UI components
            self.chip_ui = ChipLayout(self.vec_cells, self.vec_instances, self.vec_nets, self.color_list)   # Top-left
            self.patch_ui = PatchLayout(self.vec_layers, self.color_list) # Bottom-left
            self.patches_ui = PatchesLayout(self.vec_patch, self.color_list, self.patch_ui)   # Top-left
            self.layer_ui = LayerLayout(self.vec_layers, self.color_list, self.chip_ui, self.patches_ui) # Top-right
            self.net_ui = NetLayout(self.vec_nets)     # Bottom-right
            
            # 设置PatchesLayout的patch_layout引用为PatchLayout的实例
            self.patches_ui.patch_layout = self.patch_ui
            
            # Calculate width ratio: ChipLayout and PatchLayout (left side) should be 0.8 of WorkspaceUI width
            # Right side (LayerLayout and NetLayout) will be 0.2 of WorkspaceUI width
            
            # Set column stretch factors to control width proportions
            self.main_layout.setColumnStretch(0, int(self.left_width_ratio * 10))  # Left column (80% width)
            self.main_layout.setColumnStretch(1, int(self.right_width_ratio * 10)) # Right column (20% width)
            
            # Set row stretch factors to make top and bottom rows equal height
            self.main_layout.setRowStretch(0, 1)  # Top row
            self.main_layout.setRowStretch(1, 1)  # Bottom row
            
            # Create vertical layout for button_layout (top) and chip/patches (bottom)
            top_left_layout = QVBoxLayout()
            top_left_widget = QWidget()
            top_left_widget.setLayout(top_left_layout)
            
            # Create zoom buttons
            from PyQt5.QtWidgets import QHBoxLayout, QPushButton
            button_layout = QHBoxLayout()
            zoom_in_btn = QPushButton("Zoom In")
            zoom_out_btn = QPushButton("Zoom Out")
            fit_btn = QPushButton("Fit View")
            
            # Connect buttons to both chip_ui and patches_ui methods
            zoom_in_btn.clicked.connect(lambda: self._apply_to_both_views('zoom_in'))
            zoom_out_btn.clicked.connect(lambda: self._apply_to_both_views('zoom_out'))
            fit_btn.clicked.connect(lambda: self._apply_to_both_views('fit_view'))
            
            # Add buttons to layout
            button_layout.addWidget(zoom_in_btn)
            button_layout.addWidget(zoom_out_btn)
            button_layout.addWidget(fit_btn)
            button_layout.addStretch()  # Add stretch to push buttons to top
            
            # Create horizontal layout for chip_ui and patches_ui
            chips_patches_layout = QHBoxLayout()
            chips_patches_layout.addWidget(self.chip_ui)
            chips_patches_layout.addWidget(self.patches_ui)
            
            # Make chip_ui and patches_ui each take half of the view
            chips_patches_layout.setStretch(0, 1)  # chip_ui takes 1 part
            chips_patches_layout.setStretch(1, 1)  # patches_ui takes 1 part
            
            # Add button_layout (top) and chips_patches_layout (bottom) to top_left_layout
            top_left_layout.addLayout(button_layout)
            top_left_layout.addLayout(chips_patches_layout)
            
            # Install event filters for synchronized zooming
            self._setup_synchronized_zooming()
            
            # Add widgets to grid layout according to the specified arrangement:
            # - top_left_widget (chip_ui and patches_ui horizontally arranged): top-left (row 0, column 0)
            # - PatchLayout: bottom-left (row 1, column 0)
            # - LayerLayout: top-right (row 0, column 1)
            # - NetLayout: bottom-right (row 1, column 1)
            self.add_widget_to_grid(top_left_widget, 0, 0, 1, 1, (1, int(self.left_width_ratio * 10)))
            self.add_widget_to_grid(self.patch_ui, 1, 0, 1, 1, (1, int(self.left_width_ratio * 10)))
            self.add_widget_to_grid(self.layer_ui, 0, 1, 1, 1, (1, int(self.right_width_ratio * 10)))
            self.add_widget_to_grid(self.net_ui, 1, 1, 1, 1, (1, int(self.right_width_ratio * 10)))
            
            # 连接NetLayout的net_selected信号到ChipLayout和PatchesLayout的槽函数
            self.net_ui.net_selected.connect(self.chip_ui.on_net_selected)
            self.net_ui.net_selected.connect(self.patches_ui.on_net_selected)
            
            # The resizeEvent method is already implemented in the class

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load chip layout:\n{str(e)}")
            
            # Add error message to display area
            error_label = QLabel(f"Loading failed: {str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: red;")
            self.main_layout.addWidget(error_label)
    
    def _apply_to_both_views(self, method_name):
        """Apply a method to both chip_ui and patches_ui views"""
        # Get the method from both chip_ui and patches_ui
        if hasattr(self.chip_ui, method_name):
            getattr(self.chip_ui, method_name)()
        if hasattr(self.patches_ui, method_name):
            getattr(self.patches_ui, method_name)()
    
    def _setup_synchronized_zooming(self):
        """Setup synchronized zooming, scrolling and dragging between chip_ui and patches_ui"""
        # Install event filters to capture wheel events
        self.chip_ui.view.viewport().installEventFilter(self)
        self.patches_ui.view.viewport().installEventFilter(self)
        
        # Connect scroll bars for synchronized scrolling
        # Vertical scroll bars
        self.chip_ui.view.verticalScrollBar().valueChanged.connect(
            lambda value: self._sync_scroll_bar(self.chip_ui.view.verticalScrollBar(), 
                                              self.patches_ui.view.verticalScrollBar(), value))
        self.patches_ui.view.verticalScrollBar().valueChanged.connect(
            lambda value: self._sync_scroll_bar(self.patches_ui.view.verticalScrollBar(), 
                                              self.chip_ui.view.verticalScrollBar(), value))
        
        # Horizontal scroll bars
        self.chip_ui.view.horizontalScrollBar().valueChanged.connect(
            lambda value: self._sync_scroll_bar(self.chip_ui.view.horizontalScrollBar(), 
                                              self.patches_ui.view.horizontalScrollBar(), value))
        self.patches_ui.view.horizontalScrollBar().valueChanged.connect(
            lambda value: self._sync_scroll_bar(self.patches_ui.view.horizontalScrollBar(), 
                                              self.chip_ui.view.horizontalScrollBar(), value))
    

        
    def _sync_scroll_bar(self, source_bar, target_bar, value):
        """Synchronize scroll bar values between views to ensure both views display the same area"""
        # Prevent infinite recursion by checking if we're already in the middle of a sync operation
        if self._is_syncing:
            return
        
        try:
            # Set the syncing flag
            self._is_syncing = True
            
            # Calculate the proportionate value based on the maximum scroll range of each bar
            # This ensures that the visible area stays in sync even if the views have different sizes
            if source_bar.maximum() > 0 and target_bar.maximum() > 0:
                # Calculate the ratio of the current position to the maximum range
                ratio = value / source_bar.maximum()
                # Set the target bar's position based on this ratio
                target_value = int(ratio * target_bar.maximum())
            else:
                # If one of the bars has no range, just use the raw value
                target_value = value
                
            # Only set value if it's not already approximately the same (prevents unnecessary updates)
            if abs(target_bar.value() - target_value) > 1:
                # Block signals temporarily to prevent infinite recursion
                target_bar.blockSignals(True)
                target_bar.setValue(target_value)
                target_bar.blockSignals(False)
                
                # Get the view associated with the target scroll bar
                target_view = None
                if target_bar == self.chip_ui.view.verticalScrollBar() or target_bar == self.chip_ui.view.horizontalScrollBar():
                    target_view = self.chip_ui.view
                elif target_bar == self.patches_ui.view.verticalScrollBar() or target_bar == self.patches_ui.view.horizontalScrollBar():
                    target_view = self.patches_ui.view
                
                # Explicitly update the view to ensure it displays the new scroll position
                if target_view:
                    # Get the center point of the source view
                    if source_bar == self.chip_ui.view.verticalScrollBar() or source_bar == self.chip_ui.view.horizontalScrollBar():
                        source_view = self.chip_ui.view
                    else:
                        source_view = self.patches_ui.view
                    
                    # Calculate the source view's center in scene coordinates
                    source_center = source_view.mapToScene(source_view.viewport().rect().center())
                    
                    # Set the target view's center to match the source view's center
                    # We don't need to block signals here because we have the _is_syncing flag
                    target_view.centerOn(source_center)
                    
                    # Force an update to ensure the view redraws with the new position
                    target_view.update()
        finally:
            # Always clear the syncing flag, even if an exception occurs
            self._is_syncing = False
            
    def eventFilter(self, source, event):
        """Filter and handle events for synchronized zooming, scrolling and dragging"""
        chip_viewport = self.chip_ui.view.viewport()
        patches_viewport = self.patches_ui.view.viewport()
        
        # Check if it's a wheel event
        if event.type() == event.Wheel:
            # Determine which view triggered the event
            if source == chip_viewport:
                scene_pos = self.chip_ui.view.mapToScene(event.pos())
                target_view = self.patches_ui.view
                source_view = self.chip_ui.view
            elif source == patches_viewport:
                scene_pos = self.patches_ui.view.mapToScene(event.pos())
                target_view = self.chip_ui.view
                source_view = self.patches_ui.view
            else:
                return super().eventFilter(source, event)
            
            # Check if Ctrl key is pressed for zooming (match the implementation in ZoomableGraphicsView)
            if (event.modifiers() & Qt.ControlModifier):  # Use bitwise AND to check for Ctrl key
                # Handle synchronized zooming (Ctrl + wheel)
                # Calculate zoom factor (match the zoom factors in ZoomableGraphicsView)
                zoom_factor = 1.2 if event.angleDelta().y() > 0 else 0.8
                
                # Save the current transformation anchor
                original_anchor = target_view.transformationAnchor()
                
                # Set anchor to be under the mouse position in the target view
                target_view.setTransformationAnchor(target_view.AnchorUnderMouse)
                target_view.centerOn(scene_pos)
                
                # Apply zoom to the target view
                target_view.scale(zoom_factor, zoom_factor)
                
                # Restore the original transformation anchor
                target_view.setTransformationAnchor(original_anchor)
            else:
                # Handle synchronized scrolling (wheel without Ctrl)
                # Calculate scroll delta
                delta = event.angleDelta().y()
                scroll_steps = delta / 120  # Convert to scroll steps
                
                # Scroll the target view
                target_view.verticalScrollBar().setValue(
                    int(target_view.verticalScrollBar().value() - scroll_steps * 15)
                )
            
            # Allow the original event to proceed normally for the source view
            return super().eventFilter(source, event)
        
        # Check if it's a mouse move event for synchronized dragging
        elif event.type() == event.MouseMove and (event.buttons() == Qt.LeftButton):
            # Only process if the view is in ScrollHandDrag mode
            if source == chip_viewport and self.chip_ui.view.dragMode() == QGraphicsView.ScrollHandDrag:
                scene_pos = self.chip_ui.view.mapToScene(event.pos())
                target_view = self.patches_ui.view
                source_view = self.chip_ui.view
            elif source == patches_viewport and self.patches_ui.view.dragMode() == QGraphicsView.ScrollHandDrag:
                scene_pos = self.patches_ui.view.mapToScene(event.pos())
                target_view = self.chip_ui.view
                source_view = self.patches_ui.view
            else:
                return super().eventFilter(source, event)
            
            # For dragging synchronization, directly set the target view's center to match the source view's center
            # This ensures both views show the same scene area
            source_center = source_view.mapToScene(source_view.viewport().rect().center())
            target_view.centerOn(source_center)
            
            # Allow the original event to proceed normally for the source view
            return super().eventFilter(source, event)
        
        # For other event types, use the default handling
        return super().eventFilter(source, event)
    
    def resizeEvent(self, event):
        """Handle resize event to maintain width ratio"""
        # Call the base class resize event
        super().resizeEvent(event)
   
        # Update column stretch factors to maintain width ratio
        self.main_layout.setColumnStretch(0, int(self.left_width_ratio * 10))
        self.main_layout.setColumnStretch(1, int(self.right_width_ratio * 10))
        
        # Force layout update
        self.updateGeometry()