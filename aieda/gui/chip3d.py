# -*- encoding: utf-8 -*-

import sys
import os
import concurrent.futures
from typing import List, Dict, Optional, Tuple

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QMessageBox, QSplitter)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QColor, QFont, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView

from ..workspace import Workspace
import json

class Chip3D(QWidget):
    def __init__(self, workspace:Workspace, vec_cells, vec_instances, vec_nets, color_list, parent: Optional[QWidget] = None):
        """初始化Chip3D窗口小部件
        
        参数:
            workspace: 
            vec_cells: 单元的数据向量
            vec_instances: 实例数据
            vec_nets: 线网数据
            color_list: 不同单元类型的颜色列表
            parent: 父窗口小部件（可选）
        """
        super().__init__(parent)
        self.workspace = workspace
        self.vec_cells = vec_cells
        self.vec_instances = vec_instances
        self.vec_nets = vec_nets
        self.color_list = color_list
        
        self.is_rotating = False
        self.is_axes = False
        
        # 初始化UI
        self.init_ui()
        self.init_html()
    
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        control_layout = QVBoxLayout()
        
        # Add reset camera button
        import os
        current_dir = os.path.split(os.path.abspath(__file__))[0]
        
        self.reset_camera_btn = QPushButton(QIcon("{}/icon/camera_reset.png".format(current_dir)), "")
        self.reset_camera_btn.setToolTip("Reset Camera")
        self.reset_camera_btn.clicked.connect(self.reset_camera)
        control_layout.addWidget(self.reset_camera_btn)
        
        # Add data roate button
        self.rotate_btn = QPushButton(QIcon("{}/icon/rotate_off.png".format(current_dir)), "")
        self.rotate_btn.setToolTip("Rotation")
        self.rotate_btn.clicked.connect(self.rotate_view)
        control_layout.addWidget(self.rotate_btn)
        
        self.toggle_axes_btn = QPushButton(QIcon("{}/icon/axes_off.png".format(current_dir)), "")
        self.toggle_axes_btn.setToolTip("Axes")
        self.toggle_axes_btn.clicked.connect(self.toggle_axes)
        control_layout.addWidget(self.toggle_axes_btn)
        
        # Add stretch to push buttons to the left
        control_layout.addStretch()
        
        # 创建控制栏容器并设置固定宽度
        control_widget = QWidget()
        control_widget.setLayout(control_layout)
        control_widget.setFixedWidth(60)  # 设置左侧控制栏的宽度为60像素
        
        # Add control bar to main layout
        main_layout.addWidget(control_widget)
        
        # Create WebEngineView for Three.js rendering
        self.web_view = QWebEngineView()
        self.web_view.setMinimumSize(1000, 800)
        main_layout.addWidget(self.web_view)
        
        # laod data
        self.web_view.loadFinished.connect(self.on_page_loaded)
        
        self.setLayout(main_layout)
        self.setWindowTitle("Chip 3D")
        self.showMaximized()
        
    def init_html(self):
        """show layout in viewer"""
        layout_viewer_path = os.path.join(os.path.dirname(__file__), '3d', 'chip.html')
        
        if not os.path.exists(layout_viewer_path):
            QMessageBox.warning(self, "Error", f"Layout viewer not found at {layout_viewer_path}")
            return

        self.web_view.load(QUrl.fromLocalFile(layout_viewer_path))
    
    def resizeEvent(self, event):
        """Handle resize events"""
        # Call base class resize event
        super().resizeEvent(event)
        
    def reset_camera(self):
        """重置相机视角"""
        self.web_view.page().runJavaScript("if (typeof reset_camera !== 'undefined') { reset_camera(); }")
    
    def toggle_axes(self):
        self.is_axes = not self.is_axes
        
        # 更新按钮图标和提示文本
        current_dir = os.path.split(os.path.abspath(__file__))[0]
        if self.is_axes:
            self.toggle_axes_btn.setIcon(QIcon("{}/icon/axes_on.png".format(current_dir)))
            self.toggle_axes_btn.setToolTip("Show Axes")
        else:
            self.toggle_axes_btn.setIcon(QIcon("{}/icon/axes_off.png".format(current_dir)))
            self.toggle_axes_btn.setToolTip("Hide Axes")
            
        self.web_view.page().runJavaScript("if (typeof toggle_axes !== 'undefined') { toggle_axes(); }")
        
    def rotate_view(self):
        """切换旋转模式"""
        self.is_rotating = not self.is_rotating
        
        # 更新按钮图标和提示文本
        current_dir = os.path.split(os.path.abspath(__file__))[0]
        if self.is_rotating:
            self.rotate_btn.setIcon(QIcon("{}/icon/rotate_on.png".format(current_dir)))
            self.rotate_btn.setToolTip("Stop Rotation")
        else:
            self.rotate_btn.setIcon(QIcon("{}/icon/rotate_off.png".format(current_dir)))
            self.rotate_btn.setToolTip("Start Rotation")
        
        # 调用JavaScript函数切换旋转模式
        self.web_view.page().runJavaScript("if (typeof rotation_mode !== 'undefined') { rotation_mode(); }")
    
    def on_page_loaded(self, success):
        """callback to load data"""
        if success:
            json_data = self.generate()
            self.web_view.page().runJavaScript(f"updateChipData({json_data});")
        else:
            print("Failed to load the 3D layout viewer")
    
    def generate(self):
        def generate_nets(vec_nets):
            json_nets = []
            for vec_net in self.vec_nets:
                for wire in vec_net.wires:
                    for path in wire.paths:
                        layer_id = (path.node1.layer + path.node2.layer) / 2
                        color_id = layer_id % len(self.color_list)
                        color = {
                            "r": self.color_list[color_id].red() / 255.0, 
                            "g": self.color_list[color_id].green() / 255.0, 
                            "b": self.color_list[color_id].blue() / 255.0
                            }
                        
                        if path.node1.layer == path.node2.layer:
                            type = "Wire"
                        else:
                            type = "Via"
                        
                        path_data = {
                            "type": type,
                            'x1': path.node1.real_x,
                            'y1': path.node1.real_y,
                            'z1': path.node1.layer,
                            'x2': path.node2.real_x,
                            'y2': path.node2.real_y,
                            'z2': path.node2.layer,
                            'color': color,
                            'comment': f'Net_{vec_net.name}',
                            'shapeClass': f'Net_Class_{path.node1.layer}'
                        }
                            
                        json_nets.append(path_data)
                        
            return json_nets
        
        def generate_instances(instances):
            json_inst = []
            for vec_instance in instances:
                path_data = {
                            "type": "Rect",
                            'x1': vec_instance.llx,
                            'y1': vec_instance.lly,
                            'z1': 0,
                            'x2': vec_instance.urx,
                            'y2': vec_instance.ury,
                            'z2': 0,
                            'color': {"r" : 0.3, "g" : 0.3, "b" : 0.3},
                            'comment': f'{vec_instance.name}',
                            'shapeClass': f'{vec_instance.cell_id}'
                        }
                
                json_inst.append(path_data)
            
            return json_inst

        
        chip_data = {}
        
        chip_data["instances"] = generate_instances(self.vec_instances.instances)    
        chip_data["nets"] = generate_nets(self.vec_nets)

        return json.dumps(chip_data)
    