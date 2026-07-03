#!/usr/bin/env python

"""
Extract point cloud
"""

__author__ = "Brendan Harmon"
__copyright__ = "Copyright 2023, Brendan Harmon"
__email__ =  "brendan.harmon@gmail.com"
__license__ = "MIT"
__version__ = "1.0.0"

# Import modules
import pathlib
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt

# Set path
file = pathlib.Path("gaillardia-aristata-01.ply")
root = pathlib.Path(__file__).parent.resolve()
data = root / file

# Read point cloud
cloud = o3d.io.read_point_cloud(data)

# Segment point cloud
labels = np.array(cloud.cluster_dbscan(
    eps=0.0014,
    min_points=15,
    print_progress=True)
    )
print(f"Clusters: {labels.max() + 1}")

# Filter noise
mask = labels != -1
labels = labels[labels >= 0]
cloud = cloud.select_by_index(np.where(mask)[0])

# Set colors
colors = plt.get_cmap(
    "viridis")(labels / (labels.max() if labels.max() > 0 else 1)
    )
colors[labels < 0] = 0
cloud.colors = o3d.utility.Vector3dVector(colors[:, :3])

# Extract cluster
label = 1
indices = np.where(labels == label)[0]
cluster = cloud.select_by_index(indices)
o3d.visualization.draw_geometries([cluster])

# Extract largest cluster
uniques, counts = np.unique(labels, return_counts=True)
sorting = np.argsort(counts)
label = uniques[sorting[-1]]
indices = np.where(labels == label)[0]
cluster = cloud.select_by_index(indices)
o3d.visualization.draw_geometries([cluster])

# Extract second largest cluster
label = uniques[sorting[-2]]
indices = np.where(labels == label)[0]
cluster = cloud.select_by_index(indices)
o3d.visualization.draw_geometries([cluster])

