from statisticalTools.standardpred import isBurst
import os
import numpy as np
from filterViewer import viewFile

# Similar to predict.py, this file checks the accuracy of conventional algorithms in false positive and false negative rates

dud_folder = 'data/duds'
burst_folder = 'data/bursts'
dud_files = np.array([os.path.join(dud_folder, file) for file in os.listdir(dud_folder)])
burst_files = np.array([os.path.join(burst_folder, file) for file in os.listdir(burst_folder)])

n = 100

tpr = 0
fpr = 0
for i in range(n//2):
    fileChoice = np.random.choice(burst_files)
    viewFile(fileChoice)
    if isBurst(fileChoice):
        tpr += 1
    else:
        fpr += 1

print("Out of", n//2, "bursts,", tpr, "were labelled correctly")

tnr = 0
fnr = 0
for i in range(n//2):
    fileChoice = np.random.choice(burst_files)
    viewFile(fileChoice)
    if isBurst(fileChoice):
        fnr += 1
    else:
        tnr += 1
    
print("Out of", n//2, "duds,", tnr, "were labelled correctly")