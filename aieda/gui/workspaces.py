# -*- encoding: utf-8 -*-

import sys
import os

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QPushButton, QFileDialog, 
    QMessageBox, QGroupBox, QGridLayout, QCheckBox, 
    QMenuBar, QMenu, QAction, QListWidget, QListWidgetItem,
    QSplitter
)

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QRect, QSize

from aieda.gui.chip import ChipLayout
from aieda.gui.workspace import WorkspaceUI
from aieda.workspace import Workspace


class WorkspacesUI(QMainWindow):
    """Main application window for managing and displaying workspaces in AiEDA system.
    
    This class provides the main interface for browsing, loading, and analyzing workspaces.
    It includes a sidebar for workspace list and information, a main content area for displaying
    workspace details, and menu options for file operations and analysis tools.
    
    Attributes:
        main_layout (QHBoxLayout): Main layout container
        workspace_ui (WorkspaceUI): Workspace UI component
        workspace_list (WorkspaceListUI): Workspace list UI component
        content_widget (QWidget): Main content area widget
        content_layout (QVBoxLayout): Content area layout
        sidebar (QWidget): Sidebar widget
        toggle_sidebar_btn (QPushButton): Button to toggle sidebar visibility
        sidebar_visible (bool): Flag indicating if sidebar is visible
        sidebar_width (int): Width of the sidebar
        control_bar (QVBoxLayout): Control bar layout
        control_bar_widget (QWidget): Control bar widget
    """
    
    def __init__(self, workspace=None):
        """Initialize the WorkspacesUI with optional workspace.
        
        Args:
            workspace (Workspace, optional): Initial workspace to load
        """
        super().__init__()
        self.main_layout = None
        self.workspace_ui = None
        self.workspace_list = None
        self.content_widget = None
        self.content_layout = None
        self.sidebar = None
        self.toggle_sidebar_btn = None
        self.sidebar_visible = False
        self.sidebar_width = 800
        self.control_bar = None
        self.control_bar_widget = None
        
        self.init_ui()
        
        self.showMaximized()
        
        self.load_workspace(workspace)
        
    def init_ui(self):
        """Initialize all user interface components of the application window."""
        self.init_main()
        self.init_menu()
        self.init_sidebar()
        self.init_workspace_list()
        self.init_content_area()
        
    def init_main(self):
        """Initialize the main window components and layout structure."""
        self.setWindowTitle("AiEDA Workspaces Viewer")
        self.setGeometry(100, 100, 1200, 900)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.main_layout = QHBoxLayout(central_widget)
        
        self.control_bar_widget = QWidget()
        self.control_bar = QVBoxLayout(self.control_bar_widget)
        self.control_bar.setContentsMargins(5, 5, 5, 5)
        self.control_bar.setSpacing(5)
        
        import os
        current_dir = os.path.split(os.path.abspath(__file__))[0]
        self.toggle_sidebar_btn = QPushButton(QIcon("{}/icon/hide.png".format(current_dir)), "")
        self.toggle_sidebar_btn.clicked.connect(self.toggle_sidebar)
        self.control_bar.addWidget(self.toggle_sidebar_btn)
        self.control_bar.addStretch()
        
        self.main_layout.addWidget(self.control_bar_widget)
        
    def init_sidebar(self):
        """Initialize the sidebar for displaying workspace list and information."""
        self.sidebar = QWidget()
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar.setFixedWidth(self.sidebar_width)
        self.sidebar.setStyleSheet("background-color: #f0f0f0;")
        
        self.sidebar.setParent(self)
        self.sidebar.move(50, 30)
        self.sidebar.resize(self.sidebar_width, self.height())
        self.sidebar.hide()
        
    def toggle_sidebar(self):
        """Toggle the visibility of the workspace sidebar."""
        if self.sidebar_visible:
            self.sidebar.hide()
            import os
            current_dir = os.path.split(os.path.abspath(__file__))[0]
            self.toggle_sidebar_btn.setIcon(QIcon("{}/icon/show.png".format(current_dir)))
        else:
            self.sidebar.show()
            import os
            current_dir = os.path.split(os.path.abspath(__file__))[0]
            self.toggle_sidebar_btn.setIcon(QIcon("{}/icon/hide.png".format(current_dir)))
        
        self.sidebar_visible = not self.sidebar_visible
        self.updateGeometry()
    
    def resizeEvent(self, event):
        """Handle resize event for adjusting sidebar position and size.
        
        Args:
            event (QResizeEvent): Resize event object
        """
        super().resizeEvent(event)
        
        if self.sidebar_visible and hasattr(self, 'control_bar_widget'):
            self.sidebar.setGeometry(
                QRect(
                    self.control_bar_widget.width() + 20,
                    50,
                    800,
                    self.height()
                )
            )
        
        self.updateGeometry()
    
    def init_workspace_list(self):
        """Initialize the workspace list and information UI with 2:8 vertical ratio layout."""
        self.workspace_list = self.WorkspaceListUI()
        
        self.workspace_info = self.WorkspaceInfoUI()
        self.workspace_info.init_ui()
        
        self.sidebar_layout.addWidget(self.workspace_list)
        self.sidebar_layout.addWidget(self.workspace_info)
        
    def load_workspace(self, workspace):
        """Load a workspace into the UI.
        
        Args:
            workspace: The workspace object to load
        """
        if not workspace:
            return
        
        if self.workspace_ui:
            self.content_layout.removeWidget(self.workspace_ui)
            self.workspace_ui.deleteLater()
            self.workspace_ui = None
        
        self.workspace_ui = WorkspaceUI(workspace)
        self.content_layout.addWidget(self.workspace_ui)
        
        if self.workspace_list:
            self.workspace_list.add_workspace(workspace)
        
        if hasattr(self, 'workspace_info'):
            self.workspace_info.load_workspace(workspace)


    def init_content_area(self):
        """Initialize the main content area for displaying workspace details."""
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        
        self.main_layout.addWidget(self.content_widget, 1)
        
    def create_multi_widget_layout(self, widget_list):
        """Create a layout with multiple widgets.
        
        Args:
            widget_list: List of widgets to add to the layout
        
        Returns:
            QVBoxLayout: Layout containing the widgets
        """
        if not widget_list:
            return None
        
        layout = QVBoxLayout()
        for widget in widget_list:
            layout.addWidget(widget)
        
        return layout
    
    def set_widget_position(self, widget, x, y, width, height):
        """Set the position and size of a widget.
        
        Args:
            widget: The widget to position
            x: X-coordinate
            y: Y-coordinate
            width: Width of the widget
            height: Height of the widget
        """
        widget.setGeometry(x, y, width, height)
        
    def init_menu(self):
        """Initialize the menu bar with File and Analysis menus."""
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        
        load_action = QAction('Load Workspace', self)
        load_action.triggered.connect(self.load_workspace_dialog)
        file_menu.addAction(load_action)
        
        analysis_menu = menubar.addMenu('Analysis')
        
        instances_action = QAction('Instances', self)
        instances_action.triggered.connect(self.show_instances_analysis)
        analysis_menu.addAction(instances_action)
        
        nets_action = QAction('Nets', self)
        nets_action.triggered.connect(self.show_nets_analysis)
        analysis_menu.addAction(nets_action)
        
        patches_action = QAction('Patches', self)
        patches_action.triggered.connect(self.show_patches_analysis)
        analysis_menu.addAction(patches_action)
        
        drc_action = QAction('DRC', self)
        drc_action.triggered.connect(self.show_drc_analysis)
        analysis_menu.addAction(drc_action)
        
    def show_instances_analysis(self):
        """Show instances analysis dialog."""
        if hasattr(self, 'workspace_ui') and self.workspace_ui:
            QMessageBox.information(self, "Instances Analysis", "Instances analysis functionality will be implemented here.")
        else:
            QMessageBox.warning(self, "Warning", "Please load a workspace first.")
            
    def show_nets_analysis(self):
        """Show nets analysis dialog."""
        if hasattr(self, 'workspace_ui') and self.workspace_ui:
            QMessageBox.information(self, "Nets Analysis", "Nets analysis functionality will be implemented here.")
        else:
            QMessageBox.warning(self, "Warning", "Please load a workspace first.")
            
    def show_drc_analysis(self):
        """Show DRC analysis dialog."""
        if hasattr(self, 'workspace_ui') and self.workspace_ui:
            QMessageBox.information(self, "DRC Analysis", "DRC analysis functionality will be implemented here.")
        else:
            QMessageBox.warning(self, "Warning", "Please load a workspace first.")
            
    def show_patches_analysis(self):
        """Show patches analysis dialog."""
        if hasattr(self, 'workspace_ui') and self.workspace_ui:
            QMessageBox.information(self, "Patches Analysis", "Patches analysis functionality will be implemented here.")
        else:
            QMessageBox.warning(self, "Warning", "Please load a workspace first.")
        
    def load_workspace_dialog(self):
        """Show dialog to load a workspace from file."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Workspace", "", "Workspace Files (*.json);;All Files (*)", options=options)
        
        if file_path:
            try:
                workspace = Workspace.load_from_json(file_path)
                self.load_workspace(workspace)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load workspace: {str(e)}")
                
                                  
    class WorkspaceListUI(QWidget):
        """UI component for displaying list of workspaces with icons in a 4-column layout."""
        
        def __init__(self):
            """Initialize the WorkspaceListUI component."""
            super().__init__()
            
            self.workspaces = {}
            self.list_widget = None
            self.init_ui()
            
        def init_ui(self):
            """Initialize the workspace list UI components."""
            layout = QVBoxLayout(self)
            
            title_label = QLabel("Workspaces List")
            title_label.setAlignment(Qt.AlignCenter)
            font = QFont()
            font.setBold(True)
            title_label.setFont(font)
            layout.addWidget(title_label)
            
            self.list_widget = QListWidget()
            self.list_widget.setMinimumWidth(600)
            self.setMinimumWidth(610)
            
            self.list_widget.setViewMode(QListWidget.IconMode)
            self.list_widget.setFlow(QListWidget.LeftToRight)
            self.list_widget.setWrapping(True)
            self.list_widget.setResizeMode(QListWidget.Adjust)
            self.list_widget.setGridSize(QSize(140, 60))
            layout.addWidget(self.list_widget)
            
        def add_workspace(self, workspace):
            """Add a workspace to the list.
            
            Args:
                workspace: The workspace object to add
            """
            self.workspaces[workspace.design] = workspace
            self.update_ui()
            
        def update_ui(self):
            """Update the workspace list UI with current workspaces."""
            self.list_widget.clear()
            
            font = QFont()
            font.setBold(True)
            font.setPointSize(11)
            
            import os
            current_dir = os.path.split(os.path.abspath(__file__))[0]
            icon_path = "{}/icon/chip.png".format(current_dir)
            
            for design_name in list(self.workspaces.keys()):
                item = QListWidgetItem(design_name)
                if os.path.exists(icon_path):
                    item.setIcon(QIcon(icon_path))
                item.setFont(font)
                item.setTextAlignment(Qt.AlignCenter)
                self.list_widget.addItem(item)
            
            self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
          
        def on_item_double_clicked(self, item):
            """Handle double-click event on workspace items.
            
            Args:
                item: The clicked QListWidgetItem
            """
            design_name = item.text()
            if design_name in self.workspaces:
                workspace = self.workspaces[design_name]
                parent_window = self.window()
                if hasattr(parent_window, 'load_workspace'):
                    parent_window.load_workspace(workspace)
                    if hasattr(parent_window, 'workspace_info'):
                        parent_window.workspace_info.load_workspace(workspace)
    
    class WorkspaceInfoUI(QWidget):
        """UI component for displaying detailed information about a selected workspace."""
        
        def __init__(self):
            """Initialize the WorkspaceInfoUI component."""
            super().__init__()
            self.info_text = None
            
        def init_ui(self):
            """Initialize the workspace info UI components."""
            layout = QVBoxLayout(self)
            # Set spacing to 0 to make title_label and info_text closer
            layout.setSpacing(0)
            
            title_label = QLabel("Workspace Info")
            title_label.setAlignment(Qt.AlignCenter)
            font = QFont()
            font.setBold(True)
            title_label.setFont(font)
            layout.addWidget(title_label)
            
            self.info_text = QLabel("Select a workspace to see details")
            self.info_text.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            self.info_text.setWordWrap(True)
            self.info_text.setMinimumHeight(200)
            # Reduced padding from 10px to 0px to make it closer to title_label
            self.info_text.setStyleSheet("background-color: white; padding: 0px; border-radius: 4px;")
            self.info_text.setTextFormat(Qt.RichText)
            layout.addWidget(self.info_text)
            
        def load_workspace(self, workspace):
            """Load and display workspace information in HTML format.
            
            Args:
                workspace: The workspace object to display information for
            """
            if not workspace:
                self.info_text.setText("No workspace selected")
                return
            
            info_str = []
            
            info_str.append(f"<p><b>Design:</b> {workspace.design}</p>")
            info_str.append(f"<p><b>Directory:</b> {workspace.directory}</p>")
            
            info_str.append("<hr>")
            
            info_str.append(f"<p><b>Process node:</b> {workspace.configs.workspace.process_node}</p>")
            info_str.append(f"<p><b>version:</b> {workspace.configs.workspace.version}</p>")
            
            info_str.append("<hr>")
            
            info_str.append("<p><b>Flows:</b></p>")
            info_str.append("<table border='1' cellspacing='0' cellpadding='3' style='border-collapse:collapse;'>")
            info_str.append("<tr style='background-color:#f0f0f0;'>")
            info_str.append("<th style='width:150px;'>Step</th>")
            info_str.append("<th style='width:150px;'>EDA Tool</th>")
            info_str.append("<th style='width:150px;'>State</th>")
            info_str.append("<th style='width:150px;'>Runtime</th>")
            info_str.append("</tr>")
            
            for flow in workspace.configs.flows:
                step_str = str(flow.step.value)[:50]
                tool_str = str(flow.eda_tool)[:50]
                state_str = str(flow.state.value)[:50]
                runtime_str = str(flow.runtime)[:50]
                info_str.append("<tr>")
                info_str.append(f"<td style='text-align:left;'>{step_str}</td>")
                info_str.append(f"<td style='text-align:left;'>{tool_str}</td>")
                info_str.append(f"<td style='text-align:left;'>{state_str}</td>")
                info_str.append(f"<td style='text-align:left;'>{runtime_str}</td>")
                info_str.append("</tr>")
            
            info_str.append("</table>")

            self.info_text.setText('\n'.join(info_str))
    