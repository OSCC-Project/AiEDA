#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QGraphicsScene, QGraphicsView, QHBoxLayout, QVBoxLayout, 
    QGraphicsRectItem, QGraphicsLineItem, QLabel, QGraphicsItem
)
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QThreadPool, QRunnable, QObject

from .basic import ZoomableGraphicsView

class WorkerSignals(QObject):
    """Define signals for worker threads"""
    patches_data = pyqtSignal(list)
    wires_data = pyqtSignal(dict)

class PatchesWorker(QRunnable):
    """Worker thread for creating patch data - does not create GUI elements"""
    def __init__(self, patches):
        super().__init__()
        self.patches = patches
        self.signals = WorkerSignals()
        
    def run(self):
        result_data = []
        for id, patch in self.patches.items():
            # 收集patch数据
            patch_data = {
                'id': id,
                'llx': patch.llx,
                'lly': patch.lly,
                'width': patch.urx - patch.llx,
                'height': patch.ury - patch.lly
            }
            
            result_data.append(patch_data)
        
        # 发送完成信号，传递收集的数据列表
        self.signals.patches_data.emit(result_data)

class WiresWorker(QRunnable):
    """Worker thread for creating wire data - does not create GUI elements"""
    def __init__(self, patches, color_list, layer_visibility=None):
        super().__init__()
        self.patches = patches
        self.color_list = color_list
        self.layer_visibility = layer_visibility
        self.signals = WorkerSignals()
        
    def run(self):
        result_data = {}
        
        for _, patch in self.patches.items():
            for layer in patch.patch_layer:
                # 检查layer是否有id属性
                if hasattr(layer, 'id'):
                    layer_id = layer.id
                else:
                    layer_id = None
                
                for net in layer.nets:
                    for wire in net.wires:
                        for path in wire.paths:
                            if path.node1.layer == path.node2.layer or path.node1.layer > path.node2.layer:
                                color_id = path.node1.layer % len(self.color_list)
                                color = self.color_list[color_id]
                            else:
                                color_id = path.node2.layer % len(self.color_list)
                                color = self.color_list[color_id]
                                
                            path_data = {
                                'x1': path.node1.x,
                                'y1': path.node1.y,
                                'x2': path.node2.x,
                                'y2': path.node2.y,
                                'color': color,
                                'layer_id': layer_id
                            }
                            
                            # 初始化该层的列表（如果不存在）
                            if layer_id not in result_data:
                                result_data[layer_id] = []
                            
                            result_data[layer_id].append(path_data)
        
        # 发送完成信号，传递创建的数据字典
        self.signals.wires_data.emit(result_data)

class HighlightableRectItem(QGraphicsRectItem):
    """Highlightable rectangle item that supports mouse hover and double-click events
    
    This class extends QGraphicsRectItem to provide additional interactivity features,
    including highlighting on mouse hover and custom double-click event handling.
    
    Attributes:
        rect_id: Unique identifier for the rectangle
        original_pen: Original pen style to restore after highlighting
    """
    
    def __init__(self, rect_id, *args, **kwargs):
        """Initialize the HighlightableRectItem with a unique identifier
        
        Args:
            rect_id: Unique identifier for the rectangle
            *args: Additional positional arguments for QGraphicsRectItem
            **kwargs: Additional keyword arguments for QGraphicsRectItem
        """
        super().__init__(*args, **kwargs)
        self.rect_id = int(rect_id)  # Store rectangle ID
        self.original_pen = self.pen()  # Save original pen style
        self.setAcceptHoverEvents(True)  # Enable hover events
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)  # Enable selection
    
    def hoverEnterEvent(self, event):
        """Handle mouse hover enter event by highlighting the rectangle
        
        Args:
            event: QGraphicsSceneHoverEvent containing hover information
        """
        # Create highlight style pen
        highlight_pen = QPen(QColor(0, 255, 0), 50)  # Green thick border
        highlight_pen.setStyle(Qt.DashLine)
        self.setPen(highlight_pen)
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Handle mouse hover leave event by restoring original style
        
        Args:
            event: QGraphicsSceneHoverEvent containing hover information
        """
        self.setPen(self.original_pen)
        super().hoverLeaveEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """Handle double-click event using traditional method since QGraphicsRectItem doesn't inherit QObject
        
        Args:
            event: QGraphicsSceneMouseEvent containing click information
        """
        if event.button() == Qt.LeftButton:
            # Find parent widget
            parent_widget = self.scene().views()[0].parent()
            if hasattr(parent_widget, 'on_rect_double_clicked'):
                parent_widget.on_rect_double_clicked(self.rect_id)
        super().mouseDoubleClickEvent(event)

class PatchesLayout(QWidget):
    """Patch Layout UI component for AiEDA system
    
    This widget provides a comprehensive interface for visualizing integrated circuit patches,
    including interactive features like zooming, panning, and highlighting of selected elements.
    
    Attributes:
        patches: Dictionary mapping patch IDs to patch objects
        color_list: List of colors used for rendering different elements
        rect_items: Dictionary mapping patch IDs to their graphical rectangle items
        overlapping_rects: Dictionary storing overlapping rectangle borders
        patch_layout: Reference to PatchLayout component set in WorkspaceUI
        selected_net_rect: Rectangle item highlighting the selected network
        scene: QGraphicsScene for rendering patches
        view: Custom ZoomableGraphicsView for displaying the scene
        status_bar: Status bar widget at the bottom of the window
        coord_label: Label displaying coordinate information
        layer_items: Dictionary mapping layer IDs to lists of graphics items for those layers
        thread_pool: Qt线程池，用于并行处理
    """
    
    def __init__(self, vec_patches, color_list, patch_layout=None):
        """Initialize the PatchesLayout component
        
        Args:
            vec_patches: Vector of patch objects
            color_list: List of colors for rendering
            patch_layout: Optional reference to PatchLayout component
        """
        self.patches = self.load_patches(vec_patches)
        self.color_list = color_list
        self.rect_items = {}
        self.overlapping_rects = {}  # Store overlapping rectangle borders
        self.patch_layout = patch_layout  # Will be set in WorkspaceUI
        self.selected_net_rect = None
        
        # Dictionary to store graphics items by layer ID for efficient visibility management
        self.layer_items = {}
        
        # Initialize thread pool
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(4)  # Set maximum thread count
        
        super().__init__()
        
        self._init_ui()
        self.draw_layout(True)
    
    def load_patches(self, vec_patches):
        """Load patches data and convert to dictionary format
        
        Args:
            vec_patches: Vector of patch objects
            
        Returns:
            Dictionary mapping patch IDs to patch objects
        """
        patches = {patch.id: patch for patch in vec_patches} if vec_patches else {}
        return patches

    def _init_ui(self):
        """Initialize UI components and layout"""
        main_layout = QVBoxLayout(self)
        
        # Create QGraphicsScene and custom ZoomableGraphicsView
        self.scene = QGraphicsScene()
        self.view = ZoomableGraphicsView(self.scene, self)  # Pass self as parent
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        
        # Add view to main layout
        main_layout.addWidget(self.view)
        
        # Create status bar at the bottom
        self.status_bar = QWidget()
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(5, 2, 5, 2)
        
        # Left empty space for future status messages
        status_layout.addStretch(1)
        
        # Right side coordinate display
        self.coord_label = QLabel("X: 0.00, Y: 0.00")
        self.coord_label.setStyleSheet("background-color: #f0f0f0; padding: 2px 5px;")
        self.coord_label.setMinimumWidth(150)
        self.coord_label.setAlignment(Qt.AlignRight)
        status_layout.addWidget(self.coord_label)
        
        # Add status bar to main layout
        main_layout.addWidget(self.status_bar)
        
        self.setLayout(main_layout)
        self.setWindowTitle("Patches Display")
        self.resize(1000, 800)
        
    def zoom_in(self):
        """Zoom in on the view, centered at mouse position in scene coordinates"""
        # Scale the view
        self.view.scale(1.2, 1.2)
    
    def zoom_out(self):
        """Zoom out from the view, centered at mouse position in scene coordinates"""
        # Scale the view
        self.view.scale(0.8, 0.8)
    
    def fit_view(self):
        """Fit the view to the entire scene"""
        if not self.scene.items():
            return
        
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        
    def resizeEvent(self, event):
        """Handle resize event to maintain view fitting
        
        Args:
            event: QResizeEvent containing resize information
        """
        # Call the base class resize event
        super().resizeEvent(event)
        
        # Force view to fit scene
        self.fit_view()
        
    def draw_layout(self, fit_view=False):
        """Draw the patches layout in the scene
        
        Args:
            fit_view: Whether to fit the view to the entire scene after drawing
        """
        self.scene.clear()
        self.rect_items = {}  # Clear rectangle items list
        self.overlapping_rects = {}  # Clear overlapping rectangles dictionary
        self.layer_items = {}  # Reset layer items dictionary
        
        # Add task counter and flag to track parallel task completion
        self._pending_tasks = 0
        self._should_fit_view = fit_view
        
        # 使用线程池并行处理数据
        if self.patches:
            self._pending_tasks += 2  # 增加任务计数: patches和wires
            self._draw_patches_parallel()
            self._draw_wires_parallel()
        
        # 如果没有待处理任务但仍需适应视图
        if self._pending_tasks == 0 and self._should_fit_view:
            self.fit_view()
    
    def _task_completed(self):
        """Mark a task as completed and check if all tasks are finished"""
        self._pending_tasks -= 1
        if self._pending_tasks == 0 and self._should_fit_view:
            self.fit_view()
            
    def _draw_patches_parallel(self):
        """Process patch data in parallel"""
        worker = PatchesWorker(self.patches)
        worker.signals.patches_data.connect(self._on_patches_data)
        self.thread_pool.start(worker)
    
    def _on_patches_data(self, patches_data):
        """Callback for completed patch data processing - creates GUI elements in main thread"""
        for patch_info in patches_data:
            # 在主线程中创建矩形项
            rect_item = HighlightableRectItem(str(patch_info['id']), 
                                          patch_info['llx'], 
                                          patch_info['lly'], 
                                          patch_info['width'], 
                                          patch_info['height'])
                        
            # Set border to dashed line
            pen = QPen(QColor(0, 0, 0), 5.0)
            pen.setStyle(Qt.DashLine)
            rect_item.setPen(pen)
            self.scene.addItem(rect_item)
            self.rect_items[patch_info['id']] = rect_item # Store rectangle item
        
        # Mark task as completed
        self._task_completed()
        
    def _draw_wires_parallel(self):
        """Process wire data in parallel"""
        layer_visibility = getattr(self, 'layer_visibility', None)
        worker = WiresWorker(self.patches, self.color_list, layer_visibility)
        worker.signals.wires_data.connect(self._on_wires_data)
        self.thread_pool.start(worker)
    
    def _on_wires_data(self, wires_data):
        """Callback for completed wire data processing - creates GUI elements in main thread"""
        # Store layer items and add to scene based on visibility
        for layer_id, items_data in wires_data.items():
            if layer_id not in self.layer_items:
                self.layer_items[layer_id] = []
                
            # 根据数据创建GUI元素
            for item_data in items_data:
                wire_pen = QPen(item_data['color'], 30)
                line_item = QGraphicsLineItem(
                    item_data['x1'], item_data['y1'],
                    item_data['x2'], item_data['y2']
                )
                line_item.setPen(wire_pen)
                self.layer_items[layer_id].append(line_item)
            
            # 添加到场景
            should_add_to_scene = True
            if hasattr(self, 'layer_visibility') and layer_id is not None and layer_id in self.layer_visibility:
                should_add_to_scene = self.layer_visibility[layer_id]
                
            if should_add_to_scene:
                for item in self.layer_items[layer_id]:
                    self.scene.addItem(item)
        
        # Mark task as completed
        self._task_completed()
        
    def update_coord_status(self, coord_text):
        """Update the coordinate status display in the bottom status bar
        
        Args:
            coord_text: Text to display in the coordinate label
        """
        self.coord_label.setText(coord_text)
        
    def on_rect_double_clicked(self, rect_id):
        """Handle rectangle double-click event, display rectangle ID and pass selected patch to PatchLayout
        
        Args:
            rect_id: ID of the double-clicked rectangle
        """
        # Display rectangle ID in status bar
        current_text = self.coord_label.text()
        self.coord_label.setText(f"ID: {rect_id} | {current_text}")
        
        # Determine rect_id type and convert to number
        try:
            # If rect_id is string, try to convert to number
            if isinstance(rect_id, str):
                rect_id_key = int(rect_id)
            else:
                rect_id_key = rect_id
        except ValueError:
            # If conversion fails, use original rect_id
            rect_id_key = rect_id
        
        # Get selected patch
        selected_patch = self.patches.get(rect_id_key, None)
        
        # If patch_layout reference is set, pass the selected patch
        if self.patch_layout is not None and selected_patch is not None:
            self.patch_layout.update_patch(selected_patch)
        
        # Create table with all VectorPatch data except patch_layer and display in self.text_display from info.py
        if selected_patch is not None and hasattr(self.patch_layout, 'info') and self.patch_layout.info is not None:
            info_str = []
            
            # Add title
            info_str += self.patch_layout.info.make_title(f"Patch information : ID-{rect_id_key}")
            info_str += self.patch_layout.info.make_line_space()
            
            # Prepare table data
            headers = ["Feature", "Value"]
            values = []
            
            # Add all VectorPatch attributes except patch_layer
            # Required attributes
            if hasattr(selected_patch, 'id'):
                values.append(("ID", selected_patch.id))
            if hasattr(selected_patch, 'patch_id_row'):
                values.append(("Row ID", selected_patch.patch_id_row))
            if hasattr(selected_patch, 'patch_id_col'):
                values.append(("Column ID", selected_patch.patch_id_col))
            if hasattr(selected_patch, 'llx'):
                values.append(("llx", selected_patch.llx))
            if hasattr(selected_patch, 'lly'):
                values.append(("lly", selected_patch.lly))
            if hasattr(selected_patch, 'urx'):
                values.append(("urx", selected_patch.urx))
            if hasattr(selected_patch, 'ury'):
                values.append(("ury", selected_patch.ury))
            if hasattr(selected_patch, 'row_min'):
                values.append(("Row min", selected_patch.row_min))
            if hasattr(selected_patch, 'row_max'):
                values.append(("Row max", selected_patch.row_max))
            if hasattr(selected_patch, 'col_min'):
                values.append(("Column min", selected_patch.col_min))
            if hasattr(selected_patch, 'col_max'):
                values.append(("Column max", selected_patch.col_max))
            
            # Calculate width and height
            if all(hasattr(selected_patch, attr) for attr in ['llx', 'urx']):
                width = selected_patch.urx - selected_patch.llx
                values.append(("width", width))
            if all(hasattr(selected_patch, attr) for attr in ['lly', 'ury']):
                height = selected_patch.ury - selected_patch.lly
                values.append(("height", height))
            
            # Add patch_layer information
            if hasattr(selected_patch, 'patch_layer'):
                values.append(("Layer count", len(selected_patch.patch_layer)))
            
            # Add all other VectorPatch attributes
            vector_patch_attrs = ['cell_density', 'pin_density', 'net_density', 'macro_margin', 
                                 'RUDY_congestion', 'EGR_congestion', 'timing_map', 'power_map', 'ir_drop_map']
            for attr_name in vector_patch_attrs:
                if hasattr(selected_patch, attr_name):
                    attr_value = getattr(selected_patch, attr_name)
                    # Format with proper labels
                    label_map = {
                        'cell_density': 'Cell density',
                        'pin_density': 'Pin density',
                        'net_density': 'Net density',
                        'macro_margin': 'Macro margin',
                        'RUDY_congestion': 'RUDY congestion',
                        'EGR_congestion': 'EGR congestion',
                        'timing_map': 'Timing map',
                        'power_map': 'Power map',
                        'ir_drop_map': 'IR drop map'
                    }
                    display_label = label_map.get(attr_name, attr_name)
                    values.append((display_label, attr_value))
            
            # Create table and set HTML
            info_str += self.patch_layout.info.make_table(headers, values)
            self.patch_layout.info.make_html(info_str)

    
    def on_net_selected(self, selected_net):
        """Handle network selection slot function, draw bounding rectangle and adjust view
        
        Args:
            selected_net: The network object that was selected
        """
        # Remove previous overlapping rectangle borders
        for id, rect in self.overlapping_rects.items():
            if rect in self.scene.items():
                self.scene.removeItem(rect)
        self.overlapping_rects = {}
        
        # Check if selected network has feature attribute
        if hasattr(selected_net, 'feature') and selected_net.feature:
            feature = selected_net.feature
            
            # Check if feature has llx, lly, width, height attributes
            if all(hasattr(feature, attr) for attr in ['llx', 'lly', 'width', 'height']):
                if self.selected_net_rect is not None:
                    self.selected_net_rect.setRect(feature.llx-100, feature.lly-100, feature.width+200, feature.height+200)
                else:
                    # Create rectangle with white border
                    pen = QPen(QColor(200, 0, 0), 40)
                    pen.setStyle(Qt.DashLine)
                    
                    # Create rectangle item
                    self.selected_net_rect = QGraphicsRectItem(
                        feature.llx-100, feature.lly-100, feature.width+200, feature.height+200
                    )
                    
                    # Set rectangle style
                    self.selected_net_rect.setPen(pen)
                    self.selected_net_rect.setBrush(QBrush(Qt.NoBrush))  # No border fill
                    
                    # Add rectangle to scene
                    self.scene.addItem(self.selected_net_rect)
                    
                    # Move rectangle to top layer to ensure visibility
                    self.selected_net_rect.setZValue(100)  # Set high z-value
                
                # Detect and display patch rectangles overlapping with selected network rectangle
                self._show_overlapping_rects()
                
                # Auto-fit view to show entire selected network rectangle
                self.view.fitInView(self.selected_net_rect, Qt.KeepAspectRatio)
                # Slightly zoom out to leave some space around the selected rectangle
                self.view.scale(0.6, 0.6)
                
    def _show_overlapping_rects(self):
        """Show patch rectangle borders that overlap with the selected network rectangle"""
        if not hasattr(self, 'selected_net_rect') or self.selected_net_rect is None:
            return
        
        # Get selected network rectangle bounds
        selected_rect = self.selected_net_rect.rect()
        
        # Iterate through all patch rectangles and check for overlap
        for id, rect_item in self.rect_items.items():
            # Get current rectangle bounds
            patch_rect = rect_item.rect()
            
            # Check if the two rectangles overlap
            if selected_rect.intersects(patch_rect):
                # Create white dashed border rectangle
                white_pen = QPen(QColor(200, 0, 0), 20)
                white_pen.setStyle(Qt.DashLine)
                
                # Create rectangle item
                overlapping_rect = QGraphicsRectItem(
                    patch_rect.x(), patch_rect.y(), patch_rect.width(), patch_rect.height()
                )
                
                # Set rectangle style
                overlapping_rect.setPen(white_pen)
                # Set transparent red background (R=255, G=0, B=0, Alpha=50)
                overlapping_rect.setBrush(QBrush(QColor(50, 50, 50, 50)))
                
                # Add rectangle to scene
                self.scene.addItem(overlapping_rect)
                
                # Move rectangle to top layer to ensure visibility
                overlapping_rect.setZValue(0)  # One less than selected network rectangle to avoid遮挡
                
                # Store overlapping rectangle for later removal
                self.overlapping_rects[id] = overlapping_rect
    
    def update_layer_visibility(self):
        """Update the visibility of items based on the current layer_visibility settings
        
        This method is more efficient than redrawing the entire layout as it only
        shows or hides existing items rather than recreating them.
        """
        if not hasattr(self, 'layer_visibility'):
            return
        
        # Update visibility for all layer items
        for layer_id, items in self.layer_items.items():
            # Check if this layer's visibility is controlled
            if layer_id in self.layer_visibility:
                is_visible = self.layer_visibility[layer_id]
                
                for item in items:
                    # Check if item is already in the scene
                    is_in_scene = item.scene() is not None
                    
                    if is_visible and not is_in_scene:
                        # Add to scene if layer is visible and not already in scene
                        self.scene.addItem(item)
                    elif not is_visible and is_in_scene:
                        # Remove from scene if layer is hidden and in scene
                        self.scene.removeItem(item)
        
        