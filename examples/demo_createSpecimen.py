# -*- coding: utf-8 -*-
"""
Created Jan 2022
Version 2


Demonstration script for generating instances from metadata that is provided 
in the specimen_template.xlsm file without requiring prior python experience. 
Please answer the questions below.

More information about this file can be found in the instruction document
"Instructions_demo.MD"


@author: mvanswieten
"""

import os
import pandas as pd
import glob
from datetime import datetime
from getpass import getpass

from metabot_v2 import openMINDS_wrapper

w = openMINDS_wrapper()
 
# Define Location of the files
cwd = os.getcwd()
answer = input("Is this where your files are stored: " + cwd + "? yes (y) or no (n) " ) 

if answer == "y":
    fpath = cwd
elif answer == "n":
    fpath = input("Please define you path: ")
     
fpath = fpath + "\\" 
os.chdir(fpath)

# Make output folder is it does not exist yet
now = datetime.now()
output_path = "createdInstances" + "_" + now.strftime("%d%m%Y_%H%M") + "\\"
if os.path.isdir(output_path):
    print("Output folder already exists")
else:
    print("Output folder does not exist, making folder")        
    os.mkdir(output_path) 

# Import the file with the specimen metadata
metadata_file = input("What is the name of your specimen file (e.g. specimen_template.xlsx)? ")
fileLocation = fpath + metadata_file + ".xlsx"

specimenInfo = pd.read_excel(fileLocation)

specimenType = specimenInfo.specimenType.to_list()

if "subjectGroup" in specimenType:
    SG_info = specimenInfo[specimenInfo.specimenType == "subjectGroup"].reset_index(drop=True) 
    SG_data = w.makeSubjectCollections(SG_info, output_path)

if "subject" in specimenType:
    subject_info = specimenInfo[specimenInfo.specimenType == "subject"].reset_index(drop=True) 
    if 'SG_data' in locals():
        subject_info = w.findGroup(subject_info, SG_data)
    subject_data = w.makeSubjectCollections(subject_info, output_path)

if "tsc" in specimenType:
    tsc_info = specimenInfo[specimenInfo.specimenType == "tsc"].reset_index(drop=True) 
    if 'subject_data' in locals():
        tsc_info = w.findGroup(tsc_info, subject_data)
    tsc_data = w.makeSampleCollections(tsc_info, output_path)

if "ts" in specimenType:
    ts_info = specimenInfo[specimenInfo.specimenType == "ts"].reset_index(drop=True)
    if 'tsc_data' in locals():
        ts_info = w.findGroup(ts_info, tsc_data) 
    ts_data = w.makeSampleCollections(ts_info, output_path)

# Saving an overview file in the output folder for future reference
print("\nOverview file is saved in the output folder \n")

# Upload instances to the KGE
answer = input("Would you like to upload the instances you created to the KGE? yes (y) or no (n) " ) 

if answer == "y":
    token = getpass(prompt="Please enter your KG token (or Enter to skip uploading to the KG): ")
    instances_fnames = glob.glob(output_path + "*\\*", recursive = True)

    print("\nUploading data now:\n")
    
    if token != "":
        response_upload = w.upload(instances_fnames, token, space_name = "dataset")  

        # Add specimen to dataset version
        answer = input("Would you like to add the instances you created to a dataset version? yes (y) or no (n) " ) 
        dsv_uuid = input("What is the uuid of the dataset version you would like to add specimen to? ")
        token = getpass(prompt="Please enter your KG token (or Enter to skip uploading to the KG): ")
        
        print("\nAdding specimen to dataset version:" + dsv_uuid + "\n")

        # Retrieve the specimen information of the created instances
        if 'SG_data' in locals():
            SG2add = SG_data.specimen_uuid.unique().tolist()
        else:
            SG2add = []
        if 'subject_data' in locals():
            subjects2add = subject_data.specimen_uuid.unique().tolist()
        else:
            subjects2add = []
        if 'tsc_data' in locals():
            tsc2add = tsc_data.specimen_uuid.unique().tolist()
        else:
            tsc2add = []
        if 'ts_data' in locals():
            ts2add = ts_data.specimen_uuid.unique().tolist()
        else:
            ts2add = []
        
        instances2add = SG2add + subjects2add + tsc2add + ts2add

        response_addition = w.add2dsv(instances2add, token, dsv_uuid, space_name = "dataset")

    else: 
        print("No token provided")  
        
elif answer == "n":
    print("\nDone!")
