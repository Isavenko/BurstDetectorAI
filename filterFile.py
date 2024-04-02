import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndimage
# from matplotlib.widgets import Button, Slider
from astropy.io import fits
from astropy.utils.data import get_pkg_data_filename
from astropy.visualization import astropy_mpl_style
# from matplotlib.patches import Rectangles
# import scipy.stats
import os
from matplotlib import cm

# This script archives different denoising methods for the data we have. 
# This is useful for training the data, for which the data is denoised before use.

burst_folder = 'data/duds'
burst_files = np.array([os.path.join(burst_folder, file) for file in os.listdir(burst_folder)])

# def medianblur(foot):
#     if(foot[0]>foot[1]):
#         if(foot[1]>foot[2]):
#             return foot[1]
#         else:
#             if(foot[0]>foot[2]):
#                 return foot[2]
#             else:
#                 return foot[0]
#     else:
#         if(foot[0]>foot[2]):
#             return foot[0]
#         else:
#             if(foot[1]>foot[2]):
#                 return foot[2]
#             else:
#                 return foot[1]

def viewFile(file):
    # fig, axs = plt.subplots(1,2)
    image_data_db = fits.getdata(file, ext=0)/255
    for i in range(image_data_db.shape[0]):
        image_data_db[i] -= np.median(image_data_db[i])
    image_data_db = np.clip(image_data_db, 0, 0.1)
    rel_db = np.clip(image_data_db, 0, 0.02)
    
    for i in range(rel_db.shape[0]):
        rel_db[i] -= 3 * np.mean(rel_db[i])
    rel_db = np.clip(rel_db, 0, 0.02)\
    
    totalmean = np.mean(rel_db)
    relmean = np.mean(rel_db, axis=0)
    for i in range(rel_db.shape[1]):
        columnvalue = relmean[i]/totalmean
        for j in range(rel_db.shape[0]):
            rel_db[j][i] *= columnvalue
    rel_db = rel_db[:,15:]
    rel_db = (np.clip(rel_db, 0.01, 0.02)-0.01) * 100
    

    filevalue = np.max(np.sum(rel_db, axis=0))
    # if filevalue > 40:
    #     rel_db = ndimage.generic_filter(rel_db, medianblur, footprint=np.ones((1,3)))
    #     filevalue = np.max(np.sum(rel_db, axis=0))

    fig, axs = plt.subplots(1,2)
    axs[1].imshow(rel_db, interpolation='nearest', aspect='auto', cmap=cm.plasma)
    axs[0].imshow(image_data_db, interpolation='nearest', aspect='auto', cmap=cm.plasma)
    plt.title(file)
    plt.show()

    if filevalue>40:
        print("Burst", filevalue, file)
    else:
        print("No Burst", filevalue, file)
    # axs[1].imshow(rel_db, interpolation='nearest', aspect='auto', cmap=cm.plasma)
    # axs[0].imshow(image_data_db, interpolation='nearest', aspect='auto', cmap=cm.plasma)
    # plt.title(file)
    # plt.show()

def giveFilteredFile(fileData):
    # fig, axs = plt.subplots(1,2)
    image_data_db = fileData
    for i in range(image_data_db.shape[0]):
        image_data_db[i] -= np.median(image_data_db[i])
    image_data_db = np.clip(image_data_db, 0, 0.1)
    rel_db = np.clip(image_data_db, 0, 0.02)
    
    for i in range(rel_db.shape[0]):
        rel_db[i] -= 3 * np.mean(rel_db[i])
    rel_db = np.clip(rel_db, 0, 0.02)
    
    totalmean = np.mean(rel_db)
    relmean = np.mean(rel_db, axis=0)
    for i in range(rel_db.shape[1]):
        columnvalue = relmean[i]/totalmean
        for j in range(rel_db.shape[0]):
            rel_db[j][i] *= columnvalue
    rel_db = (np.clip(rel_db, 0.01, 0.02)-0.01) * 100
    
    return rel_db
    # filevalue = np.max(np.sum(rel_db, axis=0))
    # if filevalue > 40:
    #     rel_db = ndimage.generic_filter(rel_db, medianblur, footprint=np.ones((1,3)))
    #     filevalue = np.max(np.sum(rel_db, axis=0))

    # fig, axs = plt.subplots(1,2)
    # axs[1].imshow(rel_db, interpolation='nearest', aspect='auto', cmap=cm.plasma)
    # axs[0].imshow(image_data_db, interpolation='nearest', aspect='auto', cmap=cm.plasma)
    # plt.title(file)
    # plt.show()

def giveFilteredFileFast(fileData):
    # fig, axs = plt.subplots(1,2)
    rel_db = fileData
    for i in range(rel_db.shape[0]):
        rel_db[i] -= np.median(rel_db[i])
    rel_db = np.clip(rel_db, 0, 0.02)

    for i in range(rel_db.shape[0]):
        rel_db[i] -= 3 * np.mean(rel_db[i])
    rel_db = np.clip(rel_db, 0, 0.02)
    
    return rel_db