#!/usr/bin/env python

"""
Splat point cloud for 3D printing
"""

__author__ = "Brendan Harmon"
__copyright__ = "Copyright 2026, Brendan Harmon"
__email__ = "brendan.harmon@gmail.com"
__license__ = "MIT"
__version__ = "1.0.0"

# Import modules
import pathlib
import pyvista as pv
import pyvista_cad
import pymeshfix as mf

# Set path
file = pathlib.Path("gaillardia-aristata-01.ply")
root = pathlib.Path(__file__).parent.resolve()
data = root / file

# Read
cloud = pv.read(data)

# Splat
dimensions = (200, 200, 200)
volume = cloud.gaussian_splatting(
    radius=0.002,
    dimensions=dimensions,
    progress_bar=True
    )

# Dilate
kernel = (1,1,1)
volume = volume.dilate(kernel)

# Erode
kernel = (1,1,1)
volume = volume.erode(kernel)

# Extract
volume = volume.threshold(0.01)

# Mesh
mesh = volume.extract_surface(algorithm=None)

# Smooth
mesh = mesh.smooth_taubin(n_iter=50, pass_band=0.1)

# Scale
factor = [50, 50, 50]
mesh = mesh.scale(factor)

# Clean
mesh = mesh.clean()
mesh = mf.MeshFix(mesh)
mesh = mesh.mesh

# Plot
pl = pv.Plotter(notebook=False, window_size=(2000, 2000))
pl.add_mesh(mesh, color="white")
pl.show()

# Export
export = root / file.with_suffix(".3mf")
mesh.cad.to_3mf(export, units="mm")