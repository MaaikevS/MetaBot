# -*- coding: utf-8 -*-

"""
Created Feb 2022


Example script for creating subject and tissue sample instances


@author: mvanswieten

"""

import os
import pandas as pd
from datetime import datetime
from metabot import openMINDS_wrapper

# Initialise empty dataframe to store metadata in
data = {}

# Fill in the metadata for the subject
data["subjectType"] = "subject"
data["subjectName"] = "sub-01"
data["subjectInternalID"] = ""
data["subjectStateNum"] = 1
data["subjectStateNames"] = ""
data["strainName"] = ""
data["strainAtid"] = ""
data["biologicalSex"] = "female"
data["ageCategory"] = "adult"
data["subjectAttribute"] = "awake, control"

# Fill in the metadata for the sample
data["specimenType"] = "tsc"
data["sampleName"] = "sub-01_layer1"
data["sampleInternalID"] = ""
data["sampleType"] = "tissueSlice"
data["region"] = "WHSSD_brain"
data["origin"] = "brain"
data["quantity"] = 10
data["sampleStateNum"] = 2
data["sampleStateNames"] = "vglut1, vgat"
data["sampleAttribute"] = "stained"

df = pd.DataFrame(data, index=[0])

# Make output folder is it does not exist yet
output_path = "createdInstances" + "_" + datetime.now().strftime("%d%m%Y_%H%M") + "\\"
if os.path.isdir(output_path):
    print("Output folder already exists")
else:
    print("Output folder does not exist, making folder")        
    os.mkdir(output_path) 
    
# Call the openMINDS wrapper
w = openMINDS_wrapper()
    
# Create subjects instances based on the data provided
subject_data = w.makeSubjectCollections(df, output_path) 

# join the new information in a new df
df_merged = pd.concat([df,subject_data.studiedState, subject_data.subjectAtid], axis=1)

# Create sample instances based on the data provided
sample_data = w.makeSampleCollections(df_merged, output_path)  


  