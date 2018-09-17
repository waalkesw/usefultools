"""
This script is a generalized FITS file reduction pipeline, intended to be used for any
data composed of science images, flats, biases, and darks. 

The objective is that this program can be run in any folder containing the above files,
where the user can input an example file name (i.e. *HD209458_V_flat*) to find the appropriate
calibration and science images, and the pipeline will reduce the data. This happens by creating
a master bias, master flat, and master dark, and then subtracting the bias and dark while dividing
out the flat.

A second script can then be run on the resulting reduced data to perform aperture photometry or
whatever other processes the user has in mind.

Created by Will Waalkes on Wed Jan 17 14:08:47 2018
"""

import astropy.io.fits as ap
import matplotlib.pyplot as plt
import numpy as np
from glob import glob
import os

def reduction(dir_input,date,output,Object,filt):       
    
##### GET THE BIAS IMAGES, CREATE MASTERBIAS
    data = 0.0
    bias_array = []
    bias_image = glob(dir_input+'*Bias*'+date+'*fits')
    if len(bias_image) == 0:
        print "No Biases Found"
        os.sys.exit()
    for file_name in bias_image:
        data,header = ap.getdata(file_name,header=True)
        bias_array.append(data)
    
    masterbias = np.median(bias_array,axis=0)
        
    plt.figure()
    plt.imshow(masterbias)
    plt.colorbar()
    plt.title(str(date)+' Master Bias')
    plt.figure()
    plt.hist(masterbias.flatten())

    
  
##### GET THE DARK IMAGES, CREATE MASTERDARK -> (Dark frames also contain the bias info)
#    data = 0.0
#    dark_array = []
#    dark_image = glob(dir_input+'*Dark*'+date+'*fits')
#    for file_name in dark_image:
#        data,header = ap.getdata(file_name,header=True)
#        dark_array.append(data)
#    
#    masterdark = np.median(dark_array,axis=0)
#    for i in range(len(masterdark[0])):
#        for j in range(len(masterdark[1])):
#            if masterdark[i,j] >= 3000.0:
#                masterdark[i,j] = np.nan
#                
#    if len(dark_image) == 0:
#        print "No Dark Images, using Master Bias"
#        masterdark = masterbias
#    else:
#        plt.figure()
#        plt.imshow(masterdark)
#        plt.colorbar()
#        plt.title(str(date)+' Master Dark')
#        plt.figure()
#        plt.hist(masterdark)
    masterdark = masterbias
    
##### GET THE FLATS, CREATE A MASTERFLAT
    data = 0.0
    flat_array = []
    flat_image = glob(dir_input+'*Flat*'+filt+'*.fits')
    if len(flat_image) == 0:
        print "No Flats Found"
        os.sys.exit()
    for file_name in flat_image:
        data,header = ap.getdata(file_name,header=True)
        flat_array.append(data)
    
    masterflat = np.median(flat_array,axis=0)
    masterflat = masterflat-masterbias
    med = np.median(masterflat)
    masterflat = masterflat/med
        
    plt.figure()
    plt.imshow(masterflat)
    plt.colorbar()
    plt.title(str(date)+' Master Flat')
    plt.figure()
    plt.hist(masterflat.flatten())
    
    #os.sys.exit()
        
##### GET THE SCIENCE IMAGES, SUBTRACT THE BIAS AND DIVIDE THE FLATS
    science_image = glob(dir_input+'*'+Object+'*'+filt+'*'+date+'*.fits')
    if len(science_image) == 0:
        print "No Science images Found"
        os.sys.exit()
    i = 0    
    for file_name in science_image:
        data,header = ap.getdata(file_name,header=True)
        reduced_image = (data-masterdark)/masterflat
        i += 1
        if len(str(i)) == 1:
            ap.writeto(output+Object+'_'+date+'_'+'000'+str(i)+'.fits',reduced_image,header,overwrite = True)
        if len(str(i)) == 2:
            ap.writeto(output+Object+'_'+date+'_'+'00'+str(i)+'.fits',reduced_image,header,overwrite = True)
        if len(str(i)) == 3:
            ap.writeto(output+Object+'_'+date+'_'+'0'+str(i)+'.fits',reduced_image,header,overwrite = True)

#dir_inp = '/Users/willwaalkes/Desktop/Sarah_Project/Observing/'
#
#dates = ['20180117','20180118','20180119']
#objects = ['HAT-P-25b','HAT-P-9b','HAT-P-30b']
#filters = ['R','R','R']
#dir_input = ['20180117/','20180118/','20180119/']
#dir_out = ['20180117/20180117_Reduced/','20180118/20180118_Reduced/','20180119/20180119_Reduced/']
#
#reduction(dir_inp+dir_input[0],dates[0],dir_inp+dir_out[0],objects[0],filters[0])
#reduction(dir_inp+dir_input[1],dates[1],dir_inp+dir_out[1],objects[1],filters[1])
#reduction(dir_inp+dir_input[2],dates[2],dir_inp+dir_out[2],objects[2],filters[2])

dir_inp = '/Volumes/MINERVA/'

filt = 'zp'
dir_input = ['T1Dec11/','T3Nov27/','T3Nov29/','T3Oct24/','T4Oct24/']
dates = ['*','*','*','*','*']
dir_out = ['/Volumes/GameDrive/T1Dec11_Reduced/','/Volumes/GameDrive/T3Nov27_Reduced/',
           '/Volumes/GameDrive/T3Nov29_Reduced/','/Volumes/GameDrive/T3Oct24_Reduced/',
           '/Volumes/GameDrive/T4Oct24_Reduced/']

#reduction(dir_inp+dir_input[0],dates[0],dir_out[0],'WASP-12b',filt)
#reduction(dir_inp+dir_input[1],dates[1],dir_out[1],'WASP-12b',filt)
#reduction(dir_inp+dir_input[2],dates[2],dir_out[2],'WASP-12b',filt)
#reduction(dir_inp+dir_input[3],dates[3],dir_out[3],'WASP-12b',filt)
reduction(dir_inp+dir_input[4],dates[4],dir_out[4],'WASP-12b',filt)
