# MetaBot #
*Using the openMINDS package to create instances automatically*

MetaBot is a simple package that allows you to automatically generate openMINDS compatible metadata instances, without the need to know the functionalities of the openMINDS package. Metadata can be imported from a JSON file (for subject metadata), CSV file (for subject metadata), a template xlsx file (for both subjects and sample metadata) or by directly defining it in a python dictionary.

## Installation ##

### Prerequisites ###
1. **Python version=>3.6** \
    For installing Python, go to: https://www.python.org/downloads/
    ​
    Alternatively, you may install Anaconda: https://www.anaconda.com/distribution/
    (UiO users: Anaconda is available from the Software Center.)

2. **openMINDS Package** \
    The openMINDS Python package is a small library that allows you the dynamic usage of openMINDS metadata models and schemas in your Python application for generating your own collection of openMINDS conform metadata representations (instances) as JSON-LDs.

    The official versions are available at the [Python Package Index](https://pypi.org/project/openMINDS/) and can be installed using pip install in the command line:

    ``pip install openMINDS``

    The latest unstable version is available on [this GitHub](https://github.com/HumanBrainProject/openMINDS).


### Installing MetaBot ###

Install the package with the following command in the parent directory

``pip3 install . ``

For an editable version, use the following command

``pip3 install -e .``


## Code examples ##

- In examples/ex1.py we create subject instances with the metadata that is defined in the example script.

- In examples/ex2.py we create sample instances with the metadata that is defined in the example script.

- In examples/ex3.py we create subject and sample instances with the metadata that is defined in the example script.

- In examples/ex4.py we import subject metadata from a JSON file (example_subjects.json) and save it as a CSV file.

- In examples/ex5.py we upload generated instances to the Knowledge Graph editor via the API.

- In examples/demo_createSpecimen.py we provide an user-friendly step by step guide to generating instances from a specimen_template macro enabled excel file (e.g. example_specimen.xlsx). Additional information can be found in the instruction document "instructions_demo".

### Additional information metadata variables ###
Required fields are indicated with *.

#### Subject Information ####
- ``subjectType*:`` Choose subject or subject group
- ``subjectName*:`` Choose the name of the subject or subject group. This will become the lookupLabel in the editor.
- ``subjectInternalID:`` specify the name, if left empty, no internal identifier will be added.
- ``strainName:`` Choose a strain that is currently already in the system (these are "semi-controlled terms at the moment"). If you want to add a strain that is not already in the system, leave this blank.
- ``strainAtid:`` DO NOT fill in this field. This field will be filled in automatically based on the strain name that is chosen.
- ``subjectStateNum*:`` number of the states for a particular subjects.
- ``subjectStateName:`` if left empty, states are named as follows: "state-01", "state-02", etc. For any other name, please define the name here and separate multiple names with a comma.
- ``biologicalSex:`` Enter the biological sex of the subject. If unknown, leave blank.
- ``ageCategory*:`` Choose the age category from the dropdown list.
- ``subjectAttribute:`` Choose a subject attribute from the dropdown list. Leave empty if not applicable.

#### Sample information ####
- ``subjectName*:`` Define the name of the subject or subject group that is already in the editor (corresponds to the query of the specimen (see instructions below)) or that is newly created (see instructions above).
- ``subjectAtid:`` Give the subject UUID to include in the overview.
- ``studiedState:`` To link a sample to a studied state of a subject, fill in the UUID of the studied state. If samples are generated from a JSON or CSV file, or together with subjects this will be filled in automatically.
- ``specimenType*:``
  "tsc" = tissue sample collection,
  "ts" = tissue samples
- ``sampleName*:`` Choose the name of the subject or subject group. This will become the lookupLabel in the editor. A good naming convention includes the subject ID, e.g. "sub-01"; any unique features, e.g. the brain region "layer1"; and the sample type, e.g. "tsc". Following this example, the sampleName would be "sub-01_layer1_tsc".
- ``sampleInternalID:`` specify the name, if left empty, no internal identifier will be added.
- ``sampleType*:`` Choose the type of sample from the dropdown list, e.g. tissueSlice or singleCell.
- ``brainRegion:`` Select the brain region the sample is anchored to. Check [SANDS extension](https://humanbrainproject.github.io/openMINDS/v3/) for proper notation. Include everything starting with "AMBA" or "WHS". This will be used to figure out if parcellationEntity or parcellationEntityVersion needs to be used.
- ``origin:`` Select the origin of the samples. This could be organ (e.g. brain), or cellType (e.g. neuron).
- ``quantity:`` define the number of samples in the collection (only applies to tsc)
- ``sampleStateNum*:`` define the number of states, value should be at least 1
- ``sampleStateNames:`` if left empty, states are named as follows: "state-01", "state-02", etc. For any other name, please define the name here and separate multiple names with a comma.
- ``sampleAttribute:`` define attribute of the sample here: choose between "stained" or "unstained".

For more information about what controlled terms are available, see the [wiki](https://humanbrainproject.github.io/openMINDS/v3/).

### Contributors ###

Maaike M.H. van Swieten (mvanswieten@outlook.com)

### License ###

GNU LGPL, version 3.
