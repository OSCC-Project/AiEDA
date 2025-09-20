#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : test_sky130_ppa_map.py
@Time : 2025/09/20 16:58:24
@Author : simin tao
@Version : 1.0
@Contact : taosm@pcl.ac.cn
@Desc : Read the patch json file and generate the layout map file.
'''

import os
import json
import numpy as np

map_type = "net_density"  # "power" or "timing" or "net_density"

def read_patch_net_density_matrix(patchs_dir):
    patch_info = []
    max_row = 0
    max_col = 0
    for fname in os.listdir(patchs_dir):
        if fname.endswith('.json'):
            with open(os.path.join(patchs_dir, fname), 'r') as f:
                data = json.load(f)
                row = data['patch_id_row']
                col = data['patch_id_col']
                net_density = data[f'{map_type}']
                patch_info.append((row, col, net_density))
                max_row = max(max_row, row)
                max_col = max(max_col, col)
    # 初始化矩阵，行数和列数要+1（因为索引从0开始）
    matrix = np.full((max_row+1, max_col+1), np.nan)
    for row, col, net_density in patch_info:
        matrix[row, col] = net_density
    matrix = np.flipud(matrix)  # 上下镜像翻转
    return matrix

if __name__ == "__main__":
    patchs_dir = "/data3/taosimin/aieda_fork/example/sky130_test_1/output/iEDA/vectors/route/patchs"
    matrix = read_patch_net_density_matrix(patchs_dir)
    # print(matrix)

    # 输出到CSV
    csv_path = f"{map_type}_matrix.csv"
    np.savetxt(csv_path, matrix, delimiter=",", fmt="%.6f")
    print(f"Matrix saved to {csv_path}")

    # 生成热力图
    import matplotlib.pyplot as plt
    plt.figure(figsize=(8, 6))
    plt.imshow(matrix, cmap='hot', interpolation='nearest')
    plt.colorbar(label=f'{map_type} Map')
    plt.title('Heatmap')
    plt.xlabel('Col')
    plt.ylabel('Row')
    img_path = f"{map_type}_heatmap.png"
    plt.savefig(img_path, bbox_inches='tight')
    plt.close()
    print(f"Heatmap image saved to {img_path}")

