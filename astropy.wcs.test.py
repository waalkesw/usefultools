#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 12:40:03 2017

@author: willwaalkes
"""
import numpy
from matplotlib import pyplot as plt
import matplotlib.axes as Axes
from astropy.io import fits
from astropy.wcs import WCS
import astropy.units as u
import os,sys


GI436_dir_inp = './Data/GI436b/2DSpect/'
GJ1132_dir_inp = './Data/GJ1132B/2DSpect/'

# Load the FITS hdulist using astropy.io.fits
hdulist = fits.open(GI436_dir_inp+'oc2403030_x2d.fits') 

primary = hdulist[0].data  # Primary (NULL) header data unit
img = hdulist[1].data      # Intensity data
err = hdulist[2].data      # Error per pixel
dq = hdulist[3].data       # Data quality per pixel

# Parse the WCS keywords in the primary HDU
wcs = WCS(hdulist[1].header)

#print wcs

#os.sys.exit()

ax = plt.subplot(111, projection=wcs)
plt.imshow(img, origin='lower')
plt.xlabel('Wavelength')
plt.ylabel('Slit Position')
#ax.coords[0].set_major_formatter('x') # Otherwise values round to the nearest whole number
ax.coords[0].set_format_unit(u.angstrom)
#ax.coords[0].set_visible()

#plt.gca()