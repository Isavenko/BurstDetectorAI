import numpy as np

# This python file contains functions which use a function to give a file a probability of containing a burst based on a certain paremeter.
# StandardProb looks at how the maximum value in an image affects probability of there being a burst
# AIProb looks at how the output of our AI affects probability of there being a burst
# These functions were creaeted using regression on a table of data

def standardProb(value):
    return (0.823456)/(1+(6.05996*np.exp(-0.0435157*value)))

def AIProb(value):
    return ((0.772466)/(1+(52.1864*np.exp(-77.6598*value))))+0.228011