# -*- coding: utf-8 -*-
"""
Created Feb 2022


Example script for creating subject instances


@author: mvanswieten

"""
import os
import pandas as pd
from datetime import datetime
from metabot import openMINDS_wrapper

# Store metadata
data = {}
data["subjectType"] = "subject"
data["subjectName"] = "sub-01"
data["subjectInternalID"] = None
data["subjectStateNum"] = 1
data["subjectStateNames"] = None
data["strainName"] = None
data["strainAtid"] = None
data["biologicalSex"] = "female"
data["ageCategory"] = "adult"
data["subjectAttribute"] = "awake, control"

df = pd.DataFrame(data, index=['i',])

# Make output folder is it does not exist yet
output_path = "createdInstances" + "_" + datetime.now().strftime("%d%m%Y_%H%M") + "\\"
if os.path.isdir(output_path):
    print("Output folder already exists")
else:
    print("Output folder does not exist, making folder")        
    os.mkdir(output_path) 
    
# Call the openMINDS wrapper
w = openMINDS_wrapper()
    
# Create subjects instances based on the data provided (overview file is saved automatically)
subject_data = w.makeSubjectCollections(df, output_path)    



