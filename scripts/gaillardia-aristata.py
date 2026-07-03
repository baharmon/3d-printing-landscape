#!/usr/bin/env python

"""
Splat blanketflower for 3D printing
"""

__author__ = "Brendan Harmon"
__copyright__ = "Copyright 2026, Brendan Harmon"
__email__ = "brendan.harmon@gmail.com"
__license__ = "MIT"
__version__ = "1.0.0"

# Import modules
import pathlib
import urllib.request
import numpy as np
import open3d as o3d
import pyvista as pv
import pyvista_cad
import pymeshfix as mf

# Set mode
pv.set_jupyter_backend("static")

# Set paths
name = pathlib.Path("gaillardia-aristata")
file = pathlib.Path("gaillardia-aristata-01.ply")
root = pathlib.Path(__file__).parents[1].resolve()
source = root / "clouds"
source.mkdir(parents=True, exist_ok=True)
prints = root / "prints"
prints.mkdir(parents=True, exist_ok=True)
images = root / "images"
data = source / file

# Download dataset
url = "https://osf.io/m2dk5/download"
try:
    urllib.request.urlretrieve(url, data)
except Exception as e:
    print(f"Error downloading file: {e}")

# Plot point cloud
cloud = pv.read(data)
res = 2
dimensions = 1000 * res
size = 5 * res
screenshot = images / f"{name.stem}-01.png"
pv.set_plot_theme("document")
pl = pv.Plotter(
    window_size=(dimensions, dimensions),
    off_screen=True
    )
pl.enable_eye_dome_lighting()
pl.enable_eye_dome_lighting()
pl.add_points(
    cloud,
    rgb=True,
    render_points_as_spheres=True,
    point_size=size,
    ambient=0.7,
    diffuse=0.6,
    )
pl.view_yz()
pl.camera.zoom(1.4)
pl.show(screenshot=screenshot)

# Read point cloud
cloud = o3d.io.read_point_cloud(data)

# Segment point cloud
labels = np.array(cloud.cluster_dbscan(
    eps=0.0014,
    min_points=15,
    print_progress=True)
    )

# Filter point cloud
mask = labels != -1
labels = labels[labels >= 0]
cloud = cloud.select_by_index(np.where(mask)[0])

# Extract clusters
uniques, counts = np.unique(labels, return_counts=True)
sorting = np.argsort(counts)
label = uniques[sorting[-1]]
indices = np.where(labels == label)[0]
stem = cloud.select_by_index(indices)
label = uniques[sorting[-2]]
indices = np.where(labels == label)[0]
flower = cloud.select_by_index(indices)

# Fuse point clouds
center = flower.get_center()
scale = 0.003
size = 10000
shift = [0.0, 0.002, -0.003]
rng = np.random.default_rng()
points = rng.normal(center, scale, (size, 3))
gaussian = o3d.geometry.PointCloud()
gaussian.points = o3d.utility.Vector3dVector(points)
gaussian.translate(shift)
cloud = stem + flower + gaussian

# Filter point cloud
cloud, i = cloud.remove_statistical_outlier(
    nb_neighbors=10,
    std_ratio=3.0
    )

# Convert point cloud
cloud = pv.PolyData(np.asarray(cloud.points))

# Splat point cloud
dimensions = (800, 800, 800)
volume = cloud.gaussian_splatting(
    radius=0.004,
    dimensions=dimensions,
    progress_bar=True
    )
volume = volume.threshold(0.01)

# Extract mesh
mesh = volume.extract_surface(algorithm=None)

# Smooth mesh
mesh = mesh.smooth_taubin(n_iter=50, pass_band=0.1)

# Scale mesh
factor = [50, 50, 50]
mesh = mesh.scale(factor)

# Clean mesh
mesh = mesh.clean()
mesh = mf.MeshFix(mesh)
mesh = mesh.mesh

# Plot mesh
res = 2
dimensions = 1000 * res
screenshot = images / f"{name.stem}-02.png"
pl = pv.Plotter(
    off_screen=True,
    window_size=(dimensions, dimensions)
    )
pl.enable_ssao()
pl.add_mesh(mesh, color="white")
pl.view_yz()
pl.camera.zoom(1.4)
pl.show(screenshot=screenshot)

# Export mesh
export = prints / name.with_suffix(".3mf")
mesh.cad.to_3mf(export, units="mm")