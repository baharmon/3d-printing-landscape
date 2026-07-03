#!/usr/bin/env python

"""
Interpolate base for point cloud
"""

__author__ = "Brendan Harmon"
__copyright__ = "Copyright 2026, Brendan Harmon"
__email__ =  "brendan.harmon@gmail.com"
__license__ = "MIT"
__version__ = "1.0.0"

# Import modules
import pathlib
import numpy as np
import pyvista as pv
import open3d as o3d

# Set path
file = pathlib.Path("moss-02.ply")
root = pathlib.Path(__file__).parent.resolve()
data = root / file

# Read
cloud = o3d.io.read_point_cloud(data)
colors = np.asarray(cloud.colors)

# Project
points = np.asarray(cloud.points)
origin = [0, 0, 0]
normal = [0, 0, 1]
plane = pv.Plane(center=origin, direction=normal)
vector = points - origin
distance = np.dot(vector, normal)
plane = points - np.outer(distance, normal)
zshift = -0.05
plane[:, 2] += zshift

# Interpolate
parameters = np.linspace(0.0, 1.0, num=10)
base = o3d.geometry.PointCloud()
for p in parameters:
    i = o3d.geometry.PointCloud()
    interpolation = (1 - p) * points + p * plane
    i.points = o3d.utility.Vector3dVector(interpolation)
    i.colors = o3d.utility.Vector3dVector(colors)
    base += i

# Render
o3d.visualization.draw_geometries([base])

# Export
export = root / "base.ply"
o3d.io.write_point_cloud(export, base)
o3d.io.write_point_cloud(export.with_suffix(".pcd"), base, compressed=True)