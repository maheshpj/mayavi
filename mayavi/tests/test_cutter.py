# Author:
# Copyright (c) 2008,  Enthought, Inc.
# License: BSD Style.

# Standard library imports.
import unittest

# Local imports.
from mayavi.core.null_engine import NullEngine
from tvtk.api import tvtk

# Enthought library imports
from mayavi.sources.vtk_data_source import VTKDataSource
from mayavi.modules.outline import Outline
from mayavi.modules.scalar_cut_plane import ScalarCutPlane
from mayavi.filters.point_to_cell_data import PointToCellData
from mayavi.filters.triangle_filter import TriangleFilter


class TestCutter(unittest.TestCase):

    def setUp(self):
        """Initial setting up of test fixture, automatically called by TestCase before any other test method
        is invoked"""

        e = NullEngine()
        # Uncomment to see visualization for debugging etc.
        from mayavi.core.engine import Engine
        #e = Engine()
        e.start()
        e.new_scene()
        self.e = e

        image_data = tvtk.ImageData(spacing=(1, 1, 1), origin=(0, 0, 0))
        image_data.extent = [-2, 2, -2, 2, -2, 2]
        image_data.dimensions = [3, 3, 3]

        src = VTKDataSource(data=image_data)
        e.add_source(src)

        return

    def tearDown(self):
        """For necessary clean up, automatically called by TestCase after the test methods have been invoked"""
        self.e.stop()
        return

    def check(self, generate_triangles, no_of_cells):
        cp = self.cp
        ip = cp.implicit_plane

        cp.cutter.cutter.generate_triangles = generate_triangles
        ip.normal = 1, 1, 1
        poly_data = cp.cutter.outputs[0]
        self.assertEqual(poly_data.number_of_cells, no_of_cells)

    def add_unstructured_modules(self):
        e = self.e

        filter_point_to_celldata = PointToCellData()
        e.add_filter(filter_point_to_celldata)

        filter_triangle = TriangleFilter()
        e.add_filter(filter_triangle, obj=filter_point_to_celldata)

        self.add_common_modules()

    def add_common_modules(self):
        e = self.e

        # Create an outline for the data.
        o = Outline()
        e.add_module(o)

        # An interactive scalar cut plane.
        cp = ScalarCutPlane()
        e.add_module(cp)
        ip = cp.implicit_plane
        ip.origin = -1.5, -1.5, -1.5

        # Since this is running offscreen this seems necessary.
        ip.widget.origin = 0.5, 0.5, 0.5
        self.cp = cp

    def change_plane(self):
        # cut-function plane normal to original values
        cp = self.cp
        ip = cp.implicit_plane
        ip.normal = 0, 0, 0

    def test_structured(self):
        """Tests if cutter works for structured grid"""
        self.add_common_modules()
        self.check(generate_triangles=0, no_of_cells=4)
        self.change_plane()
        self.check(generate_triangles=1, no_of_cells=7)

    def test_unstructured(self):
        """Tests if cutter works for unstructured grid"""
        self.add_unstructured_modules()
        self.check(generate_triangles=0, no_of_cells=7)
        self.change_plane()
        self.check(generate_triangles=1, no_of_cells=10)

if __name__ == '__main__':
    unittest.main()