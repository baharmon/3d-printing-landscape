#!/usr/bin/env python

"""
Segment point cloud
"""

__author__ = "Brendan Harmon"
__copyright__ = "Copyright 2026, Brendan Harmon"
__email__ =  "brendan.harmon@gmail.com"
__license__ = "MIT"
__version__ = "1.0.0"

# Import modules
import pathlib
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt
import pyvista as pv

# Set path
file = pathlib.Path("gaillardia-aristata-01.ply")
root = pathlib.Path(__file__).parent.resolve()
data = root / file

# Read point cloud
cloud = o3d.io.read_point_cloud(data)
print(cloud)

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

# Plot
o3d.visualization.draw([cloud], show_skybox=False)

# Save
res = 4
dimensions = 1000 * res
size = 5 * res
screenshot = root / file.with_suffix(".png")
pv.set_plot_theme("document")
pl = pv.Plotter(
    window_size=(dimensions, dimensions),
    off_screen=True
    )
pl.enable_eye_dome_lighting()
pl.add_points(
    np.asarray(cloud.points),
    scalars=np.asarray(cloud.colors),
    render_points_as_spheres=True,
    point_size=size,
    show_scalar_bar=False,
    ambient=0.6,
    diffuse=0.8,
    )
pl.view_yz()
pl.camera.zoom(1.25)
pl.show(screenshot=screenshot)