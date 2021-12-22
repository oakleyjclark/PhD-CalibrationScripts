# PhD-CalibrationScripts
These scripts calibrate the pixellated X-ray detector HEXITEC, based on an exposure to an Am241 gamma source

Normally, the file calibration.py is run once on the file. This finds the gain and intercept values for each of the 6400 pixels, that best maps the ADU to the true energy. These parameters are saved. Then calibrate.py can be run, to produce the calibrated version of the spectrum.

The data is too large to upload (>40MB), but example data can be made available on request
