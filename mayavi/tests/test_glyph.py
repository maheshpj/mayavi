# Author: Suyog Dutt Jain <suyog.jain@aero.iitb.ac.in>
#         Prabhu Ramachandran <prabhu_r@users.sf.net>
# Copyright (c) 2008,  Enthought, Inc.
# License: BSD Style.

# Standard library imports.
from os.path import abspath
from StringIO import StringIO
import copy
import numpy
import unittest

# Local imports.
from mayavi.core.null_engine import NullEngine

# Enthought library imports
from mayavi.sources.array_source import ArraySource
from mayavi.modules.outline import Outline
from mayavi.modules.glyph import Glyph
from mayavi.modules.vector_cut_plane import VectorCutPlane

class TestGlyph(unittest.TestCase):


    def make_data(self):
        """Trivial data -- creates an elementary scalar field and a
        constant vector field along the 'x' axis."""
        s = numpy.arange(0.0, 10.0, 0.01)
        s = numpy.reshape(s, (10,10,10))
        s = numpy.transpose(s)

        v = numpy.zeros(3000, 'd')
        v[1::3] = 1.0
        v = numpy.reshape(v, (10,10,10,3))
        return s, v

    def setUp(self):
        """Initial setting up of test fixture, automatically called by TestCase before any other test method is invoked"""
        e = NullEngine()
        # Uncomment to see visualization for debugging etc.
        #e = Engine()
        e.start()
        s=e.new_scene()
        self.e=e
        self.s=s

        ############################################################
        # Create a new scene and set up the visualization.

        d = ArraySource()
        sc, vec = self.make_data()
        d.origin = (-5, -5, -5)
        d.scalar_data = sc
        d.vector_data = vec

        e.add_source(d)

        # Create an outline for the data.
        o = Outline()
        e.add_module(o)
        # Glyphs for the scalars
        g = Glyph()
        e.add_module(g)
        g.glyph.glyph_source.glyph_position = 'center'
        g.glyph.glyph.vector_mode = 'use_normal'
        g.glyph.glyph.scale_factor = 0.5
        g.glyph.mask_input_points = False
        g.actor.property.line_width = 1.0

        v = VectorCutPlane()
        glyph = v.glyph
        gs = glyph.glyph_source
        gs.glyph_position = 'tail'
        gs.glyph_source = gs.glyph_list[1]
        e.add_module(v)
        v.implicit_plane.set(normal=(0, 1, 0), origin=(0, 3, 0))
        glyph.mask_input_points = True
        glyph.mask_points.random_mode = False
        glyph.mask_points.on_ratio = 1

        v = VectorCutPlane()
        glyph = v.glyph
        gs = glyph.glyph_source
        gs.glyph_source = gs.glyph_list[2]
        gs.glyph_position = 'head'
        e.add_module(v)
        v.implicit_plane.set(normal=(0, 1, 0), origin=(0, -2, 0))
        glyph.mask_input_points = True
        glyph.mask_points.random_mode = False
        glyph.mask_points.on_ratio = 4

        self.g=g
        self.v=v
        self.scene = e.current_scene
        return

    def tearDown(self):
        """For necessary clean up, automatically called by TestCase after the test methods have been invoked"""
        self.e.stop()
        return

    def check(self):
        """Do the actual testing."""

        s=self.scene
        src = s.children[0]
        g = src.children[0].children[1]
        self.assertEqual(g.glyph.glyph_source.glyph_position,'center')
        self.assertEqual(g.glyph.glyph.vector_mode,'use_normal')
        self.assertEqual(g.glyph.glyph.scale_factor,0.5)
        self.assertEqual(g.actor.property.line_width,1.0)
        self.assertEqual(g.glyph.mask_input_points,False)

        v = src.children[0].children[2]
        glyph = v.glyph
        gs = glyph.glyph_source
        self.assertEqual(gs.glyph_position,'tail')
        self.assertEqual(gs.glyph_source,gs.glyph_list[1])
        self.assertEqual(numpy.allclose(v.implicit_plane.normal,
                                                    (0., 1., 0.)),True)
        self.assertEqual(glyph.mask_input_points,True)
        self.assertEqual(glyph.mask_points.random_mode,0)
        self.assertEqual(glyph.mask_points.on_ratio,1)

        v = src.children[0].children[3]
        glyph = v.glyph
        gs = glyph.glyph_source
        self.assertEqual(gs.glyph_source,gs.glyph_list[2])
        self.assertEqual(gs.glyph_position,'head')
        self.assertEqual(numpy.allclose(v.implicit_plane.normal,
                         (0., 1., 0.)),True)
        self.assertEqual(glyph.mask_input_points,True)
        self.assertEqual(glyph.mask_points.random_mode,0)
        self.assertEqual(glyph.mask_points.on_ratio,4)

    def test_glyph(self):
        "Test if the test fixture works"
        self.check()

    def test_components_changed(self):
        """"Test if the modules respond correctly when the components
            are changed."""

        g=self.g
        v=self.v
        g.actor = g.actor.__class__()
        glyph = g.glyph
        g.glyph = glyph.__class__()
        g.glyph = glyph

        glyph = v.glyph
        v.glyph = glyph.__class__()
        v.glyph = glyph
        v.actor = v.actor.__class__()
        v.cutter = v.cutter.__class__()
        ip = v.implicit_plane
        v.implicit_plane = ip.__class__()
        v.implicit_plane = ip
        self.check()

    def test_save_and_restore(self):
        """Test if saving a visualization and restoring it works."""
        engine = self.e
        scene = self.scene
        # Save visualization.
        f = StringIO()
        f.name = abspath('test.mv2') # We simulate a file.
        engine.save_visualization(f)
        f.seek(0) # So we can read this saved data.

        # Remove existing scene.

        engine.close_scene(scene)

        # Load visualization
        engine.load_visualization(f)
        self.scene = engine.current_scene

        self.check()

    def test_deepcopied(self):
        """Test if the MayaVi2 visualization can be deep-copied."""
        ############################################################
        # Test if the MayaVi2 visualization can be deep-copied.

        # Pop the source object.
        s = self.scene
        sources = s.children
        s.children = []
        # Add it back to see if that works without error.
        s.children.extend(sources)

        self.check()

        # Now deepcopy the source and replace the existing one with
        # the copy.  This basically simulates cutting/copying the
        # object from the UI via the right-click menu on the tree
        # view, and pasting the copy back.
        sources1 = copy.deepcopy(sources)
        s.children[:] = sources1
        self.check()

    def test_mask_input_points_changed(self):
        """Test if glyph's mask input points works."""

        g = self.g
        g.glyph.mask_input_points = True
        g.glyph.mask_points.on_ratio = 20
        g.glyph.mask_points.random_mode = 0
        g.glyph.mask_points.update()

        mask_output = g.glyph.mask_points.output.number_of_points
        glyph_input = g.glyph.glyph.input.number_of_points
        self.assertEqual(mask_output, 50)
        self.assertEqual(glyph_input, mask_output)


if __name__ == '__main__':
    unittest.main()
