#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tests.test_utilities

test the functions located in utilities submodule for runtime errors

Author: Jacob Reinhold (jacob.reinhold@jhu.edu)

Created on: 01, 2018
"""

import os
import unittest

import torchvision.transforms as torch_tfms

from niftidataset import *

try:
    import fastai
except ImportError:
    fastai = None


class TestUtilities(unittest.TestCase):

    def setUp(self):
        wd = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(wd, 'test_data', 'images')

    @unittest.skipIf(fastai is None, "fastai is not installed on this system")
    def test_niftidataset_2d_fastai(self):
        composed = torch_tfms.Compose([RandomCrop2D(10, 0),
                                       ToTensor(),
                                       ToFastaiImage()])
        myds = NiftiDataset(self.data_dir, self.data_dir, composed)
        self.assertEqual(myds[0][0].shape, (1,10,10))

    def test_niftidataset_2d(self):
        composed = torch_tfms.Compose([RandomCrop2D(10, 0),
                                       ToTensor(),
                                       Normalize()])
        myds = NiftiDataset(self.data_dir, self.data_dir, composed)
        self.assertEqual(myds[0][0].shape, (1,10,10))

    def test_niftidataset_2d_slice(self):
        composed = torch_tfms.Compose([RandomSlice(0),
                                       ToTensor(),
                                       AddChannel()])
        myds = NiftiDataset(self.data_dir, self.data_dir, composed)
        self.assertEqual(myds[0][0].shape, (1,64,64))

    def test_niftidataset_3d(self):
        composed = torch_tfms.Compose([RandomCrop3D(10),
                                       ToTensor(),
                                       AddChannel()])
        myds = NiftiDataset(self.data_dir, self.data_dir, composed)
        self.assertEqual(myds[0][0].shape, (1,1,10,10,10))

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
