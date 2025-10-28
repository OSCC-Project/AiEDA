"""
@File : flows.py
@Author : yell
@Desc : flows UI for AiEDA system
"""

import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QComboBox, QCheckBox, QTextEdit, QLineEdit, QSizePolicy
)
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush, QIcon
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QSizePolicy

class WorkspaceFlows(QWidget):

    def __init__(self, workspace, parent=None):
        """Initialize the WorkspaceInformation component
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.workspace = workspace
        
        # Set black background for the WorkspaceFlows widget
        self.setStyleSheet("background-color: black;")
        
        self._init_ui()
    
    def create_icon(self, flow, b_last = False):
        """Create a widget to display flow step information with icon and state
        
        Args:
            flow: Flow object containing step and state information
            b_last: Whether this is the last flow in the sequence
            
        Returns:
            QWidget: A widget containing icon and state information with click event handling
        """
        import os
        current_dir = os.path.split(os.path.abspath(__file__))[0]
        icon_path = "{}/icon/{}.png".format(current_dir, flow.state.value)
        
        # 创建主容器widget替代QPushButton
        container = QWidget()
        container.setMinimumHeight(40)
        container.setMaximumHeight(60)
        container.setMinimumWidth(120)
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        container.setToolTip(f"{flow.step.value}-{flow.state.value}")
        # 设置容器背景为黑色
        container.setStyleSheet("background-color: black;")
        
        # 创建水平布局
        layout = QHBoxLayout(container)
        # layout.setContentsMargins(5, 5, 5, 5)
        # layout.setSpacing(5)
        
        # 添加状态文本（白色，提高对比度）
        state_label = QLabel(f"{flow.step.value}")
        state_label.setAlignment(Qt.AlignCenter)
        state_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        state_label.setStyleSheet("color: white;")
        layout.addWidget(state_label, alignment=Qt.AlignCenter)
        
        # 添加图标
        icon_label = QLabel()
        # 设置鼠标指针样式为手型，表示可点击
        icon_label.setCursor(Qt.PointingHandCursor)
        # 使用闭包函数添加点击事件，避免使用event.sender()
        def on_click(event):
            # 直接使用捕获的flow对象
            self._handle_flow_click(flow)
            # 调用原始的鼠标事件处理（如果有）
            QLabel.mousePressEvent(icon_label, event)
        
        icon_label.mousePressEvent = on_click
        
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            icon_pixmap = icon.pixmap(24, 24)
            icon_label.setPixmap(icon_pixmap)
        else:
            # 如果图标不存在，显示占位符（白色）
            icon_label.setText("?")
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setMinimumSize(24, 24)
            icon_label.setStyleSheet("color: white;")
        layout.addWidget(icon_label, alignment=Qt.AlignCenter)
        
        # 添加间隔符（白色）
        if not b_last:
            separator = QLabel("...")
            separator.setAlignment(Qt.AlignCenter)
            separator.setStyleSheet("color: white;")
            layout.addWidget(separator)
        
        return container
        
    def _handle_flow_click(self, flow):
        print(f"Flow clicked: Step={flow.step.value}, State={flow.state.value}")
        
        parent_widget = self.parent()
        if parent_widget.workspace_info is not None:
            parent_widget.workspace_info.on_flow_selected(flow)
                
    def _init_ui(self):
        """Initialize the UI by creating a horizontal layout with evenly distributed flow buttons"""
        # Create a horizontal layout for the buttons
        icon_layout = QHBoxLayout(self)
        # icon_layout.setSpacing(15)  # Set spacing between buttons
        icon_layout.setContentsMargins(15, 10, 15, 10)  # Set margins around the layout
        
        try:
            # Create buttons for each flow step and add to the layout
            buttons = []
            if hasattr(self.workspace, 'configs') and hasattr(self.workspace.configs, 'flows'):
                for index, flow in enumerate(self.workspace.configs.flows):                   
                    b_last = False
                    if index == len(self.workspace.configs.flows) - 1:
                        b_last = True
                    icon = self.create_icon(flow, b_last)
                    buttons.append(icon)
                    icon_layout.addWidget(icon)
            else:
                state_label = QLabel(f"No Flows Available")
                state_label.setStyleSheet("color: white;")
                icon_layout.addWidget(state_label)
            
            # Set equal stretch factors for all buttons to ensure even distribution
            for i in range(len(buttons)):
                icon_layout.setStretch(i, 1)
        except Exception as e:
            # 创建一个错误标签作为占位符
            error_label = QLabel(f"Error: {str(e)[:10]}")
            error_label.setMinimumHeight(40)
            error_label.setStyleSheet("color: white;")
            icon_layout.addWidget(error_label)
        
        # Set the layout for this widget
        self.setLayout(icon_layout)
        
        self.setMaximumHeight(60)