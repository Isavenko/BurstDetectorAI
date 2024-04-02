from model import *
import numpy as np
import os
from astropy.io import fits
# from math import round
from filterFile import giveFilteredFileFast
import matplotlib.pyplot as plt
from matplotlib import cm

# This script evaluates an AI model on validation data, and checks the accuracy, false positive, and false negative rate

def load_and_preprocess(file_path, files):
    # Loading data using astropy
    desired_shape=(200,3600)
    with fits.open(file_path) as hdul:
        data = None
        data = hdul[0].data/255  # Access the data from the FITS file
        if data.shape != desired_shape:
            data = None
            return None
        data = giveFilteredFileFast(data)
        return data
    return None

burst_folder = 'data/manuallySorted/bursts'
no_burst_folder = 'data/validation/duds'
desired_shape = (200, 3600)
nTest = 100

burst_files = np.array([os.path.join(burst_folder, file) for file in os.listdir(burst_folder)])
no_burst_files = np.array([os.path.join(no_burst_folder, file) for file in os.listdir(no_burst_folder)])

model = astromodel3()
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

predSum = 0
falseNeg = 0
model.load_weights('models/magnumDingDong.h5')
for i in range(nTest//2):
    datapoint = None
    while datapoint is None:
        datapoint = load_and_preprocess(np.random.choice(burst_files, size=1)[0], burst_files)
    datapoint = np.array([datapoint[:, :, None]])
    prediction = round(model.predict(datapoint)[0][0])
    if prediction == 0:
        falseNeg += 1
        # fig, ax = plt.subplots()
        # ax.imshow(datapoint[0,:,:,0], interpolation='nearest', aspect='auto', cmap=cm.plasma)
        # plt.show()
    predSum += prediction
    print(f'calculating burst average ({i+1} / {nTest//2})\r', end='')
print('\nburst avg: ', predSum/(nTest//2))
print(f'false negative: {falseNeg}')


predSum = None
predSum = 0
falsePos = 0
for i in range(nTest//2): 
    datapoint = None
    while datapoint is None:
        datapoint = load_and_preprocess(np.random.choice(no_burst_files, size=1)[0], no_burst_files)
    datapoint = np.array([datapoint[:, :, None]])
    prediction = round(model.predict(datapoint)[0][0])
    if prediction == 1:
        falsePos += 1
    predSum += prediction
    print(f'calculating no burst average ({i+1} / {nTest//2})\r', end='')
print('\nno burst avg: ', predSum/(nTest//2))
print(f'false positives: {falsePos}')