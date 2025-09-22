"""
@File : patches.py
@Author : yell
@Desc : Patches Layout UI for AiEDA system
"""

import sys
import os
from PyQt5.QtWidgets import (QWidget,QGraphicsScene,QGraphicsView, QHBoxLayout,QVBoxLayout, QGraphicsRectItem,
                             QGraphicsLineItem, QLabel, QGraphicsItem)
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QRectF, pyqtSignal

from .basic import ZoomableGraphicsView

class HighlightableRectItem(QGraphicsRectItem):
    """可高亮的矩形项，支持鼠标悬停和双击事件"""
    # 注意：QGraphicsRectItem本身不继承QObject，不能直接使用pyqtSignal
    # 因此我们使用传统的方式实现双击事件
    
    def __init__(self, rect_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rect_id = int(rect_id)  # 存储矩形的id
        self.original_pen = self.pen()  # 保存原始笔样式
        self.setAcceptHoverEvents(True)  # 接受悬停事件
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)  # 可选择
    
    def hoverEnterEvent(self, event):
        """鼠标进入时高亮显示"""
        # 创建高亮样式的笔
        highlight_pen = QPen(QColor(0, 255, 0), 50)  # 绿色粗边框
        highlight_pen.setStyle(Qt.DashLine)
        self.setPen(highlight_pen)
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """鼠标离开时恢复原始样式"""
        self.setPen(self.original_pen)
        super().hoverLeaveEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """双击事件，使用传统方式处理"""
        if event.button() == Qt.LeftButton:
            # 查找父窗口
            parent_widget = self.scene().views()[0].parent()
            if hasattr(parent_widget, 'on_rect_double_clicked'):
                parent_widget.on_rect_double_clicked(self.rect_id)
        super().mouseDoubleClickEvent(event)

class PatchesLayout(QWidget):
    """Patch Layout UI component"""
    
    def __init__(self, vec_patches, color_list, patch_layout=None):
        self.patches = self.load_patches(vec_patches)
        self.color_list = color_list
        self.rect_items = {} 
        self.overlapping_rects = {}  # 存储交叠的矩形边框 (使用字典便于通过id管理)
        self.patch_layout = patch_layout  # 将在WorkspaceUI中设置PatchLayout的引用
        super().__init__()
        
        self._init_ui()
        self.draw_layout()
    
    def load_patches(self, vec_patches):
        patches = {patch.id : patch for patch in vec_patches} if vec_patches else {}
        return patches

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
        self.rect_items = {}  # 清空矩形项列表
        self.overlapping_rects = {}  # 清空交叠矩形字典
        
        for id, patch in self.patches.items():
            # add patch rect
            # 使用自定义的HighlightableRectItem替代默认的QGraphicsRectItem
            rect_item = HighlightableRectItem(str(id), patch.llx, 
                                          patch.lly, 
                                          patch.urx-patch.llx, 
                                          patch.ury-patch.lly)
                    
            # Set border to dashed line
            pen = QPen(QColor(0, 0, 0), 5.0)
            pen.setStyle(Qt.DashLine)
            rect_item.setPen(pen)
            self.scene.addItem(rect_item)
            self.rect_items[id] = rect_item # 存储矩形项
            
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
        
    def on_rect_double_clicked(self, rect_id):
        """处理矩形双击事件，显示矩形的id并将选中的patch传递给PatchLayout"""
        # 在状态栏显示矩形id
        current_text = self.coord_label.text()
        self.coord_label.setText(f"ID: {rect_id} | {current_text}")
        
        # 判断rect_id类型并转换为数字
        try:
            # 如果rect_id是字符串，尝试转换为数字
            if isinstance(rect_id, str):
                rect_id_key = int(rect_id)
            else:
                rect_id_key = rect_id
        except ValueError:
            # 如果转换失败，使用原始rect_id
            rect_id_key = rect_id
        
        # 获取选中的patch
        selected_patch = self.patches.get(rect_id_key, None)
        
        # 如果patch_layout引用已设置，则传递选中的patch
        if self.patch_layout is not None and selected_patch is not None:
            self.patch_layout.update_patch(selected_patch)
        
    
    def on_net_selected(self, selected_net):
        """处理选中网络的槽函数，绘制外接矩形并调整视图"""
        # 如果已经有选中的矩形，先移除它
        if hasattr(self, 'selected_net_rect') and self.selected_net_rect is not None:
            self.scene.removeItem(self.selected_net_rect)
            self.selected_net_rect = None
        
        # 移除之前的交叠矩形边框
        for id, rect in self.overlapping_rects.items():
            if rect in self.scene.items():
                self.scene.removeItem(rect)
        self.overlapping_rects = {}
        
        # 检查选中的网络是否有feature属性
        if hasattr(selected_net, 'feature') and selected_net.feature:
            feature = selected_net.feature
            
            # 检查feature是否有llx、lly、width、height属性
            if all(hasattr(feature, attr) for attr in ['llx', 'lly', 'width', 'height']):
                # 创建白色边框的矩形
                pen = QPen(QColor(200, 0, 0), 40)  
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
                
                # 检测并显示与选中网络矩形有交叠的patch矩形
                self._show_overlapping_rects()
                
                # 让视图自动调整到能看到整个选中的网络矩形
                self.view.fitInView(self.selected_net_rect, Qt.KeepAspectRatio)
                # 稍微缩小视图，在选中的矩形周围留出一些空间
                self.view.scale(0.6, 0.6)
                
    def _show_overlapping_rects(self):
        """显示与选中网络矩形有交叠的patch矩形边框"""
        if not hasattr(self, 'selected_net_rect') or self.selected_net_rect is None:
            return
        
        # 获取选中网络矩形的边界
        selected_rect = self.selected_net_rect.rect()
        
        # 遍历所有patch矩形，检查是否有交叠
        for id, rect_item in self.rect_items.items():
            # 获取当前矩形的边界
            patch_rect = rect_item.rect()
            
            # 检查两个矩形是否有交叠
            if selected_rect.intersects(patch_rect):
                # 创建白色虚线边框矩形
                white_pen = QPen(QColor(200, 0, 0), 20)
                white_pen.setStyle(Qt.DashLine)
                
                # 创建矩形项
                overlapping_rect = QGraphicsRectItem(
                    patch_rect.x(), patch_rect.y(), patch_rect.width(), patch_rect.height()
                )
                
                # 设置矩形的样式
                overlapping_rect.setPen(white_pen)
                # 设置透明红色底色 (R=255, G=0, B=0, Alpha=50)
                overlapping_rect.setBrush(QBrush(QColor(50, 50, 50, 50)))
                
                # 添加矩形到场景
                self.scene.addItem(overlapping_rect)
                
                # 将矩形移到顶层，确保可见
                overlapping_rect.setZValue(0)  # 比选中网络矩形低1，避免遮挡
                
                # 存储交叠矩形，以便后续移除
                self.overlapping_rects[id] = overlapping_rect
        
        