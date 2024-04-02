from model import *
import numpy as np
import os
from astropy.io import fits
# from math import round
from filterFile import giveFilteredFileFast
import matplotlib.pyplot as plt
from matplotlib import cm

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

burst_folder = 'data/validation/bursts'
no_burst_folder = 'data/validation/duds'
desired_shape = (200, 3600)

burst_files = np.array([os.path.join(burst_folder, file) for file in os.listdir(burst_folder)])
no_burst_files = np.array([os.path.join(no_burst_folder, file) for file in os.listdir(no_burst_folder)])

model = astromodel3()
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

model.load_weights('models/model05.h5')

predList = []

predSum = 0
falseNeg = 0

print("Starting")
for i in range(1000):
    datapoint = None
    while datapoint is None:
        datapoint = load_and_preprocess(np.random.choice(burst_files, size=1)[0], burst_files)
    datapoint = np.array([datapoint[:, :, None]])
    prediction = model.predict(datapoint)[0][0]
    predList.append(prediction)
    if i%500 == 499:
        plt.hist(predList, bins=50)
        plt.show()

with open('AIBurst.npy', 'wb') as f:
    np.save(f, np.array(predList))