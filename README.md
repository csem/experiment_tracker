Idea:
This repo should be added as a submodule to any project using Hydra for result visualization.
Then install the repo as:
`pip install -e csem_experimenttracker/`

Goal of this repo: 
1) Offer a way to process hydra-like folder structure 
2) Offer a comprehensive set of plots and template with Streamlit

Terminology (Based on WandB):

_Project_: A collection of one or more experiments. (Each _Project_ has one or more days sub-folders, and then one or more hour sub-folders)

_Experiment_: A collection of one or more runs. Each experiment contains one or more runs subfolders

_runs_: A training of a learning algorithm plus its performance evaluation

