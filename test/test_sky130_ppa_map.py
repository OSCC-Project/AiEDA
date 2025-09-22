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

from typing import Dict, List, Tuple, Any

from sklearn.metrics import r2_score, mean_absolute_error

class TimingPowerBenchmark:
    def __init__(
        self,
        clock_freq_map: Dict[str, List[float]],
        end_vertex_to_path_delay: List[Tuple[str, float]],
        leakage_power: float,
        internal_power: float,
        switch_power: float
    ):
        self.clock_freq_map = clock_freq_map
        self.end_vertex_to_path_delay = end_vertex_to_path_delay
        self.leakage_power = leakage_power
        self.internal_power = internal_power
        self.switch_power = switch_power

    @classmethod
    def from_json(cls, file_path: str) -> "TimingPowerBenchmark":
        with open(file_path, "r") as f:
            data = json.load(f)
        return cls(
            clock_freq_map=data.get("clock_freq_map", {}),
            end_vertex_to_path_delay=[
                (item[0], item[1]) for item in data.get("end_vertex_to_path_delay", [])
            ],
            leakage_power=data.get("leakage_power", 0.0),
            internal_power=data.get("internal_power", 0.0),
            switch_power=data.get("switch_power", 0.0)
        )

    def __repr__(self):
        return (
            f"TimingPowerBenchmark(clock_freq_map={self.clock_freq_map}, "
            f"end_vertex_to_path_delay={self.end_vertex_to_path_delay[:3]}..., "
            f"leakage_power={self.leakage_power}, "
            f"internal_power={self.internal_power}, "
            f"switch_power={self.switch_power})"
        )
        
    def to_flat_vector(self) -> list:
        freq_values = []
        for v in self.clock_freq_map.values():
            freq_values.extend(v)
        delay_values = [delay for _, delay in self.end_vertex_to_path_delay]
        return (
            freq_values +
            delay_values +
            [self.leakage_power, self.internal_power, self.switch_power]
        )

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

def create_ppa_vec(benchmark_json, patch_dir):
    tp_benchmark = TimingPowerBenchmark.from_json(benchmark_json)
    print(tp_benchmark)
    
    benchmark_vector = tp_benchmark.to_flat_vector()
    
    matrix = read_patch_net_density_matrix(patch_dir)
    matrix_flat = matrix.flatten().tolist()
    
    total_vector = benchmark_vector + matrix_flat
    
    return np.array(benchmark_vector)


if __name__ == "__main__":
    patchs_dir = "/data3/taosimin/aieda_fork/example/sky130_test_1/output/iEDA/vectors/route/patchs"
    
    # matrix = read_patch_net_density_matrix(patchs_dir)
    # print(matrix)

    # csv_path = f"{map_type}_matrix.csv"
    # np.savetxt(csv_path, matrix, delimiter=",", fmt="%.6f")
    # print(f"Matrix saved to {csv_path}")

    # import matplotlib.pyplot as plt
    # plt.figure(figsize=(8, 6))
    # plt.imshow(matrix, cmap='hot', interpolation='nearest')
    # plt.colorbar(label=f'{map_type} Map')
    # plt.title('Heatmap')
    # plt.xlabel('Col')
    # plt.ylabel('Row')
    # img_path = f"{map_type}_heatmap.png"
    # plt.savefig(img_path, bbox_inches='tight')
    # plt.close()
    # print(f"Heatmap image saved to {img_path}")
    
    benchmark_json = "/data3/taosimin/aieda_fork/example/sky130_test_1/output/iEDA/vectors/route/timing_power_benchmark.json"
    truth_vec = create_ppa_vec(benchmark_json, patchs_dir)
    
    patchs_dir = "/data3/taosimin/aieda_fork/example/sky130_test_1/output/iEDA/vectors/place/patchs"
    benchmark_json = "/data3/taosimin/aieda_fork/example/sky130_test_1/output/iEDA/vectors/place/timing_power_benchmark.json"
    pred_vec = create_ppa_vec(benchmark_json, patchs_dir)
    
    # calc R²
    r2 = r2_score(truth_vec, pred_vec)

    # calc MAE
    mae = mean_absolute_error(truth_vec, pred_vec)

    print(f"R²: {r2:.4f}")
    print(f"MAE: {mae:.4f}")


