from PyQt5.QtGui import QColor

# 定义修改后的rgba_to_hex函数
def rgba_to_hex(color_value):
    # 如果color_value已经是字符串且符合格式，直接返回
    if isinstance(color_value, str):
        # 尝试解析已有的JSON格式字符串
        try:
            if '"r"' in color_value or '{r:' in color_value:
                return color_value
        except:
            pass
    
    try:
        # 如果是QColor对象，直接获取RGB值
        if hasattr(color_value, 'red') and hasattr(color_value, 'green') and hasattr(color_value, 'blue'):
            r = color_value.red() / 255.0
            g = color_value.green() / 255.0
            b = color_value.blue() / 255.0
            # 返回JSON字符串格式的颜色对象
            return '{"r": ' + str(round(r, 2)) + ', "g": ' + str(round(g, 2)) + ', "b": ' + str(round(b, 2)) + '}'
        # 尝试将颜色值作为整数处理
        elif isinstance(color_value, int):
            # 假设QColor的数值格式为0xRRGGBB
            # 提取RGB分量并归一化到0-1范围
            r = ((color_value >> 16) & 0xFF) / 255.0
            g = ((color_value >> 8) & 0xFF) / 255.0
            b = (color_value & 0xFF) / 255.0
            # 返回JSON字符串格式的颜色对象
            return '{"r": ' + str(round(r, 2)) + ', "g": ' + str(round(g, 2)) + ', "b": ' + str(round(b, 2)) + '}'
    except Exception as e:
        print(f"Error converting color: {e}")
        # 如果处理失败，返回默认颜色
        return '{"r": 1, "g": 0, "b": 0}'
    
    # 默认返回红色
    return '{"r": 1, "g": 0, "b": 0}'

# 测试函数
if __name__ == "__main__":
    # 创建一个QColor对象 (红色)
    color = QColor(255, 0, 0)
    result = rgba_to_hex(color)
    print(f"QColor(255, 0, 0) -> {result}")
    
    # 测试整数格式的颜色
    color_int = 0x00FF00  # 绿色
    result = rgba_to_hex(color_int)
    print(f"0x00FF00 (green) -> {result}")
    
    # 测试字符串格式的颜色
    color_str = '{"r": 0, "g": 0, "b": 1}'
    result = rgba_to_hex(color_str)
    print(f"'{color_str}' -> {result}")