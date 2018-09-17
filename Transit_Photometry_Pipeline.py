"""
This script is where the aperture photometry will be performed on an already reduced
set of FITS images. 

The intended purpose is to analyze exoplanet transit light curves by specifying apertures
around the host star as well as several comparison stars.

Created by Will Waalkes on Wed Jan 17 23:03:28 2018
"""

import os
import sys
import numpy as np
from astropy.time import Time
import astropy.io.fits as fits
import astropy.wcs as wcs
from astropy.coordinates import SkyCoord  # High-level coordinates
from astropy.coordinates import ICRS, Galactic, FK4, FK5  # Low-level frames
from astropy.coordinates import Angle, Latitude, Longitude  # Angles
from astropy import coordinates as coord
from astropy.table import hstack
import astropy.units as u
from photutils import CircularAperture
from photutils import SkyCircularAperture
from photutils import aperture_photometry
from photutils import CircularAnnulus
from glob import glob

def Photometry(dir_input,date,period,Object,BJD_t0,star_coords,r,r_in,r_out):
    
    Data_Image = glob(dir_input+Object+'*.fits')
    comparison_coords = ascii.read(dir_input+Object+'-comp_coords.txt') #2 columns, RA and DEC
    X = comparison_coords['RA']
    Y = comparison_coords['DEC']
    flux = np.zeros(len(Data_Image))
    BJD_times = np.zeros(len(Data_Image))
    transit_hours = np.zeros(len(Data_Image))
    relative_phot = np.zeros((len(Data_Image),len(X)))
    
    i = 0
    for file_name in Data_Image:
        
        '''
        Read in the file and acquire object coordinates.
        '''
        
        hdulist = fits.open(file_name)
        data = hdulist[0].data
        header = hdulist[0].header
        w_conv = wcs.WCS(hdulist[0].header)
        px, py = wcs.utils.skycoord_to_pixel(SkyCoord(star_coords, frame=FK5, unit=(u.deg, u.deg)), w_conv)
        
        '''
        For each exposure, extract the UTC time, convert to BJD, and then convert BJD
        to hours from mid-transit
        '''
        
        UTC_times = header['DATE-OBS']
        EXP_time = header['EXPOSURE']
        
        #MINERVA_location = [-110.52443*u.deg,31.40495*u.deg] #long, lat
        APO_location = [-110.52443*u.deg,31.40495*u.deg] #long, lat
        exp_time = EXP_time/(3600.*24.) #put seconds into day
        t_start = Time(UTC_times, format = 'isot', scale='utc')
        start_time = t_start.jd #convert to jd times
        end_time = start_time + exp_time #in jd
        avg_time = (start_time+end_time)/2. #in jd
        avg_time_t = Time(avg_time, format='jd', scale='utc',location=(APO_location[0],APO_location[1]))  
     
        star_loc = coord.SkyCoord(header['TELRA'],header['TELDEC'],unit=(u.hourangle,u.deg),frame='icrs')
        light_travel = avg_time_t.light_travel_time(star_loc)
    
        BJD_time = light_travel+avg_time_t.tdb
        BJD_time = BJD_time.jd
        BJD_times[i] = BJD_time
    
        '''
        Calculate the phase of each observation, based on linear relationship between BJD and period.
        '''
       
        Norbits = (BJD_time - BJD_t0)/period #adding 0.5 shifts the orbit by 1/2 so that I am tracking the eclipse
            
        orbit = str(Norbits-int(Norbits))[1:]
        orbit = float(orbit)
        if orbit >= 0.5:
            phase = -1.0 + orbit
        else:
            phase = orbit
                
        transit_time = phase*(period*24.0) #This calculates how many hours before and after eclipse
        transit_hours[i] = transit_time
        
        '''
        NOW PERFORM BACKGROUND SUBTRACTION AND PHOTOMETRY
        '''
        
        positions = [px,py]
        apertures = CircularAperture(positions, r)
        annulus_apertures = CircularAnnulus(positions, r_in, r_out)    
        rawflux_table = aperture_photometry(data, apertures)
        bkgflux_table = aperture_photometry(data, annulus_apertures)
        phot_table = hstack([rawflux_table, bkgflux_table], table_names=['raw', 'bkg'])
        bkg_mean = phot_table['aperture_sum_bkg'] / annulus_apertures.area()
        bkg_sum = bkg_mean * apertures.area()
        final_sum = phot_table['aperture_sum_raw'] - bkg_sum
        phot_table['residual_aperture_sum'] = final_sum
        flux[i] = float(final_sum)
        print "Total Flux:",final_sum
        print "Background:",bkg_sum
        
        '''
        Now, perform the photometry on a handful of other bright stars in the field.
        '''
        for k in range(len(Y)):
            positions = [X[k],Y[k]]
            apertures = CircularAperture(positions, r)
            annulus_apertures = CircularAnnulus(positions, r_in, r_out)    
            rawflux_table = aperture_photometry(data, apertures)
            bkgflux_table = aperture_photometry(data, annulus_apertures)
            phot_table = hstack([rawflux_table, bkgflux_table], table_names=['raw', 'bkg'])
            bkg_mean = phot_table['aperture_sum_bkg'] / annulus_apertures.area()
            bkg_sum = bkg_mean * apertures.area()
            final_sum = phot_table['aperture_sum_raw'] - bkg_sum
            phot_table['residual_aperture_sum'] = final_sum
            relative_phot[i,k] = float(final_sum)
        
         #PRINT THE FITS FILE WITH THE CIRCULAR APERTURE
         
        f,ax = plt.subplots(1)
        ax.imshow(data,cmap='gray',vmin=0,vmax=3)
        circ = Circle((px,py),r,fill='False',edgecolor='yellow',facecolor='none')
        circ2 = Circle((px,py),r_in,fill='False',edgecolor='green',facecolor='none')
        circ3 = Circle((px,py),r_out,fill='False',edgecolor='green',facecolor='none')
        ax.add_patch(circ)
        ax.add_patch(circ2)
        ax.add_patch(circ3)
        plt.show()
        plt.savefig('/Users/willwaalkes/Desktop/circles.eps')
        
        i += 1
        
    #np.savetxt(dir_out+Object+'_'+date+'_fluxes.txt',flux) 
    #np.savetxt(dir_out+Object+'_'+date+'-transit_times.txt',transit_hours)
    #np.savetxt(dir_out+Object+'_'+date+'-comparison_stars.txt',relative_phot)
    data = Table((flux,transit_hours,relative_phot),('Target Flux','Times','Comparison Fluxes'))
    ascii.write(data,dir_input+Object+'-Fluxes.txt')

desktop = '/Users/willwaalkes/Desktop/'
dir_input = '/Volumes/Win_Compat_/ColoradoResearch/TFOP/reduced/'#THIS MUST BE THE SAME DIRECTORY THAT YOU SAVED THE REDUCED FILES TO
dir_out = 

#dates = ['20180117','20180118','20180119']
#periods = ['','','']
#periods = np.array(periods)
#objects = ['HAT-P-25b','HAT-P-9b','HAT-P-30b']
#BJDs = ['','','']
#BJDs = np.array(BJDs)
#object_coords = [[""],["7.344577777777777 +37.14061111111111"],[""]]
#
#Photometry(dir_input,dates[0],periods[0],objects[0],BJDs[0],object_coords[0],r=12.0,r_in=16.0,r_out=18.0)
#Photometry(dir_input,dates[1],periods[1],objects[1],BJDs[1],object_coords[1],r=12.0,r_in=16.0,r_out=18.0)
#Photometry(dir_input,dates[2],periods[2],objects[2],BJDs[2],object_coords[2],r=12.0,r_in=16.0,r_out=18.0)