# -*- encoding: utf-8 -*-
"""
@File : workspaces.py
@Author : yell
@Desc : Workspaces UI for AiEDA system
"""

import sys
import os

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                             QMessageBox, QGroupBox, QGridLayout, QCheckBox, 
                             QMenuBar, QMenu, QAction, QListWidget,QListWidgetItem)

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt

from aieda.gui.chip import ChipLayout
from aieda.gui.workspace import WorkspaceUI
from aieda.workspace import Workspace


class WorkspacesUI(QMainWindow):
    """Main application window"""
    
    def __init__(self, workspace=None):
        super().__init__()
        self.main_layout = None
        self.workspace_ui = None
        self.workspace_list = None
        
        self.init_ui()
        
        self.load_workspace(workspace)
        
    def init_ui(self):
        self.init_main()
        self.init_menu()  # Add menu initialization
        self.init_workspace_list()
        self.init_content_area()
        
    def init_main(self):
        self.setWindowTitle("AiEDA Workspaces Viewer")
        self.setGeometry(100, 100, 1200, 900)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Use QGridLayout as main layout to support both horizontal and vertical arrangement
        # and allow setting position and size for each widget
        self.main_layout = QGridLayout(central_widget)
        
        # Dictionary to store widgets and their positions for easy management
        self.widgets_grid = {}
    
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
            'colspan': colspan
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
        
    def init_workspace_list(self):
        # Initialize workspace_list and add to main layout
        self.workspace_list = self.WorkspaceListUI()
        # Add workspace list to grid layout at position (0, 0), spanning 1 row and 1 column
        # Set column stretch to 1 (for 0.1 of width)
        self.add_widget_to_grid(self.workspace_list, 0, 0, 1, 1, (1, 1))
        
        # Set column stretch factors to control width proportion
        # Workspace list (column 0) should be 0.1 of total width
        # Content area (column 1) should be 0.9 of total width
        self.main_layout.setColumnStretch(0, 1)  # 1 part for workspace list
        self.main_layout.setColumnStretch(1, 9)  # 9 parts for content area (total 10 parts)
        
    def init_content_area(self):
        # Create content area container and vertical layout
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        
        # Initialize notice label
        self.init_lad_notice()
        
        # Add content area to main layout at position (0, 1), spanning 1 row and 2 columns
        # Set column stretch to 9 (for 0.9 of width)
        self.add_widget_to_grid(self.content_widget, 0, 1, 1, 2, (1, 9))
        
        # Override resize event to maintain width ratio
        self.resizeEvent = self._on_resize
        
    def create_multi_widget_layout(self):
        """Create a layout with multiple widgets arranged in a grid pattern
        This example creates a 2x3 grid for 6 widgets"""
        # Clear all existing widgets from main layout
        for i in reversed(range(self.main_layout.count())):
            item = self.main_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
        
        # Clear widgets grid dictionary
        self.widgets_grid.clear()
        
        # Create 6 example widgets (in a real application, these would be your actual widgets)
        widgets = []
        for i in range(6):
            widget = QWidget()
            widget.setStyleSheet(f"background-color: rgb({100 + i*25}, {150 - i*10}, {200});")
            layout = QVBoxLayout(widget)
            label = QLabel(f"Widget {i+1}")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
            widgets.append(widget)
        
        # Add widgets to grid in a 2x3 pattern
        positions = [(0, 0), (0, 1), (0, 2),  # First row
                     (1, 0), (1, 1), (1, 2)]  # Second row
        
        # Set column and row stretch factors for proportional resizing
        for i in range(3):
            self.main_layout.setColumnStretch(i, 1)  # Equal width for all columns
        for i in range(2):
            self.main_layout.setRowStretch(i, 1)     # Equal height for all rows
        
        # Add widgets to grid with specified positions
        for i, (row, col) in enumerate(positions):
            self.add_widget_to_grid(widgets[i], row, col)
            
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
        
    def init_lad_notice(self):
        # First, clear any existing notice labels in the content area
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget and isinstance(widget, QLabel) and widget.styleSheet() == "color: blue;":
                widget.deleteLater()
                break
                
        # Add new notice label
        notice_label = QLabel(f"Please load a workspace.")
        notice_label.setAlignment(Qt.AlignCenter)
        notice_label.setStyleSheet("color: blue;")
        self.content_layout.addWidget(notice_label)
        
    def init_menu(self):
        """Initialize the menu bar"""
        # Create menu bar
        menubar = self.menuBar()
        
        # Create File menu
        file_menu = menubar.addMenu('File')
        
        # Create Load Workspace action
        load_workspace_action = QAction('Load Workspace', self)
        load_workspace_action.triggered.connect(self.load_workspace_dialog)
        file_menu.addAction(load_workspace_action)
        
    def load_workspace_dialog(self):
        """Open file dialog to select workspace directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Workspace Directory", "./")
        if directory:
            try:
                workspace = Workspace(directory)
                self.load_workspace(workspace)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load workspace: {str(e)}")
        
    def load_workspace(self, workspace):
        if workspace is None:
            return 
        
        """Load and display the selected workspace"""

        self.statusBar().showMessage(f"design:{workspace.design}, workspace:{workspace.directory}")
        
        # Add workspace to workspace_list
        if self.workspace_list:
            self.workspace_list.add_workspace(workspace)
        
        # Clear all existing widgets in the content area
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Create and add workspace UI to content area
        try:
            self.workspace_ui = WorkspaceUI(workspace)
            self.content_layout.addWidget(self.workspace_ui, 1)
        except Exception as e:
            error_label = QLabel(f"Failed to create workspace UI: {str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: red;")
            self.content_layout.addWidget(error_label)
            QMessageBox.critical(self, "Error", f"Failed to create workspace UI:\n{str(e)}")
            
    def _on_resize(self, event):
        """Handle resize event to maintain width ratio"""
        # Call the base class resize event
        super().resizeEvent(event)
        
        # Maintain column stretch factors to ensure workspace list is 0.1 of window width
        self.main_layout.setColumnStretch(0, 1)  # 1 part for workspace list
        self.main_layout.setColumnStretch(1, 9)  # 9 parts for content area
        
        # Force layout update
        self.updateGeometry()
            
    class WorkspaceListUI(QWidget):
        def __init__(self):
            super().__init__()
            
            self.workspaces = {}
            self.list_widget = None
            self.init_ui()
            
        def init_ui(self):
            # Create layout
            layout = QVBoxLayout(self)
            
            title_label = QLabel("Workspaces List")
            title_label.setAlignment(Qt.AlignCenter)
            font = QFont()
            font.setBold(True)
            title_label.setFont(font)
            layout.addWidget(title_label)
            
            # Create list widget
            self.list_widget = QListWidget()
            self.list_widget.setMinimumWidth(250)
            layout.addWidget(self.list_widget)
            
        def add_workspace(self, workspace):
            self.workspaces[workspace.design] = workspace
            self.update_ui()  # Automatically update UI after adding
            
        def update_ui(self):
            # Clear the list
            self.list_widget.clear()
            
            # Create font with bold style and larger size
            font = QFont()
            font.setBold(True)
            font.setPointSize(11)  # Slightly larger font size
            
            # Convert all workspace keys to a list and add to the list widget
            for design_name in list(self.workspaces.keys()):
                item = QListWidgetItem(design_name)
                item.setFont(font)  # Set bold and larger font
                item.setTextAlignment(Qt.AlignCenter)  # Center-align text
                self.list_widget.addItem(item)
            
            # Set appropriate height for the list widget
            # Adjust the height based on the number of items
            # item_height = 30  # Slightly larger item height
            # total_height = min(len(self.workspaces) * item_height + 10, 400)  # Maximum height 400px
            # self.list_widget.setMinimumHeight(total_height)
            # self.list_widget.setMaximumHeight(total_height)
            
            # Add double-click event handler to load the corresponding workspace when clicking on a list item
            self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
          
        def on_item_double_clicked(self, item):
            # Get the clicked workspace name
            design_name = item.text()
            # Get the corresponding workspace object from the dictionary
            if design_name in self.workspaces:
                workspace = self.workspaces[design_name]
                # Can add callback function or signal to notify parent window to load this workspace
                # Simple implementation here: load through parent window's load_workspace method
                parent_window = self.window()
                if hasattr(parent_window, 'load_workspace'):
                    parent_window.load_workspace(workspace)
    