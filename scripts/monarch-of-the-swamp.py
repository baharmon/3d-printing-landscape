#!/usr/bin/env python

"""
Splat Monarch of the Swamp point cloud for 3D printing
"""

__author__ = "Brendan Harmon"
__copyright__ = "Copyright 2026, Brendan Harmon"
__email__ = "brendan.harmon@gmail.com"
__license__ = "MIT"
__version__ = "1.0.0"

# Import modules
import pathlib
import urllib.request
import pyvista as pv
import pyvista_cad
import pymeshfix as mf

# Set mode
pv.set_jupyter_backend("static")

# Set paths
file = pathlib.Path("monarch-of-the-swamp.ply")
root = pathlib.Path(__file__).parents[1].resolve()
source = root / "clouds"
source.mkdir(parents=True, exist_ok=True)
prints = root / "prints"
prints.mkdir(parents=True, exist_ok=True)
images = root / "images"
data = source / file

# Download dataset
url = "https://osf.io/de5zs/download"
try:
    urllib.request.urlretrieve(url, data)
except Exception as e:
    print(f"Error downloading file: {e}")

# Read point cloud
cloud = pv.read(data)

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
    rgb=True,
    render_points_as_spheres=True,
    point_size=size,
    ambient=0.8,
    diffuse=0.8,
    )
pl.view_xz()
pl.camera.zoom(1.25)
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
pl.camera.zoom(1.25)
pl.show(screenshot=screenshot)

# Export mesh
export = prints / file.with_suffix(".3mf")
mesh.cad.to_3mf(export, units="mm")