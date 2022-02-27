# -*- coding: utf-8 -*-
"""
Created Feb 2022


Example script to upload instances to the Knowledge Graph Editor


@author: mvanswieten

"""

import glob
import os
from metabot import openMINDS_wrapper

w = openMINDS_wrapper

# Specify the folder where the instances are stored
file_location = os.getcwd()
token = input("Please enter your KG token: ")
instances_fnames = glob.glob(file_location + "*\\*", recursive = True)

# Select the space the instances need to be uploaded to, e.g. dataset
space_name = "dataset"

# Upload the instances in the folder you selected
response = w.upload(instances_fnames, token, space_name)  