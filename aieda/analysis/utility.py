import os
import matplotlib.pyplot as plt


def save_fig(fig, output_path, **kwargs):
    """
    使用显式文件句柄的方式保存matplotlib图表，解决某些环境下fig.savefig失败的问题。
    
    Args:
        fig: matplotlib figure对象
        output_path: 输出文件路径
        **kwargs: 传递给fig.savefig的其他参数
        
    Returns:
        bool: 是否保存成功
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # 尝试使用标准方法保存
        fig.savefig(output_path, **kwargs)
        
        # 验证文件是否成功创建
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return True
        
        # 如果标准方法失败，使用显式文件句柄
        print(f"Standard savefig failed for {output_path}, trying workaround...")
        
        # 确定文件格式
        file_ext = os.path.splitext(output_path)[1].lower()
        if file_ext == '.png':
            format_type = 'png'
        elif file_ext == '.pdf':
            format_type = 'pdf'
        elif file_ext == '.svg':
            format_type = 'svg'
        else:
            # 默认使用png
            format_type = 'png'
            output_path = os.path.splitext(output_path)[0] + '.png'
        
        # 使用显式文件句柄保存
        with open(output_path, 'wb') as f:
            fig.savefig(f, format=format_type, **kwargs)
        
        # 再次验证文件是否成功创建
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"Successfully saved figure using workaround: {output_path}")
            return True
        else:
            print(f"Failed to save figure even with workaround: {output_path}")
            return False
            
    except Exception as e:
        print(f"Error saving figure: {str(e)}")
        return False