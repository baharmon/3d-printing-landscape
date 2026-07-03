#!/usr/bin/env python

"""
Filter point cloud
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

# Set path
file = pathlib.Path("gaillardia-aristata-01.ply")
root = pathlib.Path(__file__).parent.resolve()
data = root / file

# Read point cloud
cloud = o3d.io.read_point_cloud(data)
print(cloud)

# Decimate point cloud
cloud = cloud.voxel_down_sample(voxel_size=0.0008)

# Crop to sphere
center = np.array([0.0, 0.0, 0.12])
radius = 0.1
points = np.asarray(cloud.points)
distance = np.linalg.norm(points - center, axis=1)
mask = distance < radius
cloud = cloud.select_by_index(np.where(mask)[0])

# # Crop to box
# region = o3d.geometry.AxisAlignedBoundingBox(
#     min_bound=(-0.1, -0.1, 0.2),
#     max_bound=(0.1, 0.1, 0.05)
#     )
# cloud = cloud.crop(region)

# Statistical outlier removal
cloud, i = cloud.remove_statistical_outlier(
    nb_neighbors=10,
    std_ratio=1.0
    )

# Radius outlier removal
cloud, i = cloud.remove_radius_outlier(
    nb_points=16,
    radius=0.05
    )

# Render point cloud
o3d.visualization.draw_geometries([cloud])
print(cloud)