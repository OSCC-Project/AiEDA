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
    """Define signals for worker threads"""
    instances_data = pyqtSignal(list)
    nets_data = pyqtSignal(dict)
    io_pins_data = pyqtSignal(list)


class InstancesWorker(QRunnable):
    """Worker thread for creating instance data - Does not create GUI elements"""
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
    """Worker thread for creating net data - Does not create GUI elements"""
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
    """Worker thread for creating IO pins data - Does not create GUI elements"""
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
        self.io_pin_color = QColor(255, 0, 0, 200)  # Red for IO pins
        self.wire_node_color = {"wire_node": QColor(0, 200, 0), "pin_node": QColor(200, 0, 0)}
        self.text_color = QColor(0, 0, 0)
        self.color_list = color_list
        
        # Selected net rectangle
        self.selected_net_rect = None

        # Dictionary to store graphic items by layer ID for efficient visibility management
        self.layer_items = {}
        
        # Initialize thread pool
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(8)  # Set maximum thread count

        # Initialize UI
        self.init_ui()
        self.draw_layout(True)
    
    def init_ui(self):
        """Initialize UI components including scene, view and status bar
        
        Set up main layout, create QGraphicsScene and ZoomableGraphicsView,
        and add a status bar for displaying coordinates.
        """
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create QGraphicsScene and custom ZoomableGraphicsView
        self.scene = QGraphicsScene()
        self.view = ZoomableGraphicsView(self.scene, self)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        
        # Add view to main layout
        main_layout.addWidget(self.view)
        
        # Create status bar at the bottom
        self.status_bar = QWidget()
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(5, 2, 5, 2)
        
        # Left side empty space reserved for future status messages
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
        self.setWindowTitle("Chip Layout Display")
        self.resize(1000, 800)

    def draw_layout(self, fit_view=False):
        """Draw chip layout elements
        
        Clear the scene and draw instances, nets and IO pins according to current display settings.
        Optionally fit the view to the scene.
        
        Parameters:
            fit_view: Whether to fit the view to the entire scene after drawing
        """
        self.scene.clear()
        self.layer_items = {}  # Reset layer items dictionary
        
        # Add task counter and flag to track parallel task completion
        self._pending_tasks = 0
        self._should_fit_view = fit_view
        
        # Use thread pool to process data in parallel
        if self.show_instances:
            self._pending_tasks += 1
            self._draw_instances_parallel()
        
        if self.show_nets:
            self._pending_tasks += 1
            self._draw_nets_parallel()
        
        if self.show_io_pins:
            self._pending_tasks += 1
            self._draw_io_pins_parallel()
        
        # If no pending tasks but still need to fit view
        if self._pending_tasks == 0 and self._should_fit_view:
            self.fit_view()
            
    def _task_completed(self):
        """Mark a task as completed and check if all tasks are done"""
        self._pending_tasks -= 1
        if self._pending_tasks == 0 and self._should_fit_view:
            self.fit_view()

    def _draw_instances_parallel(self):
        """Process instance data in parallel"""
        worker = InstancesWorker(self.instances, self.color_list, self.text_color)
        worker.signals.instances_data.connect(self._on_instances_data)
        self.thread_pool.start(worker)
    
    def _on_instances_data(self, instances_data):
        """Callback for instance data completion - create GUI elements in main thread"""
        for instance_info in instances_data:
            # Create rectangle items in main thread
            rect_item = QGraphicsRectItem(
                instance_info['llx'], instance_info['lly'], 
                instance_info['width'], instance_info['height']
            )
            
            # Set color based on cell type
            rect_item.setBrush(QBrush(instance_info['color'], Qt.Dense6Pattern))# Black border
            rect_item.setPen(QPen(QColor(0, 0, 0), 10))  # Black border
            
            # Optionally add instance name if available
            if instance_info['name']:
                # Only add text for larger instances to avoid clutter
                if instance_info['width'] > 1000 and instance_info['height'] > 1000:
                    text_item = QGraphicsTextItem(instance_info['name'], rect_item)
                    text_item.setPos(instance_info['llx'] + 5, instance_info['lly'] + 5)
                    text_item.setScale(0.5)
                    text_item.setDefaultTextColor(instance_info['text_color'])
            
            self.scene.addItem(rect_item)
        
        # Mark task as completed
        self._task_completed()
    
    def _draw_nets_parallel(self):
        """Process net data in parallel"""
        layer_visibility = getattr(self, 'layer_visibility', None)
        worker = NetsWorker(self.nets, self.wire_node_color, self.color_list, layer_visibility)
        worker.signals.nets_data.connect(self._on_nets_data)
        self.thread_pool.start(worker)
    
    def _on_nets_data(self, nets_data):
        """Callback for net data completion - create GUI elements in main thread"""
        # Store layer items and add to scene based on visibility
        for layer_id, items_data in nets_data.items():
            self.layer_items[layer_id] = []
            
            # Create GUI elements based on data
            for item_data in items_data:
                if layer_id == "nodes":
                    # Create node rectangles
                    rect_item = QGraphicsRectItem(
                        item_data['x']-25, item_data['y']-25, 50, 50
                    )
                    rect_item.setBrush(QBrush(item_data['color']))
                    rect_item.setPen(QPen(item_data['color'], 1.0))
                    self.layer_items[layer_id].append(rect_item)
                else:
                    # Create wires
                    wire_pen = QPen(item_data['color'], 30)
                    line_item = QGraphicsLineItem(
                        item_data['x1'], item_data['y1'],
                        item_data['x2'], item_data['y2']
                    )
                    line_item.setPen(wire_pen)
                    self.layer_items[layer_id].append(line_item)
            
            # Add to scene
            # Node layer is always visible
            if layer_id == "nodes":
                for item in self.layer_items[layer_id]:
                    self.scene.addItem(item)
            else:
                # Other layers based on visibility settings
                should_add_to_scene = True
                if hasattr(self, 'layer_visibility') and layer_id in self.layer_visibility:
                    should_add_to_scene = self.layer_visibility[layer_id]
                
                if should_add_to_scene:
                    for item in self.layer_items[layer_id]:
                        self.scene.addItem(item)
        
        # Mark task as completed
        self._task_completed()
    
    def _draw_io_pins_parallel(self):
        """Process IO pins data in parallel"""
        worker = IOPinsWorker(self.io_pins, self.io_pin_color, self.text_color)
        worker.signals.io_pins_data.connect(self._on_io_pins_data)
        self.thread_pool.start(worker)
    
    def _on_io_pins_data(self, io_pins_data):
        """Callback for IO pins data completion - create GUI elements in main thread"""
        for pin_info in io_pins_data:
            # Create rectangle items in main thread
            rect_item = QGraphicsRectItem(
                pin_info['llx'], pin_info['lly'], 
                pin_info['width'], pin_info['height']
            )
            
            # Set color for IO pins
            rect_item.setBrush(QBrush(pin_info['color']))# Black border
            rect_item.setPen(QPen(QColor(0, 0, 0), 10))  # Black border
            
            # Add pin name if available
            if pin_info['name']:
                pin_name = pin_info['name'].split('/')[-1] if '/' in pin_info['name'] else pin_info['name']
                text_item = QGraphicsTextItem(pin_name, rect_item)
                text_item.setPos(pin_info['llx'] + 5, pin_info['lly'] + 5)
                text_item.setScale(0.5)
                text_item.setDefaultTextColor(pin_info['text_color'])
            
            self.scene.addItem(rect_item)
        
        # Mark task as completed
        self._task_completed()
    
    def toggle_instances(self, index):
        """Toggle display of instances
        
        Parameters:
            index: 0 to show instances, other values to hide
        """
        self.show_instances = (index == 0)
        self.draw_layout()
    
    def toggle_nets(self, index):
        """Toggle display of nets
        
        Parameters:
            index: 0 to show nets, other values to hide
        """
        self.show_nets = (index == 0)
        self.draw_layout()
    
    def toggle_io_pins(self, index):
        """Toggle display of IO pins
        
        Parameters:
            index: 0 to show IO pins, other values to hide
        """
        self.show_io_pins = (index == 0)
        self.draw_layout()
    
    def zoom_in(self):
        """Zoom in on the view, centered on the mouse position in scene coordinates"""
        # Scale the view
        self.view.scale(1.2, 1.2)
    
    def zoom_out(self):
        """Zoom out from the view, centered on the mouse position in scene coordinates"""
        # Scale the view
        self.view.scale(0.8, 0.8)
    
    def fit_view(self):
        """Fit the view to the entire scene"""
        if not self.scene.items():
            return
        
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        
    def update_coord_status(self, coord_text):
        """Update the coordinate status display in the bottom status bar
        
        Parameters:
            coord_text: Text to display in the coordinate label
        """
        self.coord_label.setText(coord_text)
        
    def on_net_selected(self, selected_net):
        """Slot function to handle selected nets, drawing bounding rectangles
        
        Create a red dashed rectangle around the selected net and adjust the view
        to display the entire selected net with some padding.
        
        Parameters:
            selected_net: The selected net
        """
        # Check if the selected net has a feature attribute
        if hasattr(selected_net, 'feature') and selected_net.feature:
            feature = selected_net.feature
            
            # Check if the feature has necessary geometric properties
            if all(hasattr(feature, attr) for attr in ['llx', 'lly', 'width', 'height']):
                # Create white border rectangle
                pen = QPen(QColor(200, 0, 0), 40)
                pen.setStyle(Qt.DashLine)
                
                # Create rectangle item
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
                
                    # Set rectangle style
                    self.selected_net_rect.setPen(pen)
                    self.selected_net_rect.setBrush(QBrush(Qt.NoBrush))  # No fill
                    
                    # Add rectangle to scene
                    self.scene.addItem(self.selected_net_rect)
                    
                    # Bring rectangle to top to ensure visibility
                    self.selected_net_rect.setZValue(100)  # Set high z-value
                
                # Automatically adjust view to show entire selected net rectangle
                self.view.fitInView(self.selected_net_rect, Qt.KeepAspectRatio)
                # Zoom out slightly to leave some space around the selected net rectangle
                self.view.scale(0.6, 0.6)

    def update_layer_visibility(self):
        """Update item visibility according to current layer_visibility settings
        
        This method is more efficient than redrawing the entire layout because it only
        shows or hides existing items, rather than recreating them.
        """
        if not hasattr(self, 'layer_visibility'):
            return
        
        # Update visibility of all layer items
        for layer_id, items in self.layer_items.items():
            # Node layer is always visible
            if layer_id == "nodes":
                continue
                
            # Check if visibility of this layer is controlled
            if layer_id in self.layer_visibility:
                is_visible = self.layer_visibility[layer_id]
                
                for item in items:
                    # Check if item is already in the scene
                    is_in_scene = item.scene() is not None
                    
                    if is_visible and not is_in_scene:
                        # If layer is visible and not in scene, add to scene
                        self.scene.addItem(item)
                    elif not is_visible and is_in_scene:
                        # If layer is hidden and in scene, remove from scene
                        self.scene.removeItem(item)

    def resizeEvent(self, event):
        """Handle resize events to maintain view fitting
        
        Ensure that the view remains properly fitted to the scene when the widget is resized.
        
        Parameters:
            event: Resize event object
        """
        # Call base class resize event
        super().resizeEvent(event)
        
        # Force view to fit scene
        self.fit_view()