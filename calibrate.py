# Calibrate HEXITEC data using the calibration parameters and binedges found using
# calibration.py. User input is labelled in comments with CAPITALS
# Oakley Clark 



import numpy as np
from tkinter import filedialog
from hxtV3Read import hxtV3Read
from progressbar import progressbar
import matplotlib.pyplot as plt
    


# Function that calibrates a pixel based on the A and B value for that pixel
# and the master bin edges (newEdges)
def calibrate_pixel(Apix,Bpix,newEdges,uncalibrated):
    numberOfChannels = len(uncalibrated)
    calibrated = np.zeros(numberOfChannels)
    startpoint = 0
    for k in range(numberOfChannels):
        pixcentre = (k+1)*Apix + Bpix
        for g in range(startpoint,numberOfChannels):
            if (newEdges[g] < pixcentre and  newEdges[g+1] > pixcentre):
                calibrated[g-1] += uncalibrated[k]
                startpoint = g
                break
    return calibrated



# Load arrays A and B (gain and intercept)
print('Locate the directory that contains the calibration parameters for your module: ')
#parameterDir = filedialog.askdirectory()
parameterDir = '/Users/oakleyjclark/Desktop/PhD-Work/HEXITEC Data Work/Calibration/Python/Calibration/Calibration Parameters for HEXITEC Detectors/RAL_MAY21_CZT_1000V_GAIN=0'
A = np.load(parameterDir+'/A.npy')
B = np.load(parameterDir+'/B.npy')



# Load the spectrum to calibrate
print('Locate the .hxt file you would like to calibrate: ')
uncalibratedfid = filedialog.askopenfilename()
uncalibrated = hxtV3Read(uncalibratedfid)



# Create newcentres and newedges array based on the average gain and intercepts 
# of that module and the number of channels of the data to calibrate
numberOfChannels = np.shape(uncalibrated)[2]
newCentres = np.mean(A)*np.linspace(1,numberOfChannels,numberOfChannels) + np.mean(B)
newEdges = np.arange(newCentres[0]-(np.mean(A)/2),newCentres[-1]+(0.6*np.mean(A)),np.mean(A)) # 0.6 so just over half
#Emin = 0
#Emax = 80
#newEdges = np.linspace(Emin,Emax,numberOfChannels+1)
#newCentres = np.zeros(numberOfChannels)
#for i in range(numberOfChannels):
#    newCentres[i] = 0.5*(newEdges[i]+newEdges[i+1])

    

# Calibrate spectrum
calibratedSpectrum = np.zeros((80,80,numberOfChannels))
for i in progressbar(range(80)):
    for j in range(80):
        calibratedSpectrum[i,j,:] = calibrate_pixel(A[i,j],B[i,j],newEdges,uncalibrated[i,j,:])



# Create the calibrated summedSpectrum & old summed spectrum for reference
summedSpectrum = np.zeros(numberOfChannels)
oldSummedSpectrum = np.zeros(numberOfChannels)
for i in range(80):
    for j in range(80):
        summedSpectrum[:] += calibratedSpectrum[i,j,:]
        oldSummedSpectrum[:] += uncalibrated[i,j,:]
        


# Plot the calibrated summed spectrum vs uncalibrated summed spectrum
plt.plot(newCentres,summedSpectrum,label='Calibrated')
plt.plot(newCentres,oldSummedSpectrum,label='Uncalibrated')
plt.title('Summed Spectrum')
plt.xlabel('Energy (keV)')
plt.ylabel('Summed Counts')
plt.legend(loc='best')
plt.show()



# Save the calibrated array - same directory as uncalibrated hxt file
print('Where would you like to save the calibrated numpy array? ')
saveDir = filedialog.askdirectory()
insertIndex = uncalibratedfid.rfind('/') + 1
calibratedfid = saveDir + 'CALIBRATED_' + uncalibratedfid[insertIndex:-3] + 'npy'
np.save(calibratedfid,calibratedSpectrum)
np.save(saveDir+'CENTRES',newCentres)





