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

# Set path
file = pathlib.Path("moss-02.ply")
root = pathlib.Path(__file__).parent.resolve()
data = root / file

# Read
cloud = pv.read(data)

# Project
origin = [0, 0, 0]
normal = [0, 0, 1]
plane = pv.Plane(center=origin, direction=normal)
points = np.asarray(cloud.points)
vector = points - origin
distance = np.dot(vector, normal)
plane = points - np.outer(distance, normal)
zshift = -0.05
plane[:, 2] += zshift

# Interpolate
parameters = np.linspace(0.0, 1.0, num=10)
base = pv.PolyData(points)
for p in parameters:
    interpolation = (1 - p) * points + p * plane
    interpolation = pv.PolyData(interpolation)
    base += interpolation

# Plot
pv.set_plot_theme("document")
pl = pv.Plotter(notebook=False, window_size=(2000, 2000))
pl.enable_eye_dome_lighting()
pl.add_points(
    base,
    scalars=base.points[:, 2],
    render_points_as_spheres=True,
    point_size=12,
    show_scalar_bar=False,
    ambient=0.6,
    diffuse=0.8,
    )
pl.show()