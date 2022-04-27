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

import json
import openMINDS
import openMINDS.version_manager
import pandas as pd
import requests

class openMINDS_wrapper:
    def __init__(self):
        openMINDS.version_manager.init()
        openMINDS.version_manager.version_selection("v3")
        self.helper = openMINDS.Helper()

    def importSubjectsFromJSON(self, input_path):
        """
        
        Parameters
        ----------
        input_path : string
            path to where the JSON file is located.
        Returns
        -------
        df : pandas dataframe
            DataFrame with subject metadata.
        
        """
        df = pd.DataFrame([])
                
        with open(input_path, 'r') as f:
            sub_list = json.load(f)
        f.close()
        print("Number of subjects in this dataset: " + str(len(sub_list))) 
        
        idx = 0
        for sub in sub_list:
            
            if not 'strainAtid' in df.columns:
                df.insert(idx, 'strainAtid', '')
            if not 'biologicalSex' in df.columns:    
                df.insert(idx, 'biologicalSex', '')
            if not 'subjectAtid' in df.columns:
                 df.insert(idx, 'subjectAtid', '')
            if not 'studiedState' in df.columns:
                 df.insert(idx, 'studiedState', '')
                                                          
            df.loc[idx, "subjectName"] = sub["lookupLabel"]
            df.loc[idx, "studiedState"] = sub["studiedState"][0].split("/")[-1]
            if "species" in sub:
                if sub["species"][0] == []:
                    df.loc[idx, "strainAtid"] = None
                else:
                    df.loc[idx, "strainAtid"] = sub["species"][0].split("/")[-1]
            else:
                df.loc[idx, "strainAtid"] = None
            if "biologicalSex" in sub:
                df.loc[idx, "biologicalSex"] = sub["biologicalSex"][0].split("/")[-1]
            else:
                df.loc[idx, "biologicalSex"] = None
            df.loc[idx, "subjectAtid"] = sub["id"].split("/")[-1]  

            idx += 1                   
                
        return df
    
    def importSubjectsFromCSV(self, input_path):
        
        """
        
        Parameters
        ----------
        input_path : string
            path to where the CSV file is located.
        Returns
        -------
        df : pandas dataframe
            DataFrame with subject metadata.
        
        """
        
        df = pd.read_csv(input_path)
        print("Number of subjects in this dataset: " + str(len(df.subjectName.unique())))   
            
        return df
    
    def mergeInfo(self, subjectInfo, sampleInfo):
        
        """
        
        Parameters
        ----------
        subjectInfo : pandas dataframe
            DataFrame with subject metadata
        sampleInfo : pandas dataframe
            DataFrame with sample metadata
        Returns
        -------
        df : pandas dataframe
            Merged DataFrame with subject and sample metadata.
        
        """
        
        sub_list = subjectInfo.subjectName.unique()
        
        df = sampleInfo.copy(deep=True)
        
        for sub in range(len(sub_list)):
            
            idxs = df.index[df['sampleName'].str.contains(subjectInfo.subjectName[sub])]
        
            for i in idxs:
            
                if not 'strainAtid' in df.columns:
                    df.insert(i, 'strainAtid', '')
                if not 'biologicalSex' in df.columns:    
                    df.insert(i, 'biologicalSex', '')
                if not 'subjectAtid' in df.columns:
                     df.insert(i, 'subjectAtid', '')
                if not 'studiedState' in df.columns:
                     df.insert(i, 'studiedState', '')
                    
                df.loc[i, "subjectName"]  = subjectInfo.subjectName[sub]
                df.loc[i, "studiedState"] = subjectInfo.studiedState[sub]
                if "strainAtid" in subjectInfo.columns:
                    df.loc[i, "strainAtid"] = subjectInfo.strainAtid[sub]
                else:
                    df.loc[i, "strainAtid"] = None
                if "biologicalSex" in subjectInfo.columns:
                    df.loc[i, "biologicalSex"]  = subjectInfo.biologicalSex[sub]
                else:
                    df.loc[i, "biologicalSex"]  = None
                df.loc[i, "subjectAtid"] = subjectInfo.subjectAtid[sub]
                
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
        
        
        data = pd.DataFrame([])
        
        state_dict = {}
        subject_dict = {} 
        
        for i in range(len(df.subjectName)):
            
            # Print the name of the instance
            print("\n Creating instances for subject: " + str(df.subjectName[i]) + "\n")
            
            subject_name = df.subjectName[i]
                    
            # Define the openMINDS function based on the specimenType
            if df.subjectType[i] == "subject" :
                statemethod = 'add_core_subjectState'
                subjectmethod = 'add_core_subject'
            elif df.subjectType[i] == "subjectGroup" :
                statemethod = 'add_core_subjectGroupState'
                subjectmethod = 'add_core_subjectGroup'    
        
            # # initiate the collection into which you will store all metadata instances
            mycol = self.helper.create_collection()

            #### Subject State ####
            
            # Create a subject state name(s) first    
            stateName = []
            if pd.isnull(df.subjectStateNames[i]):
                print(">>> No subject state names defined, making generic ones <<<")
                if pd.isnull(df.subjectStateNum[i]):
                    print(">>> Number of subject states is not defined, please check <<<")
                    return
                else: 
                    for num in range(int(df.subjectStateNum[i])):
                        if num < 10:
                            stateName.append(str(subject_name) + "_" + "state-0" + str(num+1))
                        else: 
                            stateName.append(str(subject_name) + "_" + "state-" + str(num+1))
                    
            else:
                if pd.isnull(df.subjectStateNum[i]):
                    print(">>> Number of states is not defined, please check <<<")
                    return
                else:
                    # Split up the state names if there is more than one state
                    if df.subjectStateNames[i].find(','):
                        # First check if there are enough names given for the number of states
                        if df.subjectStateNum[i] != len(df.subjectStateNames[i].split(",")):
                            print("Number of states does not match the number of state names given! Please check ")
                            return
        
                        for stateNames in df.subjectStateNames[i].split(","):
                            stateName.append(str(subject_name) + "_" + stateNames.strip())
                    else:
                        # Check if the number of states matches the number of given state names
                        if df.subjectStateNum[i] != len(df.subjectStateNames[i]):
                            print("Number of states does not match the number of state names given! Please check ")
                            return
                        stateName.append(str(subject_name) + "_" + df.subjectStateNames[i])

            # Create subject state(s)
            states = []  
            stateIDs = []
            for state_num in range(len(stateName)):  
                print("creating state " + str(stateName[state_num]))
                state_dict[subject_name] = getattr(mycol, statemethod)(
                    ageCategory = [{"@id" : "https://openminds.ebrains.eu/instances/ageCategory/" + df.ageCategory[i]}])    
                mycol.get(state_dict[subject_name]).lookupLabel = stateName[state_num]
                
                # If state attribute is defined, add to collection
                attributeName = []
                if pd.isnull(df.subjectAttribute[i]):
                    print(">>> No state attribute available <<<")
                    attribute = None
                    mycol.get(state_dict[subject_name]).attribute = attribute
                else:
                    if df.subjectAttribute[i].find(','):
                        for attributes in df.subjectAttribute[i].split(","):
                            attributeName.append({"@id": "https://openminds.ebrains.eu/instances/subjectAttribute/" + str(attributes.strip())})
                        mycol.get(state_dict[subject_name]).attribute = attributeName
                        attribute = df.subjectAttribute[i]
                    else:
                        attribute = df.subjectAttribute[i]
                        mycol.get(state_dict[subject_name]).attribute = [{"@id" : "https://openminds.ebrains.eu/instances/subjectAttribute/" + str(attribute)}]

                states.append({"@id": state_dict[subject_name]})
                stateIDs.append(state_dict[subject_name].split("/")[-1])
             
            # Add the age of the animal
            if pd.isnull(df.ageValue[i]) and pd.isnull(df.ageUnit[i]):
                print("No age information available")
                age = None
            else:
                age = str(int(df.ageValue[i])) + " " + str(df.ageUnit[i])
                mycol.get(state_dict[subject_name]).age = [{"@type" : "https://openminds.ebrains.eu/core/QuantitativeValue",
                                                            "unit" : {"@id": "https://openminds.ebrains.eu/instances/unit/" + str(df.ageUnit[i])}, 
                                                            "value" : int(df.ageValue[i])
                                                           }]
            
            #add the weight of the animal
            if pd.isnull(df.weightValue[i]) and pd.isnull(df.weightUnit[i]):
                print("No weight information available")
                weight = None
            else:
                weight = str(int(df.weightValue[i])) + " " + str(df.weightUnit[i])
                mycol.get(state_dict[subject_name]).weight = [{"@type" : "https://openminds.ebrains.eu/core/QuantitativeValue",
                                                               "unit" : {"@id": "https://openminds.ebrains.eu/instances/unit/" + str(df.weightUnit[i])}, 
                                                               "value" : int(df.weightValue[i])
                                                               }]
            #### Subject ####
            
            print("Creating sample " + subject_name)

            # Find the strain information if applicable
            if pd.isnull(df.strainName[i]):
                print(">>> No strain defined <<<")
                strain_name = None
                strain_atid = None
                strain_info = None
            else:
                strain_name = df.strainName[i]
                strain_atid = df.strainAtid[i]
                if pd.isnull(strain_atid) or not strain_atid:
                    print("No strain identifier found, please check 'strainAtid' or add manually")
                    strain_info = None
                else:
                    strain_atid_url = "https://kg.ebrains.eu/api/instances/" + str(strain_atid)
                    strain_info = [{"@id": strain_atid_url}]
                
            # Create the subject and link the subject state
            subject_dict[subject_name] = getattr(mycol, subjectmethod)(
                species = strain_info,
                studiedState = states)
            mycol.get(subject_dict[subject_name]).lookupLabel = str(subject_name)
            
            # If internal identifier is defined, add to collection
            if pd.isnull(df.subjectInternalID[i]):
                print(">>> No internal identifier available <<<")
                internalID = None
            else:
                internalID =  df.subjectInternalID[i]
            mycol.get(subject_dict[subject_name]).internalIdentifier = internalID
                
            # If biological sex is defined, add to collection 
            if  pd.isnull(df.biologicalSex[i]):
                print('No biological sex information available')
                sex = None
                mycol.get(subject_dict[subject_name]).biologicalSex = sex
            else:
                sex = df.biologicalSex[i]
                mycol.get(subject_dict[subject_name]).biologicalSex = [{"@id" : "https://openminds.ebrains.eu/instances/biologicalSex/" +  str(df.biologicalSex[i])}]  

            data = data.append(pd.DataFrame({"subjectName" : subject_name,
                                             "subjectAtid" : subject_dict[subject_name].split("/")[-1],
                                             "subjectInternalID" : internalID,
                                             "studiedState" : ','.join(stateIDs),
                                             "subjectStateNames" : ','.join(stateName),
                                             "strainName" : strain_name,
                                             "strainAtid" : strain_atid,
                                             "biologicalSex" : sex,
                                             "age" : age,
                                             "weight" : weight,
                                             "subjectAttribute" : attribute},                
                                            index=[0]), 
                               ignore_index=True)
            
            mycol.save(output_path) 
            
            filename = output_path + 'subjectsCreated.csv'
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
        
        data = pd.DataFrame([])
        
        state_dict = {}
        sample_dict = {} 
        
        sub_list = df.subjectName.unique()
        
        for sub in sub_list:
            # Only select the samples of one subject
            samples = df[df['sampleName'].str.contains(sub)].reset_index(drop=True)
            
            for i in range(len(samples)):
               
                # Print the instance name
                if pd.isnull(str(samples.sampleName[i])):
                    print("\n Creating instances for subject " + str(sub) + " tissue sample " + str(i + 1) + "\n")
                else:
                    print("\n Creating instances for subject " + str(sub) + " tissue sample " + str(samples.sampleName[i]) + "\n")
                
                sample_name = samples.sampleName[i]

                # Define openMINDS function based on specimenType
                if samples.specimenType[i] == "tsc" :
                    statemethod = 'add_core_tissueSampleCollectionState'
                    samplemethod = 'add_core_tissueSampleCollection'
                elif samples.specimenType[i] == "ts" :
                    statemethod = 'add_core_tissueSampleState'
                    samplemethod = 'add_core_tissueSample'    
            
                # # initiate the collection into which you will store all metadata instances
                mycol = self.helper.create_collection()
            
                # Create a sample state name(s) first    
                stateName = []
            
                if pd.isnull(samples.sampleStateNames[i]):
                    print(">>> No state names defined, making generic ones <<<")
                    if pd.isnull(samples.sampleStateNum[i]):
                        print(">>> Number of states is not defined, please check <<<\n")
                        return
                    else: 
                        for num in range(int(samples.sampleStateNum[i])):
                            if num < 10:
                                stateName.append(str(sample_name) + "_" + "state-0" + str(num+1))
                            else: 
                                stateName.append(str(sample_name) + "_" + "state-" + str(num+1))
                        
                else:
                    if pd.isnull(samples.sampleStateNum[i]):
                        print(">>> Number of states is not defined, please check <<<\n")
                        return
                    else:
                        # Split up the state names if there is more than one state
                        if samples.sampleStateNames[i].find(','):
                            # First check if there are enough names given for the number of states
                            if samples.sampleStateNum[i] != len(samples.sampleStateNames[i].split(",")):
                                print(">>> Number of states does not match the number of state names given! Please check <<<\n")
                                return
            
                            for stateNames in samples.sampleStateNames[i].split(","):
                                stateName.append(str(sample_name) + "_" + stateNames.strip())
                        else:
                            # Check if the number of states matches the number of given state names
                            if samples.sampleStateNum[i] != len(samples.sampleStateNames[i]):
                                print(">>> Number of states does not match the number of state names given! Please check <<<\n")
                                return
                            stateName.append(str(sample_name) + "_" + samples.sampleStateNames[i])
            
                # Create sample state(s)
                states = []  
                stateIDs = []
                for state_num in range(len(stateName)):
                    
                    print("creating state " + str(stateName[state_num]))
                    state_dict[sample_name] = getattr(mycol, statemethod)()    
                    mycol.get(state_dict[sample_name]).lookupLabel = stateName[state_num]
                    mycol.get(state_dict[sample_name]).descendedFrom = [{"@id" : "https://kg.ebrains.eu/api/instances/" + df.studiedState[i]}]
                    
                    # If state attribute is defined, add to collection
                    attributeName = []
                    if pd.isnull(samples.sampleAttribute[i]):
                        print(">>> No state attribute available <<<")
                        attribute = None
                    else:
                        if samples.sampleAttribute[i].find(','):
                            for attributes in samples.sampleAttribute[i].split(","):
                                attributeName.append({"@id": "https://openminds.ebrains.eu/instances/tissueSampleAttribute/" + str(attributes.strip())})
                            mycol.get(state_dict[sample_name]).attribute = attributeName
                            attribute = samples.sampleAttribute[i]
                        else:
                            attribute = samples.sampleAttribute[i]
                            mycol.get(state_dict[sample_name]).attribute = [{"@id" : "https://openminds.ebrains.eu/instances/tissueSampleAttribute/" + str(attribute)}]
            
                    states.append({"@id": state_dict[sample_name]})
                    stateIDs.append(state_dict[sample_name].split("/")[-1])
                 
                
                # Create the sample and link the sample state
                print("Creating sample " + sample_name)
                
                if not df.strainAtid[i]:
                    print("No strain identifier found, please check 'strainAtid' or add manually")
                    strain_info = None
                    strain_atid = None

                else:
                    strain_atid = df.strainAtid[i]
                    strain_atid_url = "https://kg.ebrains.eu/api/instances/" + str(strain_atid)
                    strain_info = [{"@id": strain_atid_url}]
                        
                # check if the origin is an organ or cell type
                if str(samples.origin[i]) == "brain" or str(samples.origin[i]) == "muscle":
                    origin = "https://openminds.ebrains.eu/instances/organ/" + str(samples.origin[i])
                else:
                    origin = "https://openminds.ebrains.eu/instances/cellType/" + str(samples.origin[i])    
                
                sample_dict[sample_name] = getattr(mycol, samplemethod)(
                    species = strain_info,
                    type = [{"@id" : "https://openminds.ebrains.eu/instances/tissueSampleType/" + str(samples.sampleType[i])}],
                    origin = [{"@id" : origin}],
                    studiedState = states)
                mycol.get(sample_dict[sample_name]).lookupLabel = str(sample_name)
            
                # add biological sex if available
                if pd.isnull(df.biologicalSex[i]):
                    print('No biological sex information available')
                    sex = None
                    mycol.get(sample_dict[sample_name]).biologicalSex = sex
                else:
                    mycol.get(sample_dict[sample_name]).biologicalSex = [{"@id" : "https://openminds.ebrains.eu/instances/biologicalSex/" + str(df.biologicalSex[i])}]  
                
                # If internal identifier is defined, add to collection
                if pd.isnull(samples.sampleInternalID[i]):
                    print(">>> No internal identifier available <<<")
                    internalID = None
                else:
                    internalID = samples.sampleInternalID[i]
                mycol.get(sample_dict[sample_name]).internalIdentifier = internalID
                
                # If sample is a tissue sample collection and the quantity is defined, add to collection
                if samples.specimenType[i] == "tsc" :
                    if pd.isnull(samples.quantity[i]):
                        print(">>> No quantity available <<<")
                        quantity = None
                    else:
                        quantity = int(samples.quantity[i])
                    mycol.get(sample_dict[sample_name]).quantity = quantity
                else:
                    print(">>> No quantity available for tissue sample <<<")
                    quantity = None
            
                # If brain region is defined, add to collection
                if pd.isnull(samples.region[i]):
                    print(">>> No brain region available <<<")
                    brain_region = None
                else:
                    if (samples.region[i].split("_")[0] == "AMBA") or (samples.region[0].split("_")[0] == "WHSSD" and samples.region[0].split("_")[1] in ["v1-01", "v2", "v3-01","v3", "v4"]) or (samples.region[0].split("-")[0] == "JBA"):
                        urlstring = "https://openminds.ebrains.eu/instances/parcellationEntityVersion/"
                    elif samples.region[i].split("_")[0] == "WHSSD" or samples.region[i].split("_")[0] == "JBA" or  samples.region[i].split("_")[0] == "DWMA":
                        urlstring = "https://openminds.ebrains.eu/instances/parcellationEntity/"
                    region_dict = {}
                    brain_region = []
                    for region in samples.region[i].split(","):
                        region_dict["@id"] = urlstring + region.strip()
                        brain_region.append(region_dict)
                mycol.get(sample_dict[sample_name]).anatomicalLocation = brain_region
               
                # Store all the information in an overview file
                data = data.append(pd.DataFrame({"subjectName" : df.subjectName,
                                                 "subjectAtid" : df.subjectAtid,
                                                 "studiedState" : df.studiedState,
                                                 "sampleName" : str(sample_name),
                                                 "sampleInternalID" : internalID,
                                                 "sampleStateNames" : ','.join(stateName),
                                                 "sampleStateAtid" : ','.join(stateIDs),
                                                 "sampleAtid" :  sample_dict[sample_name].split("/")[-1],
                                                 "brainRegion" : samples.region[i],
                                                 "quantity" : quantity,
                                                 "sampleAttribute" : attribute},                
                                                index=[0]),
                                   ignore_index=True)
                
                # Save the instance in the output folder
                mycol.save(output_path) 
          
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
                atid = kg_prefix + instance["studiedState"][0]["@id"].split("/")[-1]
                instance["studiedState"][0]["@id"] = atid
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
        for atid in instance_atids:
            count += 1
            print("Posting instance " + str(count)+"/"+str(len(instance_atids)))
            response[atid] = requests.delete(url.format(atid), headers=hed)
            if response[atid] == 200:
                print(response[atid], "OK!" )
            elif response[atid] == 401:
                print(response[atid], "Token not valid, authorisation unsuccessful")
            else:
                print(response[atid])
            
        return response