""" 
Author: Nandita Bhaskhar
General utility functions
"""

import os
import argparse

import json
import logging

import string
import random

def strToBool(v):
    ''' Converts commonly inputted bool strings to type bool '''
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
		
def noneOrStr(value):
    ''' Converts string 'None' to None type '''
    if value == 'None':
        return None
    return value

def idGenerator(size=6, chars=string.ascii_uppercase + string.digits):
    # size=6, chars=string.ascii_uppercase + string.digits
    ''' Generate random string ids for directory names  '''
    return ''.join(random.choice(chars) for _ in range(size))
	
def safeID(dirPath):
    ''' Return a directory name which has not been created yet '''
    str = idGenerator()
    if str not in os.listdir(dirPath):
        return str
    else:
        safeID(dirPath)

def safeMkdir(path):
    ''' Create a directory if there isn't one already '''
    try:
        #print('Creating directory: ' + path)
        os.mkdir(path)
    except OSError:
        #print('Directory already exists')
        pass

class Params():
    """ 
    Class that loads hyperparameters from a json file.
    Example:
    ```
    params = Params(json_path)
    print(params.learning_rate) # access parameters from the file
    params.learning_rate = 0.5  # change the value of learning_rate in params
    params.save(json_path) # update the json file
    params.dict # access the dictionary defined by params
    ```
    """

    def __init__(self, json_path):
        self.update(json_path)

    def save(self, json_path):
        '''Saves parameters to json file'''
        with open(json_path, 'w') as f:
            json.dump(self.__dict__, f, indent=4)

    def update(self, json_path):
        '''Loads parameters from json file'''
        with open(json_path) as f:
            params = json.load(f)
            self.__dict__.update(params)

    @property
    def dict(self):
        '''Gives dict-like access to Params instance by `params.dict['learning_rate']`'''
        return self.__dict__

		
def setLogger(log_path):
    '''
    Sets the logger to log info in terminal and file `log_path`.
    In general, it is useful to have a logger so that every output to the terminal is saved
    in a permanent file. Here we save it to `expDir/train.log`.
    Example:
    ```
    logging.info("Starting training...")
    ```
    Args:
        log_path: (string) where to log
    '''
	
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Logging to a file
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
        logger.addHandler(file_handler)

        # Logging to console
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(stream_handler)

def saveDictToJson(d, json_path):
    '''
    Saves dict of floats in json file
    Args:
        d: (dict) of float-castable values (np.float, int, float, etc.)
        json_path: (string) path to json file
    '''
    with open(json_path, 'w') as f:
        # Need to convert the values to float for json (it doesn't accept np.array, np.float, )
        d = {k: float(v) for k, v in d.items()}
        json.dump(d, f, indent=4)
        
        
class RunningAverage():
    """A simple class that maintains the running average of a quantity
    
    Example:
    ```
    loss_avg = RunningAverage()
    loss_avg.update(2)
    loss_avg.update(4)
    loss_avg() = 3
    ```
    """
    def __init__(self):
        self.steps = 0
        self.total = 0
    
    def update(self, val):
        self.total += val
        self.steps += 1
    
    def __call__(self):
        return self.total/float(self.steps)

class IterMeter(object):
    """keeps track of total iterations"""
    def __init__(self):
        self.val = 0

    def step(self):
        self.val += 1

    def get(self):
        return self.val