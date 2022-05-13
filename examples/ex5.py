"""
Created May 2022


Example script to add specimen to a dataset version in the Knowledge Graph Editor


@author: mvanswieten

"""

from getpass import getpass
from metabot import openMINDS_wrapper

w = openMINDS_wrapper()

# Specify the uuid of the dataset version the specimen need to be added to
dsv_uuid = input("What is the uuid of the dataset version you would like to add specimen to? ")

# Ask token for authentication
token = getpass(prompt="Please enter your KG token (or Enter to skip uploading to the KG): ")

# identify the instances that need to be added (this is a list of all the uuids of the specimens you want to add ['uuid_specimen1', 'uuid_specimen2'])
instances2add = input("What are the uuids of the specimen you want to add? Paste the instances in the following format ['uuid_specimen1', 'uuid_specimen2']: ")

# Select the space the instances need to be uploaded to, e.g. dataset
space_name = "dataset"

# Upload the instances in the folder you selected
response = w.add2dsv(instances2add, token, dsv_uuid, space_name)  
