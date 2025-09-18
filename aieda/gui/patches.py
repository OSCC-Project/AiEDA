"""
@File : patches.py
@Author : yell
@Desc : Patches Layout UI for AiEDA system
"""

import sys
import os
from PyQt5.QtWidgets import (QWidget,QGraphicsScene,QGraphicsView, QHBoxLayout,QVBoxLayout, QGraphicsRectItem,
                             QGraphicsLineItem, QLabel)
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QRectF

from .basic import ZoomableGraphicsView

class PatchesLayout(QWidget):
    """Patch Layout UI component"""
    
    def __init__(self, patches, color_list):
        self.patches = patches
        self.color_list = color_list
        super().__init__()
        
        self._init_ui()
        self.draw_layout()
        
    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Create QGraphicsScene and custom ZoomableGraphicsView
        self.scene = QGraphicsScene()
        self.view = ZoomableGraphicsView(self.scene, self)  # Pass self as parent
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        # 设置视图背景为黑色
        # self.view.viewport().setStyleSheet("background-color: black;")
        
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
        """Zoom in on the view"""
        self.view.scale(1.2, 1.2)
    
    def zoom_out(self):
        """Zoom out from the view"""
        self.view.scale(0.8, 0.8)
    
    def fit_view(self):
        """Fit the view to the entire scene"""
        if not self.scene.items():
            return
        
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        
    def draw_layout(self):
        self.scene.clear()
        
        for patch in self.patches:
            # add patch rect
            rect_item = QGraphicsRectItem(patch.llx, 
                                          patch.lly, 
                                          patch.urx-patch.llx, 
                                          patch.ury-patch.lly)
                    
            # Set border to dashed line
            pen = QPen(QColor(0, 0, 0), 5.0)
            pen.setStyle(Qt.DashLine)
            rect_item.setPen(pen)
            self.scene.addItem(rect_item)
            
            for layer in patch.patch_layer:
                for net in layer.nets:
                    for wire in net.wires:
                        # color_id = net.id % len(self.color_list)
                        # color = self.color_list.get(color_id, self.color_list[None])   
                        # wire_pen = QPen(color, 30)     
                        for path in wire.paths:
                            if path.node1.layer == path.node2.layer or path.node1.layer > path.node2.layer:
                                color_id = path.node1.layer % len(self.color_list)
                                color = self.color_list[color_id]
                            else:
                                color_id = path.node2.layer % len(self.color_list)
                                color = self.color_list[color_id]
                                
                            wire_pen = QPen(color, 30) 
                    
                            line_item = QGraphicsLineItem(path.node1.x, 
                                                          path.node1.y, 
                                                          path.node2.x, 
                                                          path.node2.y)
                            line_item.setPen(wire_pen)
                            self.scene.addItem(line_item)
            
        self.fit_view()
        
    def update_coord_status(self, coord_text):
        """Update the coordinate status display in the bottom status bar"""
        self.coord_label.setText(coord_text)
    
    def on_net_selected(self, selected_net):
        """处理选中网络的槽函数，绘制外接矩形并调整视图"""
        # 如果已经有选中的矩形，先移除它
        if hasattr(self, 'selected_net_rect') and self.selected_net_rect is not None:
            self.scene.removeItem(self.selected_net_rect)
            self.selected_net_rect = None
        
        # 检查选中的网络是否有feature属性
        if hasattr(selected_net, 'feature') and selected_net.feature:
            feature = selected_net.feature
            
            # 检查feature是否有llx、lly、width、height属性
            if all(hasattr(feature, attr) for attr in ['llx', 'lly', 'width', 'height']):
                # 创建白色边框的矩形
                pen = QPen(QColor(200, 0, 0), 10)  
                pen.setStyle(Qt.DashLine)
                
                # 创建矩形项
                self.selected_net_rect = QGraphicsRectItem(
                    feature.llx-100, feature.lly-100, feature.width+200, feature.height+200
                )
                
                # 设置矩形的样式
                self.selected_net_rect.setPen(pen)
                self.selected_net_rect.setBrush(QBrush(Qt.NoBrush))  # 无边填充
                
                # 添加矩形到场景
                self.scene.addItem(self.selected_net_rect)
                
                # 将矩形移到最顶层，确保可见
                self.selected_net_rect.setZValue(100)  # 设置高的z值
                
                # 让视图自动调整到能看到整个选中的网络矩形
                self.view.fitInView(self.selected_net_rect, Qt.KeepAspectRatio)
                # 稍微缩小视图，在选中的矩形周围留出一些空间
                self.view.scale(0.9, 0.9)
        
        