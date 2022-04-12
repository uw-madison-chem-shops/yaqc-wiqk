# setting up seabreeze and pyseabreeze
import seabreeze

seabreeze.use("pyseabreeze")
import seabreeze.spectrometers as sb

# Assign spectrometer to 'spec' variable from serial number
spec = sb.Spectrometer.from_serial_number("USB4C00173")


# Print device type/serial code identifier
devices = sb.list_devices()
print(devices)
# set integration time
spec.integration_time_micros(50000)

# get wavelengths and intensities from spectrometer
wavelengths = spec.wavelengths()
intensities = spec.intensities(correct_dark_counts=True, correct_nonlinearity=False)
# print('Wavelengths ' + str(wavelengths)) #prints condensed list
# print('Intensities ' + str(intensities)) #prints condensed list

# assing wavelengths and intensities to a full list
new_wavelengths = wavelengths.tolist()
new_intensities = intensities.tolist()
# print(new_wavelengths) #prints wavelengths of entire spectrum into list

# indexing each wavelength to Lambda_#
Lambda_1 = new_wavelengths.index(570.7029414440528)
Lambda_2 = new_wavelengths.index(570.9066104179429)  # 570.9066104179429 nm #target lambda
Lambda_3 = new_wavelengths.index(571.110264928086)
# Avg_Wavelength = (new_wavelengths[Lambda_1] + new_wavelengths[Lambda_2] + new_wavelengths[Lambda_3])/3
# print('Wavelength_1 index = ', Lambda_1)
# print('Wavelength_2 index = ', Lambda_2)
# print('Wavelength_3 index = ', Lambda_3)
print(
    "Wavelength_1(nm) = ", new_wavelengths[Lambda_1], "Intensity_1 = ", new_intensities[Lambda_1]
)
print(
    "Wavelength_2(nm) = ", new_wavelengths[Lambda_2], "Intensity_2 = ", new_intensities[Lambda_2]
)
print(
    "Wavelength_3(nm) = ", new_wavelengths[Lambda_3], "Intensity_3 = ", new_intensities[Lambda_3]
)


import time

time.strftime("%Y-%m")


import os
import numpy as np

# wiqk-data and averaged_wavelength are the folder locations, desktop>wiqk-data>averaged_wavelength
# May be a good idea to add date folders when running tests and rxns
# Ex. desktop>wiqk-data>averaged_wavelength>Jun_16_2021 to stay organized, must create folder in file explorer location first
# Add this for Continuous and Stopped Flow scripts when publishing to .txt files -
filename = (
    ("wiqk-data")
    + os.sep
    + ("averaged_wavelength")
    + os.sep
    + time.strftime("%Y_%m_%d_%H-%M-%S-%p")
    + ".txt"
)


def write_row(path, row):
    with open(path, "a") as f:
        for n in row:
            f.write("%10.4f" % n)  # decimal is number of decimal places
            f.write("\t")
            f.write("\t")
        f.write("\n")


# write header to file
with open(filename, "a") as f:
    f.write("# Timestamp     \tElapsed Time    \tAverage Intensity\n")

start_time = time.time()
seconds = 30  # collection time
while True:
    ts = time.time()
    elapsed_time = ts - start_time
    intensities = spec.intensities(correct_dark_counts=True, correct_nonlinearity=False)
    # Avg_Intensity = np.mean(intensities[Lambda_1:Lambda_3+1])
    i = 1069  # index of target wavelength(570.9 nm)
    Avg_Intensity = np.mean(intensities[i - 1 : i + 2])  # indexes to 1068, 1069,1070
    write_row(filename, [ts, elapsed_time, Avg_Intensity])
    # time.sleep(0.05)
    if elapsed_time > seconds:
        break
