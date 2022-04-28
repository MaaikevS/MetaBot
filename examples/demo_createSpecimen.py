# -*- coding: utf-8 -*-
"""
Created Jan 2022


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

from metabot import openMINDS_wrapper

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
fileLocation = fpath + metadata_file

specimenInfo = pd.read_excel(fileLocation)
subjectInfo = specimenInfo.iloc[:,:14]#.drop_duplicates('subjectName', keep = 'first').reset_index(drop=True)
sampleInfo = pd.concat([specimenInfo.iloc[:,14:],subjectInfo.subjectName, subjectInfo.timePointName], axis=1) #specimenInfo.iloc[:,14:].join(subjectInfo.subjectName)

# Choose if you want to create subject, sample or both instances.
answer = 0
while answer not in ["1", "2", "3"]:
    answer = input("Do you want to create 1) subjects, 2) tissue samples, or 3) both? " )
    if answer == "1":
         subject_data = w.makeSubjectCollections(subjectInfo, output_path)
    elif answer == "2":
         a2 = 0
         while a2 not in ["1", "2"]:
             a2 = input("Do you want to create samples from a 1) JSON file or 2) csv file ? " ) 
             if a2 == "1":
                 subject_file = input("What is the name of your subject file (e.g. subjects.json)? ")
                 input_path = fpath + subject_file
                 subjectInfo = w.importSubjectsFromJSON(input_path)
                 merged_df = w.mergeInfo(subjectInfo, sampleInfo)
                 sample_data = w.makeSampleCollections(merged_df, output_path)
             elif a2 == "2":
                 subject_file = input("What is the name of your subject file (e.g. subjects.csv)? ")
                 input_path = fpath + subject_file 
                 subjectInfo = w.importSubjectsFromCSV(input_path)
                 merged_df = w.mergeInfo(subjectInfo, sampleInfo)
                 sample_data = w.makeSampleCollections(merged_df, output_path)
    elif answer == "3":
         subject_data = w.makeSubjectCollections(subjectInfo, output_path)
         merged_df = w.mergeInfo(subject_data, sampleInfo)
         sample_data = w.makeSampleCollections(merged_df, output_path)

# Saving an overview file in the output folder for future reference
print("\nOverview file is saved in the output folder \n")

# Upload instances to the KGE
answer = input("Would you like to upload the instances you created to the KGE? yes (y) or no (n) " ) 

if answer == "y":
    token = getpass(prompt="Please enter your KG token (or Enter to skip uploading to the KG): ")
    instances_fnames = glob.glob(output_path + "*\\*", recursive = True)

    print("\nUploading data now:\n")
    
    if token != "":
        response = w.upload(instances_fnames, token, space_name = "dataset")  
        
elif answer == "n":
    print("\nDone!")