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
    QHeaderView, QPushButton, QComboBox, QCheckBox, QTextEdit, QLineEdit
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
        
        self._init_ui()
    
    def create_icon(self, step, state, b_last = False):
        """Create a widget to display flow step information with icon and state
        
        Args:
            step: The flow step name
            state: The flow state
            
        Returns:
            QWidget: A widget containing icon and state information
        """
        import os
        current_dir = os.path.split(os.path.abspath(__file__))[0]
        icon_path = "{}/icon/{}.png".format(current_dir, state)
        
        # 创建主容器widget替代QPushButton
        container = QWidget()
        container.setMinimumHeight(40)
        container.setMaximumHeight(60)
        container.setMinimumWidth(120)
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        container.setToolTip(f"{step}-{state}")
        
        # 创建水平布局
        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 添加状态文本
        state_label = QLabel(f"{step}")
        state_label.setAlignment(Qt.AlignCenter)
        state_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(state_label, alignment=Qt.AlignCenter)
        
        # 添加图标
        icon_label = QLabel()
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            icon_pixmap = icon.pixmap(24, 24)
            icon_label.setPixmap(icon_pixmap)
        else:
            # 如果图标不存在，显示占位符
            icon_label.setText("?")
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setMinimumSize(24, 24)
        layout.addWidget(icon_label, alignment=Qt.AlignCenter)
        
        # 添加间隔符
        if not b_last:
            separator = QLabel("......")
            separator.setAlignment(Qt.AlignCenter)
            layout.addWidget(separator)
        
        return container
        
    def _init_ui(self):
        """Initialize the UI by creating a horizontal layout with evenly distributed flow buttons"""
        # Create a horizontal layout for the buttons
        icon_layout = QHBoxLayout(self)
        icon_layout.setSpacing(15)  # Set spacing between buttons
        icon_layout.setContentsMargins(15, 10, 15, 10)  # Set margins around the layout
        
        try:
            # Create buttons for each flow step and add to the layout
            buttons = []
            if hasattr(self.workspace, 'configs') and hasattr(self.workspace.configs, 'flows'):
                for index, flow in enumerate(self.workspace.configs.flows):
                    step_value = flow.step.value if hasattr(flow.step, 'value') else str(flow.step)
                    state_value = flow.state.value if hasattr(flow.state, 'value') else str(flow.state)
                    
                    b_last = False
                    if index == len(self.workspace.configs.flows) - 1:
                        b_last = True
                    icon = self.create_icon(step_value, state_value, b_last)
                    buttons.append(icon)
                    icon_layout.addWidget(icon)
            else:
                state_label = QLabel(f"No Flows Available")
                icon_layout.addWidget(state_label)
            
            # Set equal stretch factors for all buttons to ensure even distribution
            for i in range(len(buttons)):
                icon_layout.setStretch(i, 1)
        except Exception as e:
            error_label = QLabel(f"Failed to initialize flows: {str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            icon_layout.addWidget(error_label)
        
        # Set the layout for this widget
        self.setLayout(icon_layout)
        
        self.setMaximumHeight(60)