#!/usr/bin/env python

"""
Splat Japanese maple point cloud for 3D printing
"""

__author__ = "Brendan Harmon"
__copyright__ = "Copyright 2026, Brendan Harmon"
__email__ =  "brendan.harmon@gmail.com"
__license__ = "MIT"
__version__ = "1.0.0"

# Import modules
import pathlib
import urllib.request
import copy
import numpy as np
import open3d as o3d
import pyvista as pv
import pyvista_cad
import pymeshfix as mf

# Set mode
pv.set_jupyter_backend("static")

# Set paths
file = pathlib.Path("acer-palmatum")
root = pathlib.Path(__file__).parents[1].resolve()
source = root / "clouds"
source.mkdir(parents=True, exist_ok=True)
tree = source / "acer-palmatum-01.ply"
fern = source / "dryopteris-erythrosora-01.ply"
moss = source / "moss-02.ply"
prints = root / "prints"
prints.mkdir(parents=True, exist_ok=True)
images = root / "images"

# Download tree
url = "https://osf.io/7s8hf/download"
try:
    urllib.request.urlretrieve(url, tree)
except Exception as e:
    print(f"Error downloading file: {e}")

# Download fern
url = "https://osf.io/bfvwn/download"
try:
    urllib.request.urlretrieve(url, fern)
except Exception as e:
    print(f"Error downloading file: {e}")

# Download moss
url = "https://osf.io/uajxf/download"
try:
    urllib.request.urlretrieve(url, moss)
except Exception as e:
    print(f"Error downloading file: {e}")

# Import tree as point cloud
data = root / tree
t = o3d.io.read_point_cloud(data)

# Import fern as point cloud
data = root / fern
f = o3d.io.read_point_cloud(data)

# Import moss as point cloud
data = root / moss
m = o3d.io.read_point_cloud(data)
colors = np.asarray(m.colors)

# Scale moss
m = m.scale(1.2, center=m.get_center())

# Interpolate ground
origin = [0, 0, 0]
normal = [0, 0, 1]
plane = pv.Plane(center=origin, direction=normal)
points = np.asarray(m.points)
vector = points - origin
distance = np.dot(vector, normal)
plane = points - np.outer(distance, normal)
zshift = -0.05
plane[:, 2] += zshift
parameters = np.linspace(0.0, 1.0, num=10)
m = o3d.geometry.PointCloud()
for p in parameters:
    i = o3d.geometry.PointCloud()
    interpolation = (1 - p) * points + p * plane
    i.points = o3d.utility.Vector3dVector(interpolation)
    i.colors = o3d.utility.Vector3dVector(colors)
    m += i

# Set fern parameters
seed = 1
location = 0.0
scale = 0.25
size = 5
low = 0.5
high = 0.8

# Tranform ferns
clouds = o3d.geometry.PointCloud()
rng = np.random.default_rng(seed)
x = rng.normal(location, scale, size)
y = rng.normal(location, scale, size)
z = np.zeros(size)
points = np.column_stack((x, y, z))
for point in points:
    cloud = copy.deepcopy(f).translate(point)
    scale = rng.uniform(low, high)
    cloud.scale(scale, point)
    angle = np.radians(rng.uniform(0.0, 360.0))
    rotation = cloud.get_rotation_matrix_from_xyz((0, 0, angle))
    cloud.rotate(rotation)
    clouds += cloud
f = clouds

# Merge point clouds
cloud = t + m + f

# Convert colors
colors = np.asarray(cloud.colors)
colors = (colors * 255).astype(np.uint8)

# Export point cloud
data = source / file.with_suffix(".ply")
o3d.io.write_point_cloud(data, cloud)

# Convert point cloud
cloud = pv.PolyData(np.asarray(cloud.points))

# Plot point cloud
res = 2
dimensions = 1000 * res
size = 3 * res
screenshot = images / f"{file.stem}-01.png"
pl = pv.Plotter(
    off_screen=True,
    window_size=(dimensions, dimensions)
    )
pl.enable_eye_dome_lighting()
pl.add_points(
    cloud,
    scalars=colors,
    rgb=True,
    render_points_as_spheres=True,
    point_size=size,
    ambient=0.8,
    diffuse=0.8,
    )
pl.view_xz()
pl.camera.zoom(1.5)
pl.show(screenshot=screenshot)

# Splat point cloud
dimensions = (500, 500, 500)
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
screenshot = images / f"{file.stem}-02.png"
pl = pv.Plotter(
    off_screen=True,
    window_size=(dimensions, dimensions)
    )
pl.enable_ssao()
pl.add_mesh(mesh, color="white")
pl.view_xz()
pl.camera.zoom(1.5)
pl.show(screenshot=screenshot)

# Export mesh
export = prints / file.with_suffix(".3mf")
mesh.cad.to_3mf(export, units="mm")