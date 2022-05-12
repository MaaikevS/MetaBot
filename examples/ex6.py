# -*- coding: utf-8 -*-
"""
Created Feb 2022


Example script to upload instances to the Knowledge Graph Editor


@author: mvanswieten

"""

import glob
import os
from getpass import getpass
from metabot import openMINDS_wrapper

w = openMINDS_wrapper()

# Specify the folder where the instances are stored
file_location = os.getcwd()
fpath = input("Please define you path: ")
     
fpath = fpath + "\\" 
os.chdir(fpath)
token = getpass(prompt="Please enter your KG token (or Enter to skip uploading to the KG): ")
instances_fnames = glob.glob(fpath + "*\\*", recursive = True)

# Select the space the instances need to be uploaded to, e.g. dataset
space_name = "dataset"

# Upload the instances in the folder you selected
response = w.delete(instances_fnames, token, space_name)  