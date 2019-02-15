#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
niftidataset.utils

assortment of input/output utilities for the project

Author: Jacob Reinhold (jacob.reinhold@jhu.edu)

Created on: Oct 24, 2018
"""

__all__ = ['split_filename',
           'glob_imgs']

from typing import List, Tuple

from glob import glob
import os


def split_filename(filepath: str) -> Tuple[str, str, str]:
    """ split a filepath into the directory, base, and extension """
    path = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    base, ext = os.path.splitext(filename)
    if ext == '.gz':
        base, ext2 = os.path.splitext(base)
        ext = ext2 + ext
    return path, base, ext


def glob_imgs(path: str, ext='*.nii*') -> List[str]:
    """ grab all `ext` files in a directory and sort them for consistency """
    fns = sorted(glob(os.path.join(path, ext)))
    return fns
