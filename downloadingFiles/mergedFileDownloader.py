import bs4
import requests
import os
from parseEvents import getEvents
import tempfile
import filterViewer
from astropy.io import fits
from astropy.utils.data import get_pkg_data_filename
from astropy.visualization import astropy_mpl_style
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.patches as patches
from matplotlib.widgets import RectangleSelector
from datetime import datetime
from matplotlib.backend_bases import MouseButton
# import cv2 
import scipy as sp

# This script is useful for manually sorting data
# For every burst, it downloads all recordings which happen within that time period
# It overlays all recordings from all stations, making bursts more visible, if they happen simulatenously on mutiple stations. 
# You can drag a rectangle over the burst to see which stations are responsible for the burst
# If you press middle click, the loudest station in the selected region will be marked for download.
# When the viewer is closed, all selected stations are downloaded, and a new burst is opened.

bursts = getEvents()

MAINPATH = 'http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/2023/'

# monthResponse = requests.get(MAINPATH)
# monthData = bs4.BeautifulSoup(monthResponse.text, 'html.parser')
# monthLinks = monthData.find_all('a')[5:]

# # for i in range(12):
# #     dayResponse = requests.get(MAINPATH + monthLinks[i].get_text('href'))
# #     dayData = bs4.BeautifulSoup(dayResponse.text, 'html.parser')
# #     dayLinks = dayData.find_all('a')[5:]
# #     for day in dayLinks:
# #         response = requests.get(MAINPATH + monthLinks[i].get_text('href') + day.get_text('href'))
# #         data = bs4.BeautifulSoup(response.text, 'html.parser')
# #         links = data.find_all('a')[5:]
# #         for link in links:
# #             filename = link.get_text('href')
# #             file = requests.get(MAINPATH + monthLinks[i].get_text('href') + day.get_text('href') + filename)
# #             with open(f'data/duds/{filename}', mode='wb') as f1:
# #                 f1.write(file.content)
# #                 print(filename, 'downloaded')

class ImageViewer:
    def __init__(self, data, names, filename):
        self.data = data
        self.timestring = names[0].split("_")[1][:4] + "/" + names[0].split("_")[1][4:6] + "/" + names[0].split("_")[1][6:] + " " + names[0].split("_")[2][:2] + ":" + names[0].split("_")[2][2:4]
        self.stationNames = names
        self.isStationSelected = [False] * len(names)
        
        self.modifiableData = data
        self.selectionCounter = 0
        self.image = np.sum(data,axis=0)
        self.fig = plt.figure()
        self.axs = self.fig.add_subplot(1,2,1)
        self.ax = self.fig.add_subplot(1,2,2)
        self.fig.tight_layout()
        self.sigma = [0,3]
        blurredImage = sp.ndimage.gaussian_filter(self.image, self.sigma, mode='constant')
        self.shownImage = self.axs.imshow(blurredImage, interpolation='nearest', aspect='auto', cmap=cm.magma)
        self.selector = RectangleSelector(self.axs, self.select_callback,
                                        useblit=True,
                                        button=[1],  # disable middle button
                                        minspanx=5, minspany=5,
                                        spancoords='pixels',
                                        interactive=True)
        plt.connect('button_press_event', self.on_click)
        self.imageLayerSums = []
        for i in range(self.data.shape[0]):
            self.imageLayerSums.append(np.sum(self.data[i]))
        sortedzip = sorted(zip(self.imageLayerSums,self.stationNames,self.isStationSelected))
        self.ax.pie([i[0] for i in sortedzip],labels=[i[1].split("_")[0] for i in sortedzip],startangle=90,wedgeprops={"edgecolor":"k",'linewidth': 1, 'antialiased': True}, explode=[i[2]*0.2 for i in sortedzip])
        self.sortedStationNames = [i[1] for i in sortedzip]
        plt.title(self.timestring)

    def select_callback(self, eclick, erelease):
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        self.imageLayerSums = []
        for i in range(self.data.shape[0]):
            self.imageLayerSums.append(np.sum(self.data[i][round(y1):round(y2),round(x1):round(x2)]))
        self.modifiableData = np.copy(self.data)
        for i in range(self.data.shape[0]):
            self.modifiableData[i] *= self.imageLayerSums[i] * len(self.imageLayerSums) / sum(self.imageLayerSums)
        blurredImage = sp.ndimage.gaussian_filter(np.sum(self.modifiableData,axis=0), self.sigma, mode='constant')
        self.shownImage.set_data(blurredImage)
        # self.axs.set_title([i[1] for i in sorted(zip(imageLayerSums,self.stationNames))])
        self.ax.clear()
        sortedzip = sorted(zip(self.imageLayerSums,self.stationNames,self.isStationSelected))
        self.ax.pie([i[0] for i in sortedzip],labels=[i[1].split("_")[0] for i in sortedzip],startangle=90,wedgeprops={"edgecolor":"k",'linewidth': 1, 'antialiased': True}, explode=[i[2]*0.2 for i in sortedzip])
        self.sortedStationNames = [i[1] for i in sortedzip]
        plt.title(self.timestring)
        self.fig.canvas.draw_idle()
        self.selectionCounter = 0
        # print(f"({x1:3.2f}, {y1:3.2f}) --> ({x2:3.2f}, {y2:3.2f})")

    def on_click(self, event):
        if event.button is MouseButton.RIGHT:
            blurredImage = sp.ndimage.gaussian_filter(self.image, self.sigma, mode='constant')
            self.shownImage.set_data(blurredImage)
            # self.axs.set_title([i[1] for i in sorted(zip(imageLayerSums,self.stationNames))])
            self.ax.clear()
            self.imageLayerSums = []
            for i in range(self.data.shape[0]):
                self.imageLayerSums.append(np.sum(self.data[i]))
            sortedzip = sorted(zip(self.imageLayerSums,self.stationNames,self.isStationSelected))
            self.ax.pie([i[0] for i in sortedzip],labels=[i[1].split("_")[0] for i in sortedzip],startangle=90,wedgeprops={"edgecolor":"k",'linewidth': 1, 'antialiased': True}, explode=[i[2]*0.2 for i in sortedzip])
            self.sortedStationNames = [i[1] for i in sortedzip]
            plt.title(self.timestring)
            self.fig.canvas.draw_idle()
            self.selectionCounter = 0
        if event.button is MouseButton.MIDDLE:
            topStationIndex = self.stationNames.index(self.sortedStationNames[len(self.isStationSelected) - 1 - self.selectionCounter])
            self.isStationSelected[topStationIndex] = not self.isStationSelected[topStationIndex]
            self.selectionCounter += 1
            self.ax.clear()
            sortedzip = sorted(zip(self.imageLayerSums,self.stationNames,self.isStationSelected))
            self.ax.pie([i[0] for i in sortedzip],labels=[i[1].split("_")[0] for i in sortedzip],startangle=90,wedgeprops={"edgecolor":"k",'linewidth': 1, 'antialiased': True}, explode=[i[2]*0.2 for i in sortedzip])
            plt.title(self.timestring)
            self.fig.canvas.draw_idle()

for burst in bursts:
    # try:
    month = burst[0][1]
    day = burst[0][2]
    hour = burst[0][3]
    minute = burst[0][4]
    minuteEnd = burst[1][4]
    stations = burst[3]
    
    finalImage = []
    names = []

    if month < 10:
        if day<10:
            url = f'http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/2023/0{month}/0{day}/'
        else:
            url = f'http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/2023/0{month}/{day}/'
    else:
        if day<10:
            url = f'http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/2023/{month}/0{day}/'
        else:
            url = f'http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/2023/{month}/{day}/'
            
    response = requests.get(url)
    data = bs4.BeautifulSoup(response.text, 'html.parser')
    
    # for i in range(5, len(data.find_all('a'))):
    links = data.find_all('a')[5:]
    for link in links:
        filename = link.get_text('href')
        checkHour = int(filename.split('_')[2][0:2])
        checkMinute = int(filename.split('_')[2][2:4])
        # print(f'checking at time: {checkHour}:{checkMinute}', )
        if int(hour) == checkHour and int(minute)//15 * 15 == checkMinute:
            response = requests.get(url+link['href'])
            # print("test")
            f1 = tempfile.NamedTemporaryFile(suffix=".fit.gz",dir="./temps/",delete=False)
            f1.write(response.content)
            f1.close()
            image_data_db = fits.getdata(f1.name, ext=0)/255
            if image_data_db.shape[0] != 200: continue
            if image_data_db.shape[1] != 3600: continue
            # if abs(image_data_db.shape[1] - 3600) < 5: continue
            for i in range(image_data_db.shape[0]):
                image_data_db[i] -= np.median(image_data_db[i])
            image_data_db = np.clip(image_data_db, 0, 0.02)
            for i in range(image_data_db.shape[0]):
                image_data_db[i] -= 3 * np.mean(image_data_db[i])
            image_data_db = np.clip(image_data_db, 0, 0.02)
            finalImage.append(image_data_db[:194,:])
            names.append(filename)
            # print(filename)
            os.unlink(f1.name)
    
    finalImageArray = np.stack(finalImage)
    imageViewer = ImageViewer(finalImageArray,names,filename)
    
    plt.show()
    for fi in range(len(imageViewer.stationNames)):
        if imageViewer.isStationSelected[fi]:
            response = requests.get(url+imageViewer.stationNames[fi])
            with open("./data/manuallySorted/bursts/"+imageViewer.stationNames[fi],"wb") as f:
                f.write(response.content)
                print("Saved File", f)
        # axs.add_patch(patches.Rectangle(((int(minute)-checkMinute)*240, 0), (int(minuteEnd)-int(minute))*-240, 200, linewidth=2, edgecolor='r', facecolor='none'))
        # plt.title(f1)
        
    # except TypeError:
    #     continue

