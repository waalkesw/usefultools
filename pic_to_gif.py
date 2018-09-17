#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May 30 15:29:48 2018

@author: willwaalkes
"""

import imageio
from glob import glob

filenames = ['GJ1132b-01-spect.png', 'GJ1132b-02-spect.png', 'GJ1132b-03-spect.png',
             'GJ1132b-04-spect.png', 'GJ1132b-05-spect.png', 'GJ1132b-06-spect.png',
             'GJ1132b-07-spect.png', 'GJ1132b-08-spect.png', 'GJ1132b-09-spect.png',
             'GJ1132b-10-spect.png', 'GJ1132b-11-spect.png', 'GJ1132b-12-spect.png',
             'GJ1132b-13-spect.png', 'GJ1132b-14-spect.png']

images = []
for filename in filenames:
    images.append(imageio.imread(filename))
    
imageio.mimsave('Gj1132bspectra.gif', images,duration=1)