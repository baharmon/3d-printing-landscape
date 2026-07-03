#!/usr/bin/env python

"""
Plot point cloud
"""

__author__ = "Brendan Harmon"
__copyright__ = "Copyright 2026, Brendan Harmon"
__email__ =  "brendan.harmon@gmail.com"
__license__ = "MIT"
__version__ = "1.0.0"

# Import modules
import pathlib
import pyvista as pv

# Set path
file = pathlib.Path("gaillardia-aristata-01.ply")
directory = pathlib.Path("data")
root = pathlib.Path(__file__).parent.resolve()
data = root / file

# Set plot theme
pv.set_plot_theme("document")

# Read point cloud
cloud = pv.read(data)

# Plot
pv.plot(cloud, rgb=True, point_size=2, zoom=1.25)

# Save
res = 4
dimensions = 1000 * res
size = 4 * res
screenshot = root / file.with_suffix(".png")
pl = pv.Plotter(
    notebook=False,
    off_screen=True,
    window_size=(dimensions, dimensions)
    )
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
pl.camera.zoom(1.25)
pl.show(screenshot=screenshot)