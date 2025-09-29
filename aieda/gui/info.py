"""
@File : info.py
@Author : yell
@Desc : Infomation UI for AiEDA system
"""

import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QComboBox, QCheckBox, QTextEdit, QLineEdit
)
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QRectF

class WorkspaceInformation(QWidget):
    """Workspace information display component with text display and input functionality
    
    This class provides a UI component with a text display area and text input area
    in a 10:1 vertical ratio layout.
    
    Attributes:
        text_display (QTextEdit): Text display area for showing information
        text_input (QLineEdit): Text input area for user input
    """
    
    def __init__(self, workspace, parent=None):
        """Initialize the WorkspaceInformation component
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.workspace = workspace
        
        # Initialize UI components
        self.text_display = None
        self.text_input = None
        
        # Initialize the layout
        self.init_ui()
        
        self.load_workspace()
    
    def init_ui(self):
        """Initialize the UI components and layout"""
        # Create main vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create text display area (upper part) with scroll functionality
        self.text_display = QTextEdit("Select a workspace to see details")
        self.text_display.setReadOnly(True)  # Make it read-only
        self.text_display.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.text_display.setMinimumHeight(200)
        self.text_display.setStyleSheet("background-color: white; padding: 0px; border-radius: 4px;")
        self.text_display.setTextInteractionFlags(Qt.TextSelectableByMouse)  # Allow text selection
        self.text_display.setAcceptRichText(True)  # Keep rich text support
        
        # Create text input area (lower part)
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter information here...")
        self.text_input.setMinimumHeight(100)  # Increase input box height
        self.text_input.setAcceptRichText(False)  # Keep plain text for simplicity
        
        # Add widgets to layout with 10:1 ratio
        main_layout.addWidget(self.text_display, 8)  # 10 parts for display
        main_layout.addWidget(self.text_input, 2)    # 1 part for input
        
    def load_workspace(self):
        info_str = []
            
        info_str.append(f"<p><b>Design:</b> {self.workspace.design}</p>")
        info_str.append(f"<p><b>Directory:</b> {self.workspace.directory}</p>")
        
        info_str.append("<hr>")
        
        info_str.append(f"<p><b>Process node:</b> {self.workspace.configs.workspace.process_node}</p>")
        info_str.append(f"<p><b>version:</b> {self.workspace.configs.workspace.version}</p>")
        
        info_str.append("<hr>")
        
        info_str.append("<p><b>Flows:</b></p>")
        info_str.append("<table border='1' cellspacing='0' cellpadding='3' style='border-collapse:collapse;'>")
        info_str.append("<tr style='background-color:#f0f0f0;'>")
        info_str.append("<th style='width:150px;'>Step</th>")
        info_str.append("<th style='width:150px;'>EDA Tool</th>")
        info_str.append("<th style='width:150px;'>State</th>")
        info_str.append("<th style='width:150px;'>Runtime</th>")
        info_str.append("</tr>")
        
        for flow in self.workspace.configs.flows:
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
        # Use setHtml to properly render HTML content in QTextEdit
        self.text_display.setHtml('\n'.join(info_str))
        
    def on_net_selected(self, selected_net):
        def get_net_details(net):
            """Get detailed feature data of the net, excluding None values
            
            Args:
                net: Net object to retrieve details for
                
            Returns:
                Dictionary of net attributes with non-None values
            """
            details = {
                "name": net.name
            }
            
            # Check if net has feature attribute and it's not None
            if hasattr(net, 'feature') and net.feature:
                # Get all attributes of VectorNetFeature
                feature = net.feature
                feature_attrs = [
                    'llx', 'lly', 'urx', 'ury', 'wire_len', 'via_num', 'drc_num',
                    'R', 'C', 'power', 'delay', 'slew', 'aspect_ratio', 'width',
                    'height', 'area', 'l_ness', 'volume', 'layer_ratio'
                ]
                
                # Add all non-None attributes to details
                for attr in feature_attrs:
                    value = getattr(feature, attr, None)
                    if value is not None:
                        details[attr] = value
                
                # Special handling for drc_type list
                if hasattr(feature, 'drc_type') and feature.drc_type:
                    details['drc_type'] = ', '.join(feature.drc_type)
                
                # Process place_feature if it's not None
                if hasattr(feature, 'place_feature') and feature.place_feature:
                    place_feature = feature.place_feature
                    place_attrs = ['pin_num', 'aspect_ratio', 'width', 'height',
                                  'area', 'l_ness', 'rsmt', 'hpwl']
                    
                    for attr in place_attrs:
                        value = getattr(place_feature, attr, None)
                        if value is not None:
                            details[f'place_{attr}'] = value
            
            return details   
        
        def get_net_text(net_details):
            # Format detailed information into tooltip text
            net_text = f"Net: {net_details.get('name', 'Unknown')}\n\n" 
            
            # Add all detailed information
            for key, value in net_details.items():
                if key == 'name':
                    continue  # Skip name as it's already in the title
                    
                # Format key name to be more readable
                readable_key = key.replace('_', ' ').title()
                
                # Special handling for some value display formats
                if isinstance(value, list):
                    # For list type, display as comma-separated string
                    value_str = ', '.join(map(str, value))
                elif isinstance(value, float):
                    # For float numbers, limit decimal places
                    value_str = f"{value:.6f}"
                else:
                    value_str = str(value)
                
                net_text += f"{readable_key}: {value_str}\n"
                
            return net_text
        
        def build_html_text(net_details_text):
            """Append net details to the workspace information text display
            
            Args:
                net_details_text: The net details text to append
            """
            # 我们需要一种简单而可靠的方式来合并内容，避免复杂的HTML解析问题
            
            # 1. 首先获取当前的HTML内容
            current_html = self.text_display.toHtml()
            
            # 2. 格式化网络详情文本为HTML
            # 转义HTML特殊字符
            safe_details = net_details_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            # 保留换行
            safe_details = safe_details.replace('\n', '<br/>')
            
            # 3. 创建一个简单的HTML片段作为分隔线和网络详情
            net_details_html = f"<div style='margin-top: 20px; padding-top: 10px; border-top: 1px solid #ccc;'>"
            net_details_html += f"<h3>Net Details:</h3><p>{safe_details}</p></div>"
            
            # 4. 检查当前HTML是否包含完整的结构
            if '<body>' in current_html and '</body>' in current_html:
                # 如果是完整的HTML结构，在body结束标签前添加网络详情
                new_html = current_html.replace('</body>', net_details_html + '</body>')
            else:
                # 如果不是完整的HTML结构，创建一个新的完整HTML结构
                # 包含原有内容和网络详情
                new_html = "<!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML 4.0//EN' 'http://www.w3.org/TR/REC-html40/strict.dtd'>\n"
                new_html += "<html><head><meta name='qrichtext' content='1'/><style type='text/css'>\n"
                new_html += "p, li { white-space: pre-wrap; }\n"
                new_html += "</style></head><body style=' font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;'>\n"
                new_html += current_html
                new_html += "\n" + net_details_html
                new_html += "</body></html>"
            
            # 5. 设置更新后的HTML
            self.text_display.setHtml(new_html)    
            self.text_display.verticalScrollBar().setValue(
                self.text_display.verticalScrollBar().maximum()) 
        
        # Get detailed data of the net
        net_details = get_net_details(selected_net)
        net_text = get_net_text(net_details)
        build_html_text(net_text)