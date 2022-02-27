# -*- coding: utf-8 -*-
"""
Created Feb 2022


Example for importing subject metadata from a JSON file and saving it as a .csv file


@author: mvanswieten

"""

import os
from metabot import openMINDS_wrapper
from datetime import datetime

w = openMINDS_wrapper()

# Make an output folder based on the current data and time
now = datetime.now()
output_path = "createdInstances" + "_" + now.strftime("%d%m%Y_%H%M") + "\\"
if os.path.isdir(output_path):
    print("Output folder already exists")
else:
    print("Output folder does not exist, making folder")        
    os.mkdir(output_path) 

# Import subject information from a json file
input_path = "example_subjects.json"
subjectInfo = w.importSubjectsFromJSON(input_path)

# Save an overview of the imported subject information with the sample data
filename = output_path + 'subjectsInfo.csv'
subjectInfo.to_csv(filename, index = False, header=True)    



