# -*- encoding: utf-8 -*-

import sys
import concurrent.futures
from typing import List, Dict, Optional, Tuple

from PyQt5.QtWidgets import (
    QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsLineItem,
    QGraphicsItemGroup, QGraphicsTextItem, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QComboBox, QPushButton
)
from PyQt5.QtGui import QPen, QBrush, QColor, QFont, QPainter
from PyQt5.QtCore import Qt, QRectF, QPointF, QThreadPool, QRunnable, pyqtSignal, QObject

from ..data import DataVectors
from ..workspace import Workspace
from .basic import ZoomableGraphicsView


class WorkerSignals(QObject):
    """定义工作线程的信号"""
    instances_data = pyqtSignal(list)
    nets_data = pyqtSignal(dict)
    io_pins_data = pyqtSignal(list)


class InstancesWorker(QRunnable):
    """创建实例数据的工作线程 - 不创建GUI元素"""
    def __init__(self, instances, color_list, text_color):
        super().__init__()
        self.instances = instances.instances
        self.color_list = color_list
        self.text_color = text_color
        self.signals = WorkerSignals()
        
    def run(self):
        result_data = []
        for instance in self.instances:
            # 检查实例是否具有必要的属性
            if not all(hasattr(instance, attr) for attr in ['llx', 'lly', 'width', 'height']):
                continue
            
            # 只收集数据，不创建GUI元素
            instance_data = {
                'llx': instance.llx,
                'lly': instance.lly,
                'width': instance.width,
                'height': instance.height,
                'color': self.color_list[None],
                'name': getattr(instance, 'name', None),
                'text_color': self.text_color
            }
            
            result_data.append(instance_data)
        
        # 发送完成信号，传递收集的数据列表
        self.signals.instances_data.emit(result_data)


class NetsWorker(QRunnable):
    """创建线网数据的工作线程 - 不创建GUI元素"""
    def __init__(self, nets, wire_node_color, color_list, layer_visibility=None):
        super().__init__()
        self.nets = nets
        self.wire_node_color = wire_node_color
        self.color_list = color_list
        self.layer_visibility = layer_visibility
        self.signals = WorkerSignals()
        
    def run(self):
        result_data = {}
        
        # 遍历所有线网
        for net in self.nets:
            # 遍历线网中的所有导线
            for wire in net.wires:
                # 绘制导线节点
                wire_nodes = wire.wire
                
                # 节点1数据
                if wire_nodes.node1.pin_id is not None and wire_nodes.node1.pin_id >= 0:
                    node1_color = self.wire_node_color["pin_node"]
                else:
                    node1_color = self.wire_node_color["wire_node"]
                
                node1_data = {
                    'x': wire_nodes.node1.real_x,
                    'y': wire_nodes.node1.real_y,
                    'color': node1_color
                }
                
                # 将节点添加到特殊层，以便管理
                if "nodes" not in result_data:
                    result_data["nodes"] = []
                result_data["nodes"].append(node1_data)
                
                # 节点2数据
                if wire_nodes.node2.pin_id is not None and wire_nodes.node2.pin_id >= 0:
                    node2_color = self.wire_node_color["pin_node"]
                else:
                    node2_color = self.wire_node_color["wire_node"]
                
                node2_data = {
                    'x': wire_nodes.node2.real_x,
                    'y': wire_nodes.node2.real_y,
                    'color': node2_color
                }
                result_data["nodes"].append(node2_data)
                
                # 绘制路径
                for path in wire.paths:
                    if path.node1.layer == path.node2.layer:
                        layer_id = path.node1.layer
                        
                        # 初始化该层的列表（如果不存在）
                        if layer_id not in result_data:
                            result_data[layer_id] = []
                        
                        color_id = layer_id % len(self.color_list)
                        color = self.color_list[color_id]
                        
                        path_data = {
                            'x1': path.node1.real_x,
                            'y1': path.node1.real_y,
                            'x2': path.node2.real_x,
                            'y2': path.node2.real_y,
                            'color': color
                        }
                        
                        # 存储项目数据
                        result_data[layer_id].append(path_data)
        
        # 发送完成信号，传递创建的数据字典
        self.signals.nets_data.emit(result_data)


class IOPinsWorker(QRunnable):
    """创建IO引脚数据的工作线程 - 不创建GUI元素"""
    def __init__(self, io_pins, io_pin_color, text_color):
        super().__init__()
        self.io_pins = io_pins
        self.io_pin_color = io_pin_color
        self.text_color = text_color
        self.signals = WorkerSignals()
        
    def run(self):
        result_data = []
        
        for pin in self.io_pins:
            # 检查引脚是否具有必要的属性
            if not all(hasattr(pin, attr) for attr in ['llx', 'lly', 'width', 'height']):
                continue
            
            # 只收集数据，不创建GUI元素
            pin_data = {
                'llx': pin.llx,
                'lly': pin.lly,
                'width': pin.width,
                'height': pin.height,
                'color': self.io_pin_color,
                'name': getattr(pin, 'name', None),
                'text_color': self.text_color
            }
            
            result_data.append(pin_data)
        
        # 发送完成信号，传递收集的数据列表
        self.signals.io_pins_data.emit(result_data)


class ChipLayout(QWidget):
    """基于Qt的芯片布局显示窗口小部件，将实例、线网和IO引脚显示为矩形
    
    此窗口小部件提供了芯片布局数据的视觉表示，包括实例、
    线网和IO引脚。它支持缩放、平移和切换不同
    布局元素的可见性。
    
    属性:
        vec_cells: 单元的数据向量
        instances: 实例数据
        nets: 线网数据
        io_pins: IO引脚数据
        show_instances: 显示/隐藏实例的标志
        show_nets: 显示/隐藏线网的标志
        show_io_pins: 显示/隐藏IO引脚的标志
        net_opacity: 线网显示的不透明度级别
        scene: 用于绘图的QGraphicsScene
        view: 自定义ZoomableGraphicsView
        status_bar: 用于坐标显示的状态栏小部件
        coord_label: 用于显示当前坐标的标签
        layer_items: 将层ID映射到这些层的图形项列表的字典
        thread_pool: Qt线程池，用于并行处理
    """
    
    def __init__(self, vec_cells, vec_instances, vec_nets, color_list, parent: Optional[QWidget] = None):
        """初始化ChipLayout窗口小部件
        
        参数:
            vec_cells: 单元的数据向量
            vec_instances: 实例数据
            vec_nets: 线网数据
            color_list: 不同单元类型的颜色列表
            parent: 父窗口小部件（可选）
        """
        super().__init__(parent)
        self.vec_cells = vec_cells
        self.instances = vec_instances
        self.nets = vec_nets

        self.io_pins = []
        
        # 显示选项
        self.show_instances = True
        self.show_nets = True
        self.show_io_pins = True
        self.net_opacity = 0.5
        
        # 颜色
        self.net_color = QColor(0, 250, 0)  # 带透明度的蓝色
        self.io_pin_color = QColor(255, 0, 0, 200)  # IO引脚的红色
        self.wire_node_color = {"wire_node": QColor(0, 200, 0), "pin_node": QColor(200, 0, 0)}
        self.text_color = QColor(0, 0, 0)
        self.color_list = color_list
        
        # 所选线网矩形
        self.selected_net_rect = None

        # 用于高效可见性管理的按层ID存储图形项的字典
        self.layer_items = {}
        
        # 初始化线程池
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(8)  # 设置最大线程数

        # 初始化UI
        self.init_ui()
        self.draw_layout(True)
    
    def init_ui(self):
        """初始化UI组件，包括场景、视图和状态栏
        
        设置主布局，创建QGraphicsScene和ZoomableGraphicsView，
        并添加用于显示坐标的状态栏。
        """
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # 创建QGraphicsScene和自定义ZoomableGraphicsView
        self.scene = QGraphicsScene()
        self.view = ZoomableGraphicsView(self.scene, self)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        
        # 将视图添加到主布局
        main_layout.addWidget(self.view)
        
        # 在底部创建状态栏
        self.status_bar = QWidget()
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(5, 2, 5, 2)
        
        # 左侧为未来状态消息保留的空白空间
        status_layout.addStretch(1)
        
        # 右侧坐标显示
        self.coord_label = QLabel("X: 0.00, Y: 0.00")
        self.coord_label.setStyleSheet("background-color: #f0f0f0; padding: 2px 5px;")
        self.coord_label.setMinimumWidth(150)
        self.coord_label.setAlignment(Qt.AlignRight)
        status_layout.addWidget(self.coord_label)
        
        # 将状态栏添加到主布局
        main_layout.addWidget(self.status_bar)
        
        self.setLayout(main_layout)
        self.setWindowTitle("Chip Layout Display")
        self.resize(1000, 800)

    def draw_layout(self, fit_view=False):
        """绘制芯片布局元素
        
        清除场景并根据当前显示设置绘制实例、线网和IO引脚。
        可选地使视图适合场景。
        
        参数:
            fit_view: 绘制后是否使视图适合整个场景
        """
        self.scene.clear()
        self.layer_items = {}  # 重置层项字典
        
        # 添加任务计数器和标志来跟踪并行任务完成情况
        self._pending_tasks = 0
        self._should_fit_view = fit_view
        
        # 使用线程池并行处理数据
        if self.show_instances:
            self._pending_tasks += 1
            self._draw_instances_parallel()
        
        if self.show_nets:
            self._pending_tasks += 1
            self._draw_nets_parallel()
        
        if self.show_io_pins:
            self._pending_tasks += 1
            self._draw_io_pins_parallel()
        
        # 如果没有待处理任务但仍需适应视图
        if self._pending_tasks == 0 and self._should_fit_view:
            self.fit_view()
            
    def _task_completed(self):
        """标记一个任务完成，并检查是否所有任务都已完成"""
        self._pending_tasks -= 1
        if self._pending_tasks == 0 and self._should_fit_view:
            self.fit_view()

    def _draw_instances_parallel(self):
        """并行处理实例数据"""
        worker = InstancesWorker(self.instances, self.color_list, self.text_color)
        worker.signals.instances_data.connect(self._on_instances_data)
        self.thread_pool.start(worker)
    
    def _on_instances_data(self, instances_data):
        """处理实例数据完成的回调 - 在主线程中创建GUI元素"""
        for instance_info in instances_data:
            # 在主线程中创建矩形项
            rect_item = QGraphicsRectItem(
                instance_info['llx'], instance_info['lly'], 
                instance_info['width'], instance_info['height']
            )
            
            # 设置基于单元类型的颜色
            rect_item.setBrush(QBrush(instance_info['color'], Qt.Dense6Pattern))
            rect_item.setPen(QPen(QColor(0, 0, 0), 10))  # 黑色边框
            
            # 可选地添加实例名称（如果可用）
            if instance_info['name']:
                # 仅为较大的实例添加文本以避免混乱
                if instance_info['width'] > 1000 and instance_info['height'] > 1000:
                    text_item = QGraphicsTextItem(instance_info['name'], rect_item)
                    text_item.setPos(instance_info['llx'] + 5, instance_info['lly'] + 5)
                    text_item.setScale(0.5)
                    text_item.setDefaultTextColor(instance_info['text_color'])
            
            self.scene.addItem(rect_item)
        
        # 标记任务完成
        self._task_completed()
    
    def _draw_nets_parallel(self):
        """并行处理线网数据"""
        layer_visibility = getattr(self, 'layer_visibility', None)
        worker = NetsWorker(self.nets, self.wire_node_color, self.color_list, layer_visibility)
        worker.signals.nets_data.connect(self._on_nets_data)
        self.thread_pool.start(worker)
    
    def _on_nets_data(self, nets_data):
        """处理线网数据完成的回调 - 在主线程中创建GUI元素"""
        # 存储层项并根据可见性添加到场景
        for layer_id, items_data in nets_data.items():
            self.layer_items[layer_id] = []
            
            # 根据数据创建GUI元素
            for item_data in items_data:
                if layer_id == "nodes":
                    # 创建节点矩形
                    rect_item = QGraphicsRectItem(
                        item_data['x']-25, item_data['y']-25, 50, 50
                    )
                    rect_item.setBrush(QBrush(item_data['color']))
                    rect_item.setPen(QPen(item_data['color'], 1.0))
                    self.layer_items[layer_id].append(rect_item)
                else:
                    # 创建导线
                    wire_pen = QPen(item_data['color'], 30)
                    line_item = QGraphicsLineItem(
                        item_data['x1'], item_data['y1'],
                        item_data['x2'], item_data['y2']
                    )
                    line_item.setPen(wire_pen)
                    self.layer_items[layer_id].append(line_item)
            
            # 添加到场景
            # 节点层始终显示
            if layer_id == "nodes":
                for item in self.layer_items[layer_id]:
                    self.scene.addItem(item)
            else:
                # 其他层根据可见性设置
                should_add_to_scene = True
                if hasattr(self, 'layer_visibility') and layer_id in self.layer_visibility:
                    should_add_to_scene = self.layer_visibility[layer_id]
                
                if should_add_to_scene:
                    for item in self.layer_items[layer_id]:
                        self.scene.addItem(item)
        
        # 标记任务完成
        self._task_completed()
    
    def _draw_io_pins_parallel(self):
        """并行处理IO引脚数据"""
        worker = IOPinsWorker(self.io_pins, self.io_pin_color, self.text_color)
        worker.signals.io_pins_data.connect(self._on_io_pins_data)
        self.thread_pool.start(worker)
    
    def _on_io_pins_data(self, io_pins_data):
        """处理IO引脚数据完成的回调 - 在主线程中创建GUI元素"""
        for pin_info in io_pins_data:
            # 在主线程中创建矩形项
            rect_item = QGraphicsRectItem(
                pin_info['llx'], pin_info['lly'], 
                pin_info['width'], pin_info['height']
            )
            
            # 设置IO引脚的颜色
            rect_item.setBrush(QBrush(pin_info['color']))
            rect_item.setPen(QPen(QColor(0, 0, 0), 10))  # 黑色边框
            
            # 如果可用，添加引脚名称
            if pin_info['name']:
                pin_name = pin_info['name'].split('/')[-1] if '/' in pin_info['name'] else pin_info['name']
                text_item = QGraphicsTextItem(pin_name, rect_item)
                text_item.setPos(pin_info['llx'] + 5, pin_info['lly'] + 5)
                text_item.setScale(0.5)
                text_item.setDefaultTextColor(pin_info['text_color'])
            
            self.scene.addItem(rect_item)
        
        # 标记任务完成
        self._task_completed()
    
    def toggle_instances(self, index):
        """切换实例的显示
        
        参数:
            index: 0表示显示实例，其他值表示隐藏
        """
        self.show_instances = (index == 0)
        self.draw_layout()
    
    def toggle_nets(self, index):
        """切换线网的显示
        
        参数:
            index: 0表示显示线网，其他值表示隐藏
        """
        self.show_nets = (index == 0)
        self.draw_layout()
    
    def toggle_io_pins(self, index):
        """切换IO引脚的显示
        
        参数:
            index: 0表示显示IO引脚，其他值表示隐藏
        """
        self.show_io_pins = (index == 0)
        self.draw_layout()
    
    def zoom_in(self):
        """放大视图，以场景坐标中的鼠标位置为中心"""
        # 缩放视图
        self.view.scale(1.2, 1.2)
    
    def zoom_out(self):
        """缩小视图，以场景坐标中的鼠标位置为中心"""
        # 缩放视图
        self.view.scale(0.8, 0.8)
    
    def fit_view(self):
        """使视图适合整个场景"""
        if not self.scene.items():
            return
        
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        
    def update_coord_status(self, coord_text):
        """更新底部状态栏中的坐标状态显示
        
        参数:
            coord_text: 要在坐标标签中显示的文本
        """
        self.coord_label.setText(coord_text)
        
    def on_net_selected(self, selected_net):
        """处理所选线网的槽函数，绘制边界矩形
        
        在所选线网周围创建红色虚线矩形，并调整视图
        以显示带有一些填充的整个所选线网。
        
        参数:
            selected_net: 所选的线网
        """
        # 检查所选线网是否具有feature属性
        if hasattr(selected_net, 'feature') and selected_net.feature:
            feature = selected_net.feature
            
            # 检查feature是否具有必要的几何属性
            if all(hasattr(feature, attr) for attr in ['llx', 'lly', 'width', 'height']):
                # 创建白色边框矩形
                pen = QPen(QColor(200, 0, 0), 40)
                pen.setStyle(Qt.DashLine)
                
                # 创建矩形项
                if self.selected_net_rect is not None:
                    self.selected_net_rect.setRect(
                        feature.llx-100, feature.lly-100, 
                        feature.width+200, feature.height+200
                    )
                else:
                    self.selected_net_rect = QGraphicsRectItem(
                        feature.llx-100, feature.lly-100, 
                        feature.width+200, feature.height+200
                    )
                
                    # 设置矩形样式
                    self.selected_net_rect.setPen(pen)
                    self.selected_net_rect.setBrush(QBrush(Qt.NoBrush))  # 无填充
                    
                    # 将矩形添加到场景
                    self.scene.addItem(self.selected_net_rect)
                    
                    # 将矩形带到顶层以确保可见性
                    self.selected_net_rect.setZValue(100)  # 设置高z值
                
                # 自动调整视图以显示整个选定的线网矩形
                self.view.fitInView(self.selected_net_rect, Qt.KeepAspectRatio)
                # 稍微缩小以在线选矩形周围留出一些空间
                self.view.scale(0.6, 0.6)

    def update_layer_visibility(self):
        """根据当前layer_visibility设置更新项目的可见性
        
        此方法比重新绘制整个布局更高效，因为它只
        显示或隐藏现有项目，而不是重新创建它们。
        """
        if not hasattr(self, 'layer_visibility'):
            return
        
        # 更新所有层项目的可见性
        for layer_id, items in self.layer_items.items():
            # 节点层始终显示
            if layer_id == "nodes":
                continue
                
            # 检查是否控制此层的可见性
            if layer_id in self.layer_visibility:
                is_visible = self.layer_visibility[layer_id]
                
                for item in items:
                    # 检查项目是否已经在场景中
                    is_in_scene = item.scene() is not None
                    
                    if is_visible and not is_in_scene:
                        # 如果层可见且不在场景中，则添加到场景
                        self.scene.addItem(item)
                    elif not is_visible and is_in_scene:
                        # 如果层隐藏且在场景中，则从场景中移除
                        self.scene.removeItem(item)

    def resizeEvent(self, event):
        """处理调整大小事件以保持视图拟合
        
        确保当窗口小部件调整大小时，视图保持正确拟合到场景。
        
        参数:
            event: 调整大小事件对象
        """
        # 调用基类调整大小事件
        super().resizeEvent(event)
        
        # 强制视图适合场景
        self.fit_view()