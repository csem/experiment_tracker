# Why
For simplifying visualitation of results collected with Hydra.
Here a working example http://138.131.217.125:8501/

# Installation 

For adding CSEM_ExperimentTracker as a submodules in a repo for the first time just run:
`git submodule add git@gitlab.csem.local:611/csem_experimenttracker.git`
Then add and commit the two files 

```
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        new file:   .gitmodules
        new file:   csem_experimenttracker
```

When cloning the repo with a submodule remember to add `--recurse-submodules --remote-submodules` to the git clone command. Otherwise submodules will not be used.


Then install the repo as:
`pip install -e csem_experimenttracker/`

Goal of this repo: 
1) Offer a way to process hydra-like folder structure 
2) Offer a comprehensive set of plots and template with Streamlit

# How to use it
This module offers a series of utility functions and templates for creating your own GUI.
You should be some what familiar with Streamlit. If you aren't, just spend 20 minutes looking at https://docs.streamlit.io/en/stable/getting_started.html

CSEM_ExperimentTracker is module tha comprises of two main sub-modules (plus a bunch of utilities .py files)
- GUI. Here will find modules about implementing graphical widget, plots and GUI utilities.

- Process. Here you will modules processing hydra like structure.  base_loader.py is the abstract class that needs to be implemented depeding for your specific type of experiment. You can find this already for lightning.

Start by importing `csem_exptrack`

# Terminology (Based on WandB):

- **Project**: A collection of one or more experiments. (Each _Project_ has one or more days sub-folders, and then one or more time sub-folders) 
- **Experiment**: A collection of one or more runs. Each experiment contains one or more runs subfolders 
- **Run**: A training of a learning algorithm plus its performance evaluation 

# Important

If you want to use the parallel coordinate plots all yours hyperparameters should be indented and included in hyperparameters. Example:
```
hyperparameters:
  lm_bs: 128 # try between 128 and bigger
  lm_last_layer_epochs: 7 # try between 1 and 20
  lm_all_layers_epochs: 6 # try between 1 and 20
```

Adding a key called random_seed will allow you to average plots

# Structure of the resulting pandas dataframe 
df_example contains an example of pandas dataframe  end result
