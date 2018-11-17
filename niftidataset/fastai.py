#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
niftidataset.fastai

functions to support fastai datasets

Author: Jacob Reinhold (jacob.reinhold@jhu.edu)

Created on: Nov 15, 2018
"""

__all__ = ['open_nii',
           'get_slice',
           'get_patch3d',
           'niidatabunch']

from functools import singledispatch
from typing import Callable, List, Optional, Union

import fastai as fai
import fastai.vision as faiv
import nibabel as nib
import numpy as np
import torch

from .utils import glob_nii


def open_nii(fn:str) -> faiv.Image:
    """ Return fastai `Image` object created from NIfTI image in file `fn`."""
    x = nib.load(str(fn)).get_data()
    return faiv.Image(torch.Tensor(x))


@faiv.TfmPixel
@singledispatch
def get_slice(x, pct:faiv.uniform=0.5, axis:int=0) -> np.ndarray:
    """" Get a random slice of `x` based on axis """
    s = int(x.size(axis) * pct)
    return x[np.newaxis,s,:,:].contiguous() if axis == 0 else \
           x[np.newaxis,:,s,:].contiguous() if axis == 1 else \
           x[np.newaxis,:,:,s].contiguous()

@faiv.TfmPixel
@singledispatch
def get_patch3d(x, pct:faiv.uniform=0.5, ps:int=64) -> np.ndarray:
    """" Get a random 3d patch of `x` of size ps^3 """
    h, w, d = x.shape
    max_idxs = (h - ps // 2, w - ps // 2, d - ps // 2)
    min_idxs = (ps // 2, ps // 2, ps // 2)
    mask = np.where(x > x.mean())  # returns a tuple of length 3
    c = int(len(mask[0] * pct)-1)
    s_idxs = [m[c] for m in mask]  # pull out the chosen idxs
    i, j, k = [i if min_i <= i <= max_i else max_i if i > max_i else min_i
               for max_i, min_i, i in zip(max_idxs, min_idxs, s_idxs)]
    o = 0 if ps % 2 == 0 else 1
    return x[np.newaxis, i-ps//2:i+ps//2+o, j-ps//2:j+ps//2+o, k-ps//2:k+ps//2+o].contiguous()


def niidatabunch(src_dir:str, tgt_dir:str, split:float=0.2, tfms:Optional[List[Callable]]=None,
                 path:str='.', bs:int=32, device:Union[str,torch.device]="cpu", n_jobs=fai.defaults.cpus):
    """ create a NIfTI databunch from two directories """
    src_fns = glob_nii(src_dir)
    tgt_fns = glob_nii(tgt_dir)
    if len(src_fns) != len(tgt_fns) or len(src_fns) == 0:
        raise ValueError(f'Number of source and target images must be equal and non-zero')
    val_idxs = np.random.choice(len(src_fns), int(split * len(src_fns)))
    srcd = fai.ItemList(src_fns, create_func=open_nii).split_by_idx(val_idxs)
    tgtd = fai.ItemList(tgt_fns, create_func=open_nii).split_by_idx(val_idxs)
    train_ll = fai.LabelList(srcd.train, tgtd.train, tfms, tfm_y=True)
    val_ll = fai.LabelList(srcd.valid, tgtd.valid, tfms, tfm_y=True)
    ll = fai.LabelLists(path, train_ll, val_ll)
    idb = faiv.ImageDataBunch.create_from_ll(ll, bs=bs, device=device, num_workers=n_jobs)
    return idb
