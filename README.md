# MetaBot #
*Using the openMINDS package to create instances automatically*

MetaBot is a simple package that allows you to automatically generate openMINDS compatible metadata instances, without the need to know the functionalities of the openMINDS package. Metadata can be imported from a template xlsx file (for both subjects and sample metadata) or by directly defining it in a python dictionary.

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

- In examples/ex3.py we upload generated instances to the Knowledge Graph editor (via the API).

- In examples/ex4.py we deleted generated instances that are already uploaded to the Knowledge Graph editor (via the API).

- In examples/ex5.py we add generated instances for specimen to a dataset version in the Knowledge Graph editor (via the API).

- In examples/demo_createSpecimen.py we provide an user-friendly step by step guide to generating instances from a specimen_template excel file (e.g. specimen_template.xlsx). The template file makes it clear which fields can be filled in for a particular specimen (e.g. a subject does not have a "sampleType"). Additional information can be found in the instruction document "instructions_demo".

### Additional information metadata variables ###
Required fields are indicated with *.

#### Specimen information ####
- ``specimenType*:``
"tsc" = tissue sample collection,
"ts" = tissue samples
"subject" = individual subject
"subject group" = a group of individuals with a common characteristic
- ``name*:`` Choose the name of the subject or subject group. This will become the lookupLabel in the editor.
- ``internalID:`` specify the name, if left empty, no internal identifier will be added.
- ``strainName:`` Choose a strain that is currently already in the system (these are "semi-controlled terms at the moment"). If you want to add a strain that is not already in the system, leave this blank.
- ``strainAtid:`` DO NOT fill in this field. This field will be filled in automatically based on the strain name that is chosen.
- ``timePoint*:`` number of the states for a particular subjects.
- ``timePointName:`` if left empty, states are named as follows: "state-01", "state-02", etc. For any other name, please define the name here and separate multiple names with a comma.
- ``biologicalSex:`` Enter the biological sex of the subject. If unknown, leave blank.
- ``ageCategory*:`` Choose the age category from the dropdown list.
- ``ageValue:`` Define the age value
- ``ageUnit:`` Choose the age unit from the dropdown list.
- ``weightValue:`` Define the weight value
- ``weightUnit:`` Choose the weight unit from the dropdown list.
- ``pathology:``  Choose the pathology (disease or disease model) from the dropdown list.
- ``attribute:`` Choose a subject attribute from the dropdown list. Leave empty if not applicable.
- ``region:`` Select the brain region the sample is anchored to. Check [SANDS extension](https://humanbrainproject.github.io/openMINDS/v3/) for proper notation. Include everything starting with "AMBA" or "WHS". This will be used to figure out if parcellationEntity or parcellationEntityVersion needs to be used.
- ``origin:`` Select the origin of the samples. This could be organ (e.g. brain), or cellType (e.g. neuron).
- ``quantity:`` define the number of samples in the collection (only applies to tsc)
- ``isPartOf:`` If a subject or tissue sample is part of a subject group or tissue sample collection, respectively, define the name of the group here.
- ``descendedFrom:`` If the specimen descends from another specimen (e.g. tissue sample from subject), define the state of the specimen it descends from.

For more information about what controlled terms are available, see the [wiki](https://humanbrainproject.github.io/openMINDS/v3/).

### Contributors ###

Maaike M.H. van Swieten (mvanswieten@outlook.com)

### License ###

GNU LGPL, version 3.
