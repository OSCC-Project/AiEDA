import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from multiprocessing import Pool
directory = os.getcwd()
output_dir = os.path.join(directory, 'output_png')
os.makedirs(output_dir, exist_ok=True)
def process_csv(filename):
    output_name = os.path.basename(os.path.dirname(filename)) + "_" + os.path.splitext(os.path.basename(filename))[0]
    plt.figure()  
    temp = sns.heatmap(np.array(pd.read_csv(filename)), cmap='hot_r')
    temp.set_title(output_name)
    plt.savefig(os.path.join(output_dir, output_name + ".png"), dpi=300, bbox_inches='tight')
    plt.close()  
csv_files = [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.endswith(".csv")]
with Pool() as pool:
    pool.map(process_csv, csv_files)
