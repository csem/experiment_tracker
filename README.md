# Why
For simplifying visualitation of results collected with Hydra.

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
This repo offers a series of utility functions and templates for creating your own GUI.

# Terminology (Based on WandB):

- **Project**: A collection of one or more experiments. (Each _Project_ has one or more days sub-folders, and then one or more time sub-folders) 
- **Experiment**: A collection of one or more runs. Each experiment contains one or more runs subfolders 
- **Run**: A training of a learning algorithm plus its performance evaluation 

# Structure of the resulting pandas dataframe 
df_example contains an example of pandas dataframe  end result
