# -*- coding: utf-8 -*-
"""
Created Dec 2021
File containing openMINDS_wrapper class
    
Methods:
-------
    importSubjectsFromJSON : 
        import subject metadata from JSON file
    importSubjectsFromCSV : 
        import subject metadata from CSV file
    mergeInfo : 
        merge subject and sample metadata
    makeSubjectCollections : 
        create subject and subject state instances
    makeSampleCollections : 
        create sample and sample state instances
    upload : 
        upload instances to KGE
    delete : 
        delete instances from KGE
@author: mvanswieten
"""

# from itertools import count
import json
# from lib2to3.pgen2 import token
import openMINDS
import openMINDS.version_manager
import pandas as pd
import requests

class openMINDS_wrapper:
    def __init__(self):
        openMINDS.version_manager.init()
        openMINDS.version_manager.version_selection("v3")
        self.helper = openMINDS.Helper()
    
    def findGroup(self, df, group_data):

        groupState = group_data.timePointName.to_list()
        groupName = group_data.name.to_list()

        for i in range(len(df)):
            if df.isPartOf[i] in groupName:
                idx = groupName.index(df.isPartOf[i])
                if not 'isPartOf_uuid' in df.columns:
                    df.insert(i, 'isPartOf_uuid', '')
                df.loc[i, "isPartOf_uuid"] = group_data.specimen_uuid[idx]
        
        for i in range(len(df)):
            if df.descendedFrom[i] in groupState:
                idx = groupState.index(df.descendedFrom[i])
                if not 'descendedFrom_uuid' in df.columns:
                    df.insert(i, 'descendedFrom_uuid', '')
                df.loc[i, "descendedFrom_uuid"] = group_data.state_uuid[idx]
        
        return df


    def makeSubjectCollections(self, df, output_path):
        """
        
        Parameters
        ----------
        df : Pandas DataFrame
            DataFrame containing subject metadata
        output_path : string
            Location files should be saved in
        Returns
        -------
        data : Pandas DataFrame
            DataFrame containing subject metadata including information about 
            the newly generated instances
        """
        kg_prefix = "https://kg.ebrains.eu/api/instances/"
        data = df
        
        uniqueSubs = df.name.unique()

        state_dict = {}
        subject_dict = {} 
        specimen_uuid = []
        state_uuid = []
        for sub in range(len(uniqueSubs)):
            
            # Print the name of the instance
            print("\n Creating instances for subject: " + str(uniqueSubs[sub]) + "\n")
            
            subject_name = uniqueSubs[sub]
                    
            # Define the openMINDS function based on the specimenType
            if df.specimenType[sub] == "subject" :
                statemethod = 'add_core_subjectState'
                subjectmethod = 'add_core_subject'
            elif df.specimenType[sub] == "subjectGroup" :
                statemethod = 'add_core_subjectGroupState'
                subjectmethod = 'add_core_subjectGroup'    
        
            # # initiate the collection into which you will store all metadata instances
            mycol = self.helper.create_collection()

            #### Subject State ####
            
            # Create a subject state name(s) first 
            stateInfo = df[df.name == uniqueSubs[sub]].drop_duplicates('timePointName', keep = 'first').reset_index(drop=True) 
            numberOfStates = len(stateInfo)
            stateName = []
            for state in range(numberOfStates):
                if pd.isnull(stateInfo.timePointName[state]):
                    print(">>> No subject state name defined, making generic one <<<")
                    stateName.append(str(subject_name) + "_" + "state-0" + str(stateInfo.timePoint[state]))
                else:
                    stateName.append(str(stateInfo.timePointName[state]))

            # Create subject state(s)
            states = []  
            for state_num in range(len(stateName)):  
                print("creating state " + str(stateName[state_num]) + " for subject " + str(subject_name))
                state_dict[subject_name] = getattr(mycol, statemethod)(
                    ageCategory = [{"@id" : "https://openminds.ebrains.eu/instances/ageCategory/" + stateInfo.ageCategory[state_num]}])    
                mycol.get(state_dict[subject_name]).lookupLabel = stateName[state_num]
                
                # If state attribute is defined, add to collection
                attributeName = []
                if pd.isnull(stateInfo.attribute[state_num]):
                    print("No subject attribute defined")
                    attribute = None
                    mycol.get(state_dict[subject_name]).attribute = attribute
                else:
                    if stateInfo.attribute[state_num].find(','):
                        for attributes in stateInfo.attribute[state_num].split(","):
                            attributeName.append({"@id": "https://openminds.ebrains.eu/instances/subjectAttribute/" + str(attributes.strip())})
                        mycol.get(state_dict[subject_name]).attribute = attributeName
                        attribute = stateInfo.attribute[state_num]
                    else:
                        attribute = stateInfo.attribute[state_num]
                        mycol.get(state_dict[subject_name]).attribute = [{"@id" : "https://openminds.ebrains.eu/instances/subjectAttribute/" + str(attribute)}]

                states.append({"@id": kg_prefix + state_dict[subject_name].split("/")[-1]})
                state_uuid.append(state_dict[subject_name].split("/")[-1])

                # Add the age of the animal
                if pd.isnull(stateInfo.ageValue[state_num]) and pd.isnull(stateInfo.ageUnit[state_num]):
                    print("No age information defined")
                elif str(stateInfo.ageValue[state_num]).find("-") != -1:
                    ages = stateInfo.ageValue[state_num].split("-")
                    mycol.get(state_dict[subject_name]).age = [{"@type" : "https://openminds.ebrains.eu/core/QuantitativeValueRange",
                                                "minValueUnit" : {"@id": "https://openminds.ebrains.eu/instances/unitOfMeasurement/" + str(stateInfo.ageUnit[state_num])},
                                                "maxValueUnit" : {"@id": "https://openminds.ebrains.eu/instances/unitOfMeasurement/" + str(stateInfo.ageUnit[state_num])}, 
                                                "minValue" : int(ages[0].strip()),
                                                "maxValue" : int(ages[1].strip())
                                                }]
                else:
                    mycol.get(state_dict[subject_name]).age = [{"@type" : "https://openminds.ebrains.eu/core/QuantitativeValue",
                                                                "unit" : {"@id": "https://openminds.ebrains.eu/instances/unitOfMeasurement/" + str(stateInfo.ageUnit[state_num])}, 
                                                                "value" : int(stateInfo.ageValue[state_num])
                                                            }]
                
                #add the weight of the animal
                if pd.isnull(stateInfo.weightValue[state_num]) and pd.isnull(stateInfo.weightUnit[state_num]):
                    print("No weight information defined")
                elif str(stateInfo.weightValue[state_num]).find("-") != -1:
                    weights = stateInfo.weightValue[state_num].split("-")
                    mycol.get(state_dict[subject_name]).weight = [{"@type" : "https://openminds.ebrains.eu/core/QuantitativeValueRange",
                                                "minValueUnit" : {"@id": "https://openminds.ebrains.eu/instances/unitOfMeasurement/" + str(stateInfo.weightUnit[state_num])},
                                                "maxValueUnit" : {"@id": "https://openminds.ebrains.eu/instances/unitOfMeasurement/" + str(stateInfo.weightUnit[state_num])}, 
                                                "minValue" : int(weights[0].strip()),
                                                "maxValue" : int(weights[1].strip())
                                                }]
                else:
                    mycol.get(state_dict[subject_name]).weight = [{"@type" : "https://openminds.ebrains.eu/core/QuantitativeValue",
                                                                "unit" : {"@id": "https://openminds.ebrains.eu/instances/unitOfMeasurement/" + str(stateInfo.weightUnit[state_num])}, 
                                                                "value" : int(stateInfo.weightValue[state_num])
                                                                }]
                
                if pd.isnull(stateInfo.descendedFrom[state_num]):
                    print("No 'descended from' information defined")
                else:
                    if 'descendedFrom_uuid' in stateInfo.columns:
                        descendedState = []
                        for st in range(len(stateInfo.descendedFrom_uuid[state_num])):
                            descendedState.append({"@id": kg_prefix + stateInfo.descendedFrom_uuid[state_num][st]})
                            
                        mycol.get(state_dict[subject_name]).descendedFrom = descendedState

            #### Subject ####
            print("Creating subject " + str(subject_name))

            # Find the strain information if applicable
            if pd.isnull(df.strainName[sub]):
                print("No strain defined")
                strain_info = None
            else:
                if pd.isnull(df.strainAtid[sub]) or not df.strainAtid[sub]:
                    print("No strain identifier found, please check 'strainAtid' or add manually")
                    strain_info = None
                else:
                    strain_atid_url = "https://kg.ebrains.eu/api/instances/" + str(df.strainAtid[sub])
                    strain_info = [{"@id": strain_atid_url}]
                
            # Create the subject and link the subject state
            subject_dict[subject_name] = getattr(mycol, subjectmethod)(
                species = strain_info,
                studiedState = states)
            mycol.get(subject_dict[subject_name]).lookupLabel = str(subject_name)
            
            # If internal identifier is defined, add to collection
            if pd.isnull(df.internalID[sub]):
                print(">>> No internal identifier available <<<")
                internalID = None
            else:
                internalID =  str(df.internalID[sub])
            mycol.get(subject_dict[subject_name]).internalIdentifier = internalID
                
            # If biological sex is defined, add to collection 
            if  pd.isnull(df.biologicalSex[sub]):
                print('No biological sex information available')
                sex = None
                # mycol.get(subject_dict[subject_name]).biologicalSex = sex
            else:
                sex = [{"@id" : "https://openminds.ebrains.eu/instances/biologicalSex/" +  str(df.biologicalSex[sub])}]
            mycol.get(subject_dict[subject_name]).biologicalSex = sex

            if pd.isnull(df.isPartOf[sub]):
                print("Specimen is not part of a group or collection")
            else:
                if 'isPartOf_uuid' in df.columns:
                    mycol.get(subject_dict[subject_name]).isPartOf = [{"@id" : "https://kg.ebrains.eu/api/instances/" + df.isPartOf_uuid[sub]}]
            
            mycol.save(output_path) 
        
            for x in range(numberOfStates):
                specimen_uuid.append(subject_dict[subject_name].split("/")[-1])

        data["specimen_uuid"] = specimen_uuid
        data["state_uuid"] = state_uuid
            
        filename = output_path + df.specimenType[sub] + '_created.csv'
        data.to_csv(filename, index = False, header=True)  
      
        return data

    def makeSampleCollections(self, df, output_path):
        """
        
        Parameters
        ----------
        df : Pandas DataFrame
            DataFrame containing sample metadata
        output_path : string
            Location files should be saved in
        Returns
        -------
        data : Pandas DataFrame
            DataFrame containing sample metadata including information about 
            the newly generated instances
        """
        
        kg_prefix = "https://kg.ebrains.eu/api/instances/"
        data = df
        
        uniqueSamples = df.name.unique()
        state_dict = {}
        sample_dict = {} 
        specimen_uuid = []
        state_uuid = []
        for sample in range(len(uniqueSamples)):
            
            sample_name = uniqueSamples[sample]
            stateInfo = df[df.name == uniqueSamples[sample]].reset_index(drop=True)

            # Select all the states that belong to one sample
            print("\n Creating states for tissue sample " + str(sample_name) + "\n")

            sampleStates = stateInfo.timePointName.to_list()
            
            stateName = []
            states = []  
            # stateIDs = []
            for state in range(len(sampleStates)):

                # Find the names of the sample states, if no name was given, make generic name
                if pd.isnull(stateInfo.timePointName[state]):
                    print(">>> No subject state name defined, making generic one <<<")
                    stateName.append(str(sample_name) + "_" + "state-0" + str(stateInfo.timePoint[state]))
                else:
                    stateName.append(str(sample_name) + "_" + str(stateInfo.timePointName[state]))

                # Define openMINDS function based on specimenType
                if stateInfo.specimenType[state] == "tsc" :
                    statemethod = 'add_core_tissueSampleCollectionState'
                    samplemethod = 'add_core_tissueSampleCollection'
                elif stateInfo.specimenType[state] == "ts" :
                    statemethod = 'add_core_tissueSampleState'
                    samplemethod = 'add_core_tissueSample' 
                
                # initiate the collection into which you will store all metadata instances
                mycol = self.helper.create_collection()

                # Create sample state(s)                    
                print("creating state " + str(stateName[state]))
                state_dict[sample_name] = getattr(mycol, statemethod)()    
                mycol.get(state_dict[sample_name]).lookupLabel = stateName[state]

                if pd.isnull(df.descendedFrom[state]):
                    print("No 'descended from' information defined")
                else:
                    if 'descendedFrom_uuid' in df.columns:
                        mycol.get(state_dict[sample_name]).descendedFrom = [{"@id" : kg_prefix + stateInfo.descendedFrom_uuid[state]}]
                    
                # If state attribute is defined, add to collection
                attribute = []
                if pd.isnull(stateInfo.attribute[state]):
                    print(">>> No state attribute available <<<")
                    attribute = None
                else:
                    if stateInfo.attribute[state].find(','):
                        for attributes in stateInfo.attribute[state].split(","):
                            attribute.append({"@id": "https://openminds.ebrains.eu/instances/tissueSampleAttribute/" + str(attributes.strip())})
                        # mycol.get(state_dict[sample_name]).attribute = attribute
                        # attribute = stateInfo.attribute[state]
                    else:
                        attribute = [{"@id" : "https://openminds.ebrains.eu/instances/tissueSampleAttribute/" + str(stateInfo.attribute[state])}]
                mycol.get(state_dict[sample_name]).attribute = attribute
        
                states.append({"@id": kg_prefix + state_dict[sample_name].split("/")[-1]})
                # stateIDs.append(state_dict[sample_name].split("/")[-1])                 
                state_uuid.append(state_dict[sample_name].split("/")[-1])

                # Save the instance in the output folder
                mycol.save(output_path)     

            # Create the sample and link the sample state
            print("Creating sample " + str(sample_name))
            
            if not stateInfo.strainAtid[state]:
                print("No strain identifier found, please check 'strainAtid' or add manually")
                strain_info = None
                strain_atid = None
            else:
                strain_atid = kg_prefix + str(stateInfo.strainAtid[state])
                strain_info = [{"@id": strain_atid}]
                    
            # check if the origin is an organ or cell type
            if str(stateInfo.origin[state]) == "brain" or str(stateInfo.origin[state]) == "muscle":
                origin = "https://openminds.ebrains.eu/instances/organ/" + str(stateInfo.origin[state])
            else:
                origin = "https://openminds.ebrains.eu/instances/cellType/" + str(stateInfo.origin[state])    
            
            sample_dict[sample_name] = getattr(mycol, samplemethod)(
                species = strain_info,
                type = [{"@id" : "https://openminds.ebrains.eu/instances/tissueSampleType/" + str(stateInfo.sampleType[state])}],
                origin = [{"@id" : origin}],
                studiedState = states)
            mycol.get(sample_dict[sample_name]).lookupLabel = str(sample_name)
        
            # add biological sex if available
            if pd.isnull(stateInfo.biologicalSex[state]):
                print('No biological sex information available')
                sex = None
                # mycol.get(sample_dict[sample_name]).biologicalSex = sex
            else:
                sex = [{"@id" : "https://openminds.ebrains.eu/instances/biologicalSex/" + str(stateInfo.biologicalSex[state])}]  
            mycol.get(sample_dict[sample_name]).biologicalSex = sex
            
            # If internal identifier is defined, add to collection
            if pd.isnull(stateInfo.internalID[state]):
                print(">>> No internal identifier available <<<")
                internalID = None
            else:
                internalID = str(stateInfo.internalID[state])
            mycol.get(sample_dict[sample_name]).internalIdentifier = internalID
            
            # If sample is a tissue sample collection and the quantity is defined, add to collection
            if stateInfo.specimenType[state] == "tsc" :
                if pd.isnull(stateInfo.quantity[state]):
                    print("No quantity defined")
                    quantity = None
                else:
                    quantity = int(stateInfo.quantity[state])
            else:
                # print(">>> No quantity available for tissue sample <<<")
                quantity = None
            mycol.get(sample_dict[sample_name]).quantity = quantity
        
            # If brain region is defined, add to collection
            if pd.isnull(stateInfo.region[state]):
                print("No brain region defined")
                brain_region = None
            else:
                if (stateInfo.region[state].split("_")[0] == "AMBA") or (stateInfo.region[state].split("_")[0] == "WHSSD" and stateInfo.region[state].split("_")[1] in ["v1-01", "v2", "v3-01","v3", "v4"]) or (stateInfo.region[state].split("-")[0] == "JBA"):
                    urlstring = "https://openminds.ebrains.eu/instances/parcellationEntityVersion/"
                elif stateInfo.region[state].split("_")[0] == "WHSSD" or stateInfo.region[state].split("_")[0] == "JBA" or  stateInfo.region[state].split("_")[0] == "DWMA":
                    urlstring = "https://openminds.ebrains.eu/instances/parcellationEntity/"
                region_dict = {}
                brain_region = []
                for region in stateInfo.region[state].split(","):
                    region_dict["@id"] = urlstring + region.strip()
                    brain_region.append(region_dict)
            mycol.get(sample_dict[sample_name]).anatomicalLocation = brain_region
        
            if pd.isnull(df.isPartOf[state]):
                print("Specimen is not part of a group or collection")
            else:
                if 'isPartOf_uuid' in df.columns:
                    mycol.get(sample_dict[sample_name]).isPartOf = [{"@id" : "https://kg.ebrains.eu/api/instances/" + df.isPartOf_uuid[state]}]

            for x in range(len(sampleStates)):
                specimen_uuid.append(sample_dict[sample_name].split("/")[-1])

            # Save the instance in the output folder
            mycol.save(output_path) 

        data["specimen_uuid"] = specimen_uuid
        data["state_uuid"] = state_uuid

        filename = output_path + df.specimenType[sample] + '_created.csv'
        data.to_csv(filename, index = False, header=True)        
   
        return data
    
    def upload(self, instances_fnames, token, space_name):
        """
        
        Parameters
        ----------
        instances_fnames : List 
            list of file paths to instances that need to be uploaded
        token : string
            Authorisation token to get access to the KGE
        space_name : string
            Space that the instances needs to be uploaded to, e.g. "dataset", "common", etc.
        Returns
        -------
        response : dictionary
            For each UUID as response is stored that indications if the upload 
            was successful
        """
        
        hed = {"accept": "*/*",
               "Authorization": "Bearer " + token,
               "Content-Type": "application/json"
               }
        
        # Prefix to upload to the right space
        url = "https://core.kg.ebrains.eu/v3-beta/instances/{}?space=" + space_name
        kg_prefix = "https://kg.ebrains.eu/api/instances/"
        
        new_instances = []
        for fname in instances_fnames:
            with open(fname, 'r') as f:
                new_instances.append(json.load(f))
            f.close()
        
        # Correct the capitalisation in the openMINDS package
        for instance in new_instances:
            atid = kg_prefix + instance["@id"].split("/")[-1]
            instance["@id"] = atid
            if "studiedState" in instance.keys():
                for ss in range(len(instance["studiedState"])):
                    atid = kg_prefix + instance["studiedState"][ss]["@id"].split("/")[-1]
                    instance["studiedState"][ss]["@id"] = atid
            if instance["@type"].endswith("Tissuesamplecollectionstate"):
                splittype = instance["@type"].split("/")[:-1]
                splittype.append("TissueSampleCollectionState")
                instance["@type"] = "/".join(splittype)
            if instance["@type"].endswith("Tissuesamplecollection"):
                splittype = instance["@type"].split("/")[:-1]
                splittype.append("TissueSampleCollection")
                instance["@type"] = "/".join(splittype)
            if instance["@type"].endswith("Tissuesamplestate"):
                splittype = instance["@type"].split("/")[:-1]
                splittype.append("TissueSampleState")
                instance["@type"] = "/".join(splittype)
            if instance["@type"].endswith("Tissuesample"):
                splittype = instance["@type"].split("/")[:-1]
                splittype.append("TissueSample")
                instance["@type"] = "/".join(splittype)
            if instance["@type"].endswith("Subjectstate"):
                splittype = instance["@type"].split("/")[:-1]
                splittype.append("SubjectState")
                instance["@type"] = "/".join(splittype)
        
        # Upload to the KGE
        print("\nUploading instances now:\n")
        
        count = 0
        response = {}    
        for instance in new_instances:
            count += 1
            print("Posting instance " + str(count)+"/"+str(len(new_instances)))
            atid = instance["@id"].split("/")[-1] 
            response[atid] = requests.post(url.format(atid), json=instance, headers=hed)
            if response[atid].status_code == 200:
                print(response[atid], "OK!" )
            elif response[atid].status_code == 409:
                print(response[atid], "Instance already exists")
            elif response[atid].status_code == 401:
                print(response[atid], "Token not valid, authorisation not successful")
            else:
                print(response[atid])
            
            
        return response    
            
    def delete(self, instance_atids, token, space_name):   
        """
        
        Parameters
        ----------
        instances_fnames : List 
            UUIDs of the instances that need to be deleted
        token : string
            Authorisation token to get access to the KGE
        space_name : string
            Space that the instances needs to be deleted from, e.g. "dataset", "common", etc.
        
        Returns
        -------
        response : dictionary
            For each UUID as response is stored that indications if the deletion
            was successful
        """
        
        
        hed = {"accept": "*/*",
               "Authorization": "Bearer " + token
               }
        
        # URL of the space the instances need to be removed from
        url = "https://core.kg.ebrains.eu/v3-beta/instances/{}?space=" + space_name
        
        # Delete the instances
        print("\nDeleting instances now:\n")
        
        count = 0
        response = {}    
        for instance in instance_atids:
            atid = instance.split("\\")[-1] 
            count += 1
            print("Deleting instance " + str(count)+"/"+str(len(instance_atids)))
            response[atid] = requests.delete(url.format(atid), headers=hed)
            if response[atid].status_code == 200:
                print(response[atid].status_code, "OK!" )
            elif response[atid].status_code == 401:
                print(response[atid], "Token not valid, authorisation unsuccessful")
            elif response[atid].status_code == 404:
                print(response[atid], "Instance not found")
            else:
                print(response[atid])
            
        return response

    def add2dsv(self, instances2add, token, dsv_uuid, space_name):
        """
        
        Parameters
        ----------
        instances2add : List 
            UUIDs of the studied specimen that need to be added to the studiedSpecimen section of the dataset version
        token : string
            Authorisation token to get access to the KGE
        dsv_uuid : string
            UUID of the dataset version the specimen needs to be added to
        space_name : string
            Space that the instances needs to be deleted from, e.g. "dataset", "common", etc.
        
        Returns
        -------
        response : dictionary
            For each UUID as response is stored that indications if the deletion
            was successful
        """
        
        hed = {"accept": "*/*",
            "Authorization": "Bearer " + token
            }
            
        # URL of the space the instances need to be removed from
        url = "https://core.kg.ebrains.eu/v3-beta/instances/{}?space=" + space_name
        kg_prefix = "https://kg.ebrains.eu/api/instances/"

        studiedSpecimen = []
        for atid in instances2add:
            studiedSpecimen.append({"@id": kg_prefix + atid.split("\\")[-1] })

        # Create the instance to patch
        instance = {"@context": {"@vocab": "https://openminds.ebrains.eu/vocab/"},
                    "studiedSpecimen": studiedSpecimen
                    }

        response = {}     
        print("Adding specimen now ")
        response[dsv_uuid] = requests.patch(url.format(dsv_uuid), json=instance, headers=hed)
        if response[dsv_uuid].status_code == 200:
            print(response[dsv_uuid].status_code, "OK!" )
        elif response[dsv_uuid].status_code == 401:
            print(response[dsv_uuid], "Token not valid, authorisation unsuccessful")
        elif response[dsv_uuid].status_code == 404:
            print(response[dsv_uuid], "Instance not found")
        else:
            print(response[dsv_uuid])