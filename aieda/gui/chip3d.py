# -*- encoding: utf-8 -*-

import sys
import os
import concurrent.futures
from typing import List, Dict, Optional, Tuple

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QMessageBox, QSplitter)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView

from ..data import DataVectors
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
        
        # 初始化UI
        self.init_ui()
        self.show_chip()
    
    def init_ui(self):
        """Initialize UI components including web view and control buttons"""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create control bar
        control_layout = QHBoxLayout()
        
        # Add reset camera button
        self.reset_camera_btn = QPushButton("Reset Camera")
        self.reset_camera_btn.clicked.connect(self.reset_camera)
        control_layout.addWidget(self.reset_camera_btn)
        
        # Add data refresh button
        self.refresh_data_btn = QPushButton("Refresh Data")
        self.refresh_data_btn.clicked.connect(self.refresh_data)
        control_layout.addWidget(self.refresh_data_btn)
        
        # Add stretch to push buttons to the left
        control_layout.addStretch()
        
        # Add control bar to main layout
        main_layout.addLayout(control_layout)
        
        # Create WebEngineView for Three.js rendering
        self.web_view = QWebEngineView()
        self.web_view.setMinimumSize(1000, 800)
        main_layout.addWidget(self.web_view)
        
        # 连接加载完成信号，用于注入数据
        self.web_view.loadFinished.connect(self.on_page_loaded)
        
        self.setLayout(main_layout)
        self.setWindowTitle("Chip 3D Layout Display")
        self.resize(1000, 800)
    
    def resizeEvent(self, event):
        """Handle resize events"""
        # Call base class resize event
        super().resizeEvent(event)
        
    def reset_camera(self):
        """重置相机视角"""
        # 使用JavaScript重置相机
        self.web_view.page().runJavaScript("if (typeof app !== 'undefined' && app.sceneManager) { app.sceneManager.resetView(); }")
    
    def refresh_data(self):
        """刷新显示的数据"""
        # 生成新的JSON数据
        json_data = GenerateJsonNets(self.workspace, self.vec_nets, self.color_list).generate()
        # 将数据传递给JavaScript
        self.web_view.page().runJavaScript(f"updateChipData({json_data});")
    
    def on_page_loaded(self, success):
        """页面加载完成后的回调"""
        if success:
            # 页面加载成功后，注入数据
            self.refresh_data()
        else:
            print("Failed to load the 3D layout viewer")
    
    def show_chip(self):
        """加载layout-viewer到web_view中显示"""
        # 获取layout-viewer的index.html路径
        layout_viewer_path = os.path.join(os.path.dirname(__file__), '3d', 'chip.html')
        
        # 确保路径存在
        if not os.path.exists(layout_viewer_path):
            QMessageBox.warning(self, "Error", f"Layout viewer not found at {layout_viewer_path}")
            return
        
        # 加载HTML文件
        self.web_view.load(QUrl.fromLocalFile(layout_viewer_path))

class GenerateJsonNets:
    def __init__(self, workspace, vec_nets, color_list):
        self.workspace = workspace
        self.vec_nets = vec_nets
        self.color_list = color_list
    
    def generate(self):
        """生成芯片数据的JSON格式"""
        # 生成线网数据
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
                    
        
        # 创建完整的JSON数据对象
        chip_data = {
            "shapes": json_nets,
            # 可以根据需要添加其他数据类型（如单元、过孔等）
        }
        
        with open(self.workspace.paths_table.html["nets_json"], "w", encoding="utf-8") as f_writer:
            json.dump(chip_data, f_writer, indent=4)
            print("save json to {}".format(self.workspace.paths_table.html["nets_json"]))
        
        # 将Python对象转换为JSON字符串
        return json.dumps(chip_data)