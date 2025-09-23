"""
@File : patch.py
@Author : yell
@Desc : Patch Layout UI for AiEDA system
"""

import sys
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QGroupBox, QGridLayout, QScrollArea, QTableWidget, 
                            QTableWidgetItem, QHeaderView)
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QRectF

class PatchImageWidget(QWidget):
    """自定义Widget用于显示所有图层叠加的组合图像"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_dict = None
        self.row_num = 0
        self.col_num = 0
        self.setMinimumSize(400, 400)
        # 设置白色背景和灰色边框
        self.setStyleSheet("background-color: #FFFFFF; border: 2px solid #CCCCCC;")
        
    def set_image_data(self, image_dict, row_num, col_num):
        """设置要显示的图像数据"""
        self.image_dict = image_dict
        self.row_num = row_num
        self.col_num = col_num
        self.update()  # 触发重绘
        
    def paintEvent(self, event):
        """重绘事件，绘制所有图层叠加的图像"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 获取widget尺寸
        width = self.width()
        height = self.height()
        
        # 绘制白色背景
        painter.fillRect(0, 0, width, height, QBrush(QColor(255, 255, 255)))
        
        # 绘制灰色边框
        pen = QPen(QColor(204, 204, 204))  # #CCCCCC 灰色
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(1, 1, width - 2, height - 2)  # 留出边框宽度的边距
        
        if self.image_dict is None or len(self.image_dict) == 0:
            # 显示空提示
            painter.drawText(self.rect(), Qt.AlignCenter, "No image data available")
            return
        
        if self.row_num == 0 or self.col_num == 0:
            return
            
        scale_x = width / self.col_num
        scale_y = height / self.row_num
        scale = min(scale_x, scale_y)  # 使用等比例缩放
        
        # 计算居中偏移
        offset_x = (width - self.col_num * scale) / 2
        offset_y = (height - self.row_num * scale) / 2
        
        # 绘制所有图层的数据（叠加显示）
        for layer_id, layer_array in self.image_dict.items():
            for i in range(self.row_num):
                for j in range(self.col_num):
                    color_value = layer_array[i, j]
                    if color_value > 0:  # 只绘制有颜色的点
                        # 创建QColor对象
                        if isinstance(color_value, int):
                            color_id = color_value
                        else:
                            color_id = int(color_value) if color_value.is_integer() else color_value
                        
                        # 确保颜色ID有效
                        color_id = int(color_id) % 16777216  # 24位颜色值范围
                        
                        # 将颜色ID转换为RGB值
                        r = (color_id >> 16) & 0xFF
                        g = (color_id >> 8) & 0xFF
                        b = color_id & 0xFF
                        
                        painter.setBrush(QBrush(QColor(r, g, b)))
                        painter.setPen(Qt.NoPen)
                        
                        # 绘制像素点（作为矩形）
                        rect = QRectF(
                            offset_x + j * scale,
                            offset_y + i * scale,
                            max(1, scale),  # 确保至少1像素宽
                            max(1, scale)   # 确保至少1像素高
                        )
                        painter.drawRect(rect)
        
        if self.col_num > 0 and self.row_num > 0:
            rect = QRectF(
                offset_x,
                offset_y,
                self.col_num * scale,
                self.row_num * scale
            )
            pen = QPen(QColor(200, 0, 0)) 
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(QBrush(Qt.NoBrush))
            painter.drawRect(rect)
 

class LayerImageWidget(QWidget):
    """自定义Widget用于显示单个图层的图像数据，支持Ctrl+滚轮缩放"""
    
    def __init__(self, layer_id, parent=None):
        super().__init__(parent)
        self.layer_id = layer_id
        self.layer_array = None
        self.row_num = 0
        self.col_num = 0
        self.setMinimumSize(300, 300)
        # 设置白色背景和灰色边框
        self.setStyleSheet("background-color: #FFFFFF; border: 2px solid #CCCCCC;")
        
        # 缩放相关变量
        self.zoom_factor = 1.0  # 初始缩放比例
        self.min_zoom = 0.1     # 最小缩放比例
        self.max_zoom = 10.0    # 最大缩放比例
        self.zoom_step = 0.1    # 每次滚轮缩放的步长
        
    def set_layer_data(self, layer_array, row_num, col_num):
        """设置要显示的图层数据"""
        self.layer_array = layer_array
        self.row_num = row_num
        self.col_num = col_num
        self.update()  # 触发重绘
        
    def wheelEvent(self, event):
        """处理鼠标滚轮事件，实现Ctrl+滚轮缩放功能"""
        # 检查是否按下了Ctrl键
        if event.modifiers() == Qt.ControlModifier:
            # 获取滚轮方向
            delta = event.angleDelta().y()
            
            # 根据滚轮方向调整缩放比例
            if delta > 0:  # 滚轮向上，放大
                self.zoom_factor = min(self.zoom_factor + self.zoom_step, self.max_zoom)
            else:  # 滚轮向下，缩小
                self.zoom_factor = max(self.zoom_factor - self.zoom_step, self.min_zoom)
            
            # 触发重绘以显示缩放后的图像
            self.update()
        else:
            # 如果没有按下Ctrl键，调用父类的事件处理
            super().wheelEvent(event)
            
    def paintEvent(self, event):
        """重绘事件，绘制图层数据，支持缩放"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 获取widget尺寸
        width = self.width()
        height = self.height()
        
        # 绘制白色背景
        painter.fillRect(0, 0, width, height, QBrush(QColor(255, 255, 255)))
        
        # 绘制灰色边框
        pen = QPen(QColor(204, 0, 0))  # #CCCCCC 灰色
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(1, 1, width - 2, height - 2)  # 留出边框宽度的边距
        
        if self.layer_array is None:
            return
        
        if self.row_num == 0 or self.col_num == 0:
            return
            
        # 计算基础像素大小（保持正方形）
        # 取相同的值作为宽高，确保图像显示为正方形
        base_pixel_size = min(width / self.col_num, height / self.row_num)
        
        # 应用缩放比例
        pixel_size = base_pixel_size * self.zoom_factor
        
        # 计算居中偏移，使正方形图像保持在中心位置
        total_width = self.col_num * pixel_size
        total_height = self.row_num * pixel_size
        offset_x = (width - total_width) / 2
        offset_y = (height - total_height) / 2
        
        # 绘制图层数据
        for i in range(self.row_num):
            for j in range(self.col_num):
                color_value = self.layer_array[i, j]
                if color_value > 0:  # 只绘制有颜色的点
                    # 创建QColor对象
                    if isinstance(color_value, int):
                        color_id = color_value
                    else:
                        color_id = int(color_value) if color_value.is_integer() else color_value
                    
                    # 确保颜色ID有效
                    color_id = int(color_id) % 16777216  # 24位颜色值范围
                    
                    # 将颜色ID转换为RGB值
                    r = (color_id >> 16) & 0xFF
                    g = (color_id >> 8) & 0xFF
                    b = color_id & 0xFF
                    
                    painter.setBrush(QBrush(QColor(r, g, b)))
                    painter.setPen(Qt.NoPen)
                    
                    # 绘制像素点（作为矩形），考虑缩放和居中
                    rect = QRectF(
                        offset_x + j * pixel_size,
                        offset_y + i * pixel_size,
                        max(1, pixel_size),  # 确保至少1像素宽
                        max(1, pixel_size)   # 确保至少1像素高
                    )
                    painter.drawRect(rect)
    
    def reset_zoom(self):
        """重置缩放比例为默认值"""
        self.zoom_factor = 1.0
        self.update()

class PatchLayout(QWidget):
    """Patch Layout UI component，支持scroll_content的Ctrl+滚轮缩放"""
    
    def __init__(self, vec_layers, color_list):
        self.vec_layers = self.load_layers(vec_layers)
        self.color_list = color_list
        self.patch = None
        super().__init__()
        
        # 缩放相关变量
        self.scroll_zoom_factor = 1.0  # scroll_content的初始缩放比例
        self.scroll_min_zoom = 0.5     # scroll_content的最小缩放比例
        self.scroll_max_zoom = 2.0     # scroll_content的最大缩放比例
        self.scroll_zoom_step = 0.1    # scroll_content的每次缩放步长
        self.original_item_size = 300  # 原始项目大小

        self._init_ui()
        
    def load_layers(self, vec_layers):
        layers = {layer.id: layer for layer in vec_layers.layers} if vec_layers else {}
        return layers
        
    def _init_ui(self):
        """Initialize UI components"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        
        # Title label
        title_label = QLabel("Patch Images")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        
        # 添加标题到主布局
        self.main_layout.addWidget(title_label)
        
        # 创建水平布局，用于并排显示两个组件
        content_layout = QHBoxLayout()
        
        # 左侧：组合图像显示组件（PatchImageWidget），占比0.2
        combined_title = QLabel("Patch Image")
        combined_title.setAlignment(Qt.AlignCenter)
        combined_title.setStyleSheet("font-weight: bold;")
        
        self.combined_widget = PatchImageWidget()
        
        combined_layout = QVBoxLayout()
        combined_layout.addWidget(combined_title)
        combined_layout.addWidget(self.combined_widget, 1)
        
        combined_container = QWidget()
        combined_container.setLayout(combined_layout)
        
        # 添加组合图像到水平布局，占比0.2
        content_layout.addWidget(combined_container, 2)  # 2表示扩展系数
        
        # 右侧：单个图层显示区域（LayerImageWidget），占比0.8
        layers_title = QLabel("Patch Layer Images")
        layers_title.setAlignment(Qt.AlignCenter)
        layers_title.setStyleSheet("font-weight: bold;")
        
        # 创建滚动区域以支持大量图层
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 滚动区域内的容器widget
        self.scroll_content = QWidget()
        self.layers_layout = QGridLayout(self.scroll_content)  # 使用网格布局支持多行
        self.layers_layout.setHorizontalSpacing(10)  # 设置水平间距
        self.layers_layout.setVerticalSpacing(10)    # 设置垂直间距
        self.scroll_area.setWidget(self.scroll_content)
        
        # 创建右侧垂直布局
        right_layout = QVBoxLayout()
        right_layout.addWidget(layers_title)
        right_layout.addWidget(self.scroll_area, 1)
        
        right_container = QWidget()
        right_container.setLayout(right_layout)
        
        # 添加右侧布局到水平布局，占比0.8
        content_layout.addWidget(right_container, 8)  # 8表示扩展系数
        
        # 添加水平布局到主布局
        self.main_layout.addLayout(content_layout, 1)
        
        # 存储图层widget的字典
        self.layer_widgets = {}
        
        # 连接滚动区域的事件过滤器
        self.scroll_area.viewport().installEventFilter(self)
        self.image_dict = {}  # 存储当前的图像数据字典
        self.layer_containers = []  # 存储所有图层容器widget
        
    def eventFilter(self, obj, event):
        """事件过滤器，用于捕获scroll_area的滚轮事件"""
        # 检查是否是滚动区域的视口触发的滚轮事件
        if obj == self.scroll_area.viewport() and event.type() == event.Wheel:
            # 检查是否按下了Ctrl键
            if event.modifiers() == Qt.ControlModifier:
                # 获取滚轮方向
                delta = event.angleDelta().y()
                
                # 根据滚轮方向调整缩放比例
                if delta > 0:  # 滚轮向上，放大
                    self.scroll_zoom_factor = min(self.scroll_zoom_factor + self.scroll_zoom_step, self.scroll_max_zoom)
                else:  # 滚轮向下，缩小
                    self.scroll_zoom_factor = max(self.scroll_zoom_factor - self.scroll_zoom_step, self.scroll_min_zoom)
                
                # 应用缩放
                self.apply_scroll_zoom()
                
                # 阻止事件继续传播
                return True
        
        # 对于其他事件，调用父类的事件过滤器
        return super().eventFilter(obj, event)
        
    def apply_scroll_zoom(self):
        """应用缩放比例到scroll_content中的所有图层组件"""
        # 计算新的项目大小
        new_item_size = int(self.original_item_size * self.scroll_zoom_factor)
        
        # 更新每个图层容器的大小
        for container in self.layer_containers:
            # 获取容器内的布局
            layout = container.layout()
            if layout and layout.count() > 1:
                # 获取图像widget
                image_widget = layout.itemAt(1).widget()
                if image_widget:
                    # 设置新的最小尺寸
                    image_widget.setMinimumSize(new_item_size, new_item_size)
                    
        # 更新布局
        self.scroll_content.updateGeometry()
        self.scroll_area.update()
        
    def reset_scroll_zoom(self):
        """重置scroll_content的缩放比例为默认值"""
        self.scroll_zoom_factor = 1.0
        
        # 恢复每个图层容器的原始大小
        for container in self.layer_containers:
            # 获取容器内的布局
            layout = container.layout()
            if layout and layout.count() > 1:
                # 获取图像widget
                image_widget = layout.itemAt(1).widget()
                if image_widget:
                    # 恢复原始最小尺寸
                    image_widget.setMinimumSize(self.original_item_size, self.original_item_size)
        
        self.scroll_content.updateGeometry()
        self.scroll_area.update()
        
    def update_patch(self, patch): 
        import numpy 
          
        def align_data(row, col):
            return (row-patch.row_min, col-patch.col_min)
        
        # 初始化图像字典（修正拼写错误）
        image_dict = {}
        
        row_num, col_num = patch.row_max-patch.row_min, patch.col_max-patch.col_min

        for layer in patch.patch_layer:
            for net in layer.nets:
                for wire in net.wires:    
                    for path in wire.paths:
                        if path.node1.layer == path.node2.layer:
                            layer_id = path.node1.layer
                            
                            color = self.color_list[layer_id % len(self.color_list)]
                            # 将QColor转换为RGB整数值
                            color_value = (color.red() << 16) | (color.green() << 8) | color.blue()
                            
                            row1, col1 = align_data(path.node1.row, path.node1.col)
                            row2, col2 = align_data(path.node2.row, path.node2.col)
                            
                            layer_array = image_dict.get(layer_id, None)
                            if layer_array is None:
                                layer_array = numpy.zeros((row_num, col_num))
                                image_dict[layer_id] = layer_array
                            layer_array[min(row1,row2) : max(row1,row2)+1, min(col1, col2) : max(col1, col2)+1] = color_value
                            
                        else:
                            # via data
                            row, col = (path.node1.col-patch.col_min, path.node1.row-patch.row_min)
                            
                            for layer_id in [path.node1.layer, (path.node1.layer+path.node2.layer)/2, path.node2.layer]:
                                color = self.color_list[layer_id % len(self.color_list)]
                                # 将QColor转换为RGB整数值
                                color_value = (color.red() << 16) | (color.green() << 8) | color.blue()
                                
                                layer_array = image_dict.get(layer_id, None)
                                if layer_array is None:
                                    layer_array = numpy.zeros((row_num, col_num))
                                    image_dict[layer_id] = layer_array
                                
                                layer_array[row, col] = color_value
                                
        # 存储当前的patch数据和图像数据
        self.patch = patch
        self.image_dict = image_dict
        
        # 为组合图像组件设置数据
        if hasattr(self, 'combined_widget'):
            self.combined_widget.set_image_data(image_dict, row_num, col_num)
        
        # 清理现有的图层widget
        for widget in self.layer_widgets.values():
            widget.setParent(None)
        self.layer_widgets.clear()
        
        # 移除布局中的所有项
        while self.layers_layout.count() > 0:
            item = self.layers_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # 为每个图层创建显示组件
        if image_dict:
            # 计算网格布局的行列（每行显示4个图层，可根据需要调整）
            max_columns = 4
            index = 0
            
            for layer_id, layer_array in image_dict.items():
                # 创建图层图像widget
                layer_widget = LayerImageWidget(layer_id)
                
                # 设置LayerImageWidget为正方形，大小为row_num和col_num的倍数
                # 计算合适的正方形尺寸（基于原始项目大小和行列数的倍数）
                base_size = self.original_item_size
                # 确保尺寸是row_num和col_num的公倍数
                # 找到row_num和col_num的最小公倍数
                def lcm(a, b):
                    import math
                    return a * b // math.gcd(a, b)
                
                if row_num > 0 and col_num > 0:
                    min_size = lcm(int(row_num), int(col_num))
                    # 确保正方形尺寸至少为base_size，并且是min_size的倍数
                    square_size = max(base_size, ((base_size + min_size - 1) // min_size) * min_size)
                else:
                    square_size = base_size
                
                # 创建图层标题
                layer_title = QLabel(self.vec_layers[layer_id].name)
                layer_title.setStyleSheet("font-weight: bold;")
                layer_title.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
                layer_title.setFixedWidth(square_size)  # 设置与layer_widget相同的宽度，确保对齐
                
                # 设置固定的正方形尺寸
                layer_widget.setFixedSize(square_size, square_size)
                
                # 创建垂直布局放置标题和图像
                layer_layout = QVBoxLayout()
                # 设置布局的内容边距和间距，确保标题和图像精确对齐
                layer_layout.setContentsMargins(0, 0, 0, 0)
                layer_layout.setSpacing(0)  # 设置布局项之间的间距为0
                # 添加标题和图像到布局，确保水平和垂直居中对齐
                layer_layout.addWidget(layer_title, alignment=Qt.AlignHCenter | Qt.AlignVCenter | Qt.AlignBottom)
                layer_layout.addWidget(layer_widget, 1, alignment=Qt.AlignHCenter | Qt.AlignVCenter | Qt.AlignTop)  # 让图像占据剩余空间，并确保垂直居中
                
                # 创建容器widget放置布局
                container = QWidget()
                container.setLayout(layer_layout)
                
                # 计算网格位置
                row = index // max_columns
                col = index % max_columns
                
                # 添加到网格布局
                self.layers_layout.addWidget(container, row, col)
                
                # 存储widget引用
                self.layer_widgets[layer_id] = layer_widget
                
                # 存储容器引用
                self.layer_containers.append(container)
                
                # 设置图层数据
                layer_widget.set_layer_data(layer_array, row_num, col_num)
                
                index += 1
        else:
            # 如果没有图层数据，显示空消息
            empty_label = QLabel("No layer data available")
            empty_label.setAlignment(Qt.AlignCenter)
            # 添加到网格布局的中心位置
            self.layers_layout.addWidget(empty_label, 0, 0)
            self.layers_layout.setAlignment(empty_label, Qt.AlignCenter)