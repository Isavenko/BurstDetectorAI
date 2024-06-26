from astropy.io import fits
import numpy as np
from model import *
import os
from tensorflow.keras.utils import Sequence
import tensorflow as tf
import os
from multiprocessing import shared_memory, Process, Event
from time import sleep
import psutil
import matplotlib.pyplot as plt
from filterFile import giveFilteredFileFast

# This file is responsbible for traning an AI which can predict bursts in fits files

# This data filler runs on a different CPU core, which allows data to be loaded from storage into memory independent of data being loaded from memory to GPU
# This function runs continously while training
def dataFiller(shmx, datashape, shmy, labelshape, firstLoadEvent):
    datax = np.ndarray(datashape, dtype=np.float16, buffer=shmx.buf)
    datay = np.ndarray(labelshape, dtype=np.float16, buffer=shmy.buf)
    # load data into memory
    # print('loading data to memory')
    n = datashape[0]

    burst_folder = 'data/bursts'
    no_burst_folder = 'data/duds'
    desired_shape = (200, 3600)

    burst_files = np.array([os.path.join(burst_folder, file) for file in os.listdir(burst_folder)])
    no_burst_files = np.array([os.path.join(no_burst_folder, file) for file in os.listdir(no_burst_folder)])
   
    blockNr = 0
    while True:        
        for i in range(n//2):
            datapoint = load_and_preprocess(np.random.choice(burst_files, size=1)[0], burst_files)
            while datapoint is None:
                datapoint = load_and_preprocess(np.random.choice(burst_files, size=1)[0], burst_files)
            datax[i*2] = datapoint
            datay[i*2] = [1]
            datapoint = load_and_preprocess(np.random.choice(no_burst_files, size=1)[0], no_burst_files)
            while datapoint is None:
                datapoint = load_and_preprocess(np.random.choice(no_burst_files, size=1)[0], no_burst_files)
            datax[i*2+1] = datapoint
            datay[i*2+1] = [0]
        blockNr += 1
        print(f'\n\033[92mLoaded Block {blockNr} Into Memory\033[0m')
        firstLoadEvent.set()

        # print(datax.shape, datay.shape) #for debugging
        # print('data size: ', datax.size * datax.itemsize / 1073741824, 'labels size: ', datay.size * datay.itemsize / 1073741824)

# This function does a similar task to the dataFiller, but runs only once, instead of continuously
# This function used to continously load data, however since now the validation data is smaller, there is no longer a memory restriction, meaning that all data can be loaded at once into memory
def validationFiller(validationx, validationy, validationamount):
    n = validationamount

    burst_folder = 'data/validation/bursts'
    no_burst_folder = 'data/validation/duds'
    # desired_shape = (200, 3600)

    burst_files = np.array([os.path.join(burst_folder, file) for file in os.listdir(burst_folder)])
    no_burst_files = np.array([os.path.join(no_burst_folder, file) for file in os.listdir(no_burst_folder)])
        
    for i in range(n//2):
        datapoint = load_and_preprocess(np.random.choice(burst_files, size=1)[0], burst_files)
        while datapoint is None:
            datapoint = load_and_preprocess(np.random.choice(burst_files, size=1)[0], burst_files)
        validationx[i*2] = datapoint[:,:,None]
        validationy[i*2] = [1]
        datapoint = load_and_preprocess(np.random.choice(no_burst_files, size=1)[0], no_burst_files)
        while datapoint is None:
            datapoint = load_and_preprocess(np.random.choice(no_burst_files, size=1)[0], no_burst_files)
        validationx[i*2+1] = datapoint[:,:,None]
        validationy[i*2+1] = [0]
    print('Loaded Validation Data Into Memory')

# This function reads a .fits file and checks whether it is corrupt, and if it has the desired shape 
def load_and_preprocess(file_path, files):
    # Loading data using astropy
    desired_shape=(200,3600)
    with fits.open(file_path) as hdul:
        try:
            data = np.array(hdul[0].data, dtype=np.float16)/255  # Access the data from the FITS file
        except TypeError:
            print(f'\n\033[91mCannot Load Corrupt File {file_path}\033[0m')
            return None
        if data.shape != desired_shape:
            data = None
            return None
        data = giveFilteredFileFast(data)
        return data
    return None

# This function runs on the main CPU core and feeds data slowly from memory into the GPU.
class CustomDataGenerator(Sequence):
    def __init__(self, datax, datay, n, batch_size):
        self.datax = datax
        self.datay = datay
        self.n = n
        self.batch_size = batch_size
        
        # list all files in the folders
        self.burst_files = [os.path.join(burst_folder, file) for file in os.listdir(burst_folder)]
        self.no_burst_files = [os.path.join(no_burst_folder, file) for file in os.listdir(no_burst_folder)]
                     
        # Determine the number of batches based on the smaller of the two sets
        self.num_batches = min(len(self.burst_files), len(self.no_burst_files)) // self.batch_size

    def __len__(self):
        return self.num_batches

    def __getitem__(self, index):
        rand = np.random.randint(self.n, size=(self.batch_size))
        batch_data = np.array([self.datax[i] for i in rand]).astype(np.float16)[:, :, :, None]
        batch_labels = np.array([self.datay[i] for i in rand]).astype(np.float16)
        
        # print(batch_data.shape, batch_labels.shapes)
        return batch_data, batch_labels
        
    
if __name__ == '__main__':
    firstLoadEvent = Event()
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    
    model = astromodel3()
    desired_shape = (200,3600)
    n = 3000
    validation_size = 150
    batch_size = 8
    dataxbytes = 2 * desired_shape[0] * desired_shape[1] * n
    dataybytes = 2 * n
    validationxbytes = 2 * desired_shape[0] * desired_shape[1] * validation_size
    validationybytes = 2 * validation_size
        
    model.summary()
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    
    burst_folder = 'data/bursts'
    no_burst_folder = 'data/duds'

    
    if(psutil.virtual_memory()[4]-dataxbytes-dataybytes < 100*1024*1024):
        raise "Running this program will leave you with less than 100MB in memory. Lower n before continuing."

    # create buffers for trainign and validation data
    dataxshm = shared_memory.SharedMemory(create=True, size=dataxbytes)
    datax = np.ndarray((n,*desired_shape), dtype=np.float16, buffer=dataxshm.buf)
    datax.fill(0)

    datayshm = shared_memory.SharedMemory(create=True, size=dataybytes)
    datay = np.ndarray((n,1), dtype=np.float16, buffer=datayshm.buf)
    datay.fill(0)
    
    # validationxshm = shared_memory.SharedMemory(create=True, size=validationxbytes)
    validationx = np.ndarray((validation_size,*desired_shape,1), dtype=np.float16)
    validationx.fill(0)
    
    # validationyshm = shared_memory.SharedMemory(create=True, size=validationybytes)
    validationy = np.ndarray((validation_size,1), dtype=np.float16)
    validationy.fill(0)
    
    validationFiller(validationx,validationy,validation_size)

    fillerProcess = Process(target=dataFiller, args=(dataxshm,(n,*desired_shape),datayshm,(n,1),firstLoadEvent))
    fillerProcess.start()
    firstLoadEvent.wait()
    print("First load loaded")
    
    # defining callback to save model after every epoch
    modelNr = len(os.listdir("models")) + 1
    print(f"Weights will be saved under models/model{modelNr}Checkpoint.h5")
    steps_per_epoch = datay.size / batch_size
    save_period = 1
    cp_callback = tf.keras.callbacks.ModelCheckpoint(
        filepath=f'models/model{modelNr}Checkpoint.h5',
        verbose=0,
        save_freq=int(save_period * steps_per_epoch)
    )

    train_generator = CustomDataGenerator(datax=datax, datay=datay, n=n, batch_size=batch_size)
    # validation_generator = CustomDataGenerator(datax=validationx, datay=validationy, n=validation_size, batch_size=batch_size)

    # Train the model using fit_generator
    history = model.fit(train_generator, epochs=200, steps_per_epoch=steps_per_epoch, callbacks=[cp_callback], validation_data=(validationx,validationy))
    
    fillerProcess.terminate()

    # Remove Block A from Memory
    dataxshm.close()
    dataxshm.unlink()
    
    # Visualise loss over time
    # print(history.history.keys())
    # summarize history for accuracy
    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title('Model Accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Test'], loc='upper left')
    plt.show()
    # summarize history for loss
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('Model Loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Test'], loc='upper left')
    plt.show()