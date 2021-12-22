#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  1 14:21:13 2021

@author: oakleyjclark
"""


# Finds the gain and intercept (A and B) used to calibrate a given HEXITEC
# system, from an input Am-241 spectrum. Output is used by the file
# calibrate.py
# Oakley Clark - Last Update: 21st June 2021



from hxtV3Read import hxtV3Read
import numpy as np
import scipy.optimize as spo
from progressbar import progressbar
from tkinter import filedialog
import os
import matplotlib.pyplot as plt



# Gaussian function used to peak fit every peak for every pixel to find centre
def gauss(xdata,a,b,c):
    return a*np.exp(-0.5*((xdata-b)/c)**2)



# function that calculates the A and B (gain and intercept) of a pixel
def find_gain_and_intercept(testpix):
    peakenergy = np.array([13.9,20.7,26.3,36.3,59.5]) # ------ USER INPUT ------- INPUT SUBJECT PEAK ENERGIES FROM YOUR DATA
    numberofpeaks = len(peakenergy)
    roughgain = peakenergy[4]/np.argmax(testpix)
    roughcentre = np.round(peakenergy/roughgain)
    searchwidth = 15.0*np.ones(5)# half of the search range for each peak channels
    lc = roughcentre - searchwidth
    uc = roughcentre + searchwidth
    guessparametersgauss = np.zeros(3)
    centres = np.zeros(numberofpeaks)
    for k in range(numberofpeaks):
            datatofit = testpix[int(lc[k]):int(uc[k])+1]
            guessparametersgauss[0] = np.max(datatofit) # amplitude
            guessparametersgauss[1] = roughcentre[k]# centre
            guessparametersgauss[2] = 3.0 # sigma
            lowerbounds = np.array([0,lc[k],0])
            upperbounds = np.array([np.inf,uc[k],6])
            bounds = (lowerbounds,upperbounds)
            channels = np.linspace(int(lc[k]),int(uc[k]),int(uc[k])-int(lc[k])+1)
            popt, pcov = spo.curve_fit(gauss,channels,datatofit,guessparametersgauss,bounds=bounds)  
            centres[k] = popt[1]
            gainintercept = np.polyfit(centres,peakenergy,1)
    return gainintercept
  

      
# Load spectrum data -------- USER INPUT ------ INPUT THE .HXT FILE WITH THE KNOWN PEAKS HERE
print()
print('Data: Select Am-241 spectrum from the detector you wish to calibrate')
calibrationfid = filedialog.askopenfilename()
calibrationfile = hxtV3Read(calibrationfid)



# Save parameters - Now calibrate a spectrum using calibrate.py
print()
print('Save Directory Name: Enter the HEX module identifier to insert into filename...')
print('EG. Where_When_CZT/CdTe_Voltage_Gain')
ID = input()
print()



# Initialize gain and intercept arrays
A = np.zeros((80,80))
B = np.zeros((80,80))
brokenPixels = []



# loop through all pixels to find gain and intercept (A and B)
for i in progressbar(range(80)):
    for j in range(80):
        testpix = calibrationfile[i,j,:]
        try:
            gainintercept = find_gain_and_intercept(testpix)
        except:
            brokenPixels.append((i,j))
            gainintercept = np.zeros(2)
            print('PIXEL ERROR AT (i,j) = (',i,',',j,'): Gain and intercept returned 0')
        finally:
            A[i,j] = gainintercept[0]
            B[i,j] = gainintercept[1]



# Feed back which pixels broke
print()
print('Process terminated for the following pixels:')
print(brokenPixels)
print('A and B returned zero for these pixels')
answer = input('Would you like to make the zero values the mean of the rest or remain at zero? y or n: ')
if (answer == 'y'):
    Amean = np.mean(A)
    Bmean = np.mean(B)
    for k in range(len(brokenPixels)):
        coord = brokenPixels[k]
        A[coord[0],coord[1]] = Amean
        B[coord[0],coord[1]] = Bmean



# Save arrays
newpath = '/Users/oakleyjclark/Desktop/PhD-Work/HEXITEC Data Work/Calibration/Python/Calibration/Calibration Parameters for HEXITEC Detectors/'+ ID
os.mkdir(newpath)
np.save(newpath + '/A.npy',A)
np.save(newpath + '/B.npy',B)
print()
print('Calibration files saved to ',newpath)
print()



# Plots
plotspath = newpath + '/plots'
os.mkdir(plotspath)
# Plot A (Gain Map)
plt.imshow(A)
plt.colorbar()
plt.title('A - Gain Map')
plt.savefig(plotspath+'/A',format='pdf')
plt.close()
# Plot B (Gain Map)
plt.imshow(B)
plt.colorbar()
plt.title('B - Intercept Map')
plt.savefig(plotspath+'/B',format='pdf')
plt.close()



