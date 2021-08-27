# Overview
This tool allows to work collect and visualize easily scripts runned with Hydra. With it you can sort runs and experiment per tag, hyperparameters, group, etc.
You can also export and visualize them by different ways using streamlit and plotly. 
Here a working example http://138.131.217.125:8501/

# Installation 

#### Adding to an existing repo
For adding CSEM_ExperimentTracker as a submodules in a repo for the first time just run:
`git submodule add git@gitlab.csem.local:611/csem_experimenttracker.git`
Then add and commit the two files 

```
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        new file:   .gitmodules
        new file:   csem_experimenttracker
```

#### Cloning from a remote repo containing it
When cloning the repo with a submodule remember to add `--recurse-submodules --remote-submodules` to the git clone command. Otherwise submodules will not be used.

#### Pip Installation
After you have cloned CSEM_ExperimentTracker,  install it with:
`pip install -e csem_experimenttracker/`

# Getting started
## Collect your results
Let's assume you have run an experiment "my_experiment" of 3 runs (see below for the terminology) on 2021-01-26 at 17:07:39. And that, for each run you are saving a npy file and a log file. 

```
my_experiment/
└── 2021-01-26
    └── 17-07-39
        ├── 0
        │   ├── .hydra
        │   │   ├── config.yaml
        │   │   ├── hydra.yaml
        │   │   └── overrides.yaml
        │   ├── lstm_finetuning.log
        │   └── metric.npy
        ├── 1
        │   ├── .hydra
        │   │   ├── config.yaml
        │   │   ├── hydra.yaml
        │   │   └── overrides.yaml
        │   ├── lstm_finetuning.log
        │   └── metric.npy
        ├── 2
        │   ├── .hydra
        │   │   ├── config.yaml
        │   │   ├── hydra.yaml
        │   │   └── overrides.yaml
        │   ├── lstm_finetuning.log
        │   └── metric.npy
        └── multirun.yaml
```

The following code snippets will return a pd.DataFrame containing the parameters for each and the path to your results (i.e. the npy files).

```python
from csem_exptrack import process
loader = process.file_loader.FileLoader(query_string="*.npy")
df = loader.load_folder("my_experiment")
```

if you want to return also the path to your log files you can pass a list instead of a string as parameter to query_string 

```python
from csem_exptrack import process
loader = process.file_loader.FileLoader(query_string=["*.npy","*.log"])
df = loader.load_folder("my_experiment")
```

The returned pd.DataFrame contains the paths of your results relative to the folder where you run your code the parameters, from .hydra/config, of each run.
The pd.DataFrame has hierchical structure, both for columns and rows.
- Columns:
  - Level 0: **Date**: The date of your experiment (i.e. 2021-01-26 17-07-39)
  - Level 1: **Run**: The integer representing the value of your run (0 to 3)
- Rows:
  - Level 0: **param_df**: Can be Hyperparameters, Dataset, Other, Path. See below "formatting the hydra file"
  - Level 1: **Parameters**: Parameters for each subgroup

You can know more about hierchical pandas dataframe here: 
https://pandas.pydata.org/pandas-docs/stable/user_guide/advanced.html

Once you have the pandas dataframe you can do whataver you want with it! Here some examples:
1. Going through each run and load the npy file in a list, with the same order as the pd.DataFrame.
```python
results = [np.load(x,allow_pickle=True) for x in  df.loc[("path",0)]]
```

2. Get all the hyperparameters:
```python
df.loc["hyperparameters"]
```

3. Get all parameters for run 1
```python
df.loc[:, ('2021-01-26 17-07-39', 1)]
```

## Visualize your results
Before starting you should be some what familiar with Streamlit. If you aren't, just spend 20 minutes looking at https://docs.streamlit.io/en/stable/getting_started.html.
This library offers some utility functions for creating CSEM GUI and visualize your results nicely.
Current supported plots:
* Parallel Coordinates 
* Confusion Matrix
* Learning Curves

you can use them by importing 
```python
from csem_exptrack.gui import plots
```

### Parallel Coordinates
```python
plots.parallel_coordinates(param_df: pd.DataFrame, perf_df: pd.DataFrame) --> None 
```
param_df: pd.DataFrame mentioned above (i.e. the one you load with process.file_loader).  It must contain a level 0 named "hyperparameters".
perf_df: pd.DataFrmae pandas dataframe with columns the metrics you are interested and with two-level rows with date and runs. The runs must exists in param_df, and can be also a subset. 

Example of perf_df with one single columns:
```python
                       best_accuracy
2021-01-26 17-07-39 0       0.702448
                    1       0.4345
                    2       0.681733
```

These are also valid:
- Subset of runs
```python
                       best_accuracy
2021-01-26 17-07-39 0       0.702448
                    2       0.681733
```
- Multiple metrics 
```python
                       best_accuracy  Reward
2021-01-26 17-07-39 0       0.702448       3
                    2       0.681733       9
```


### Confusion Matrix 
```python
plots.interactive_confusion_matrix(conf: np.array, order: List, colorscale="electric"): --> None
```
This function will display a interactive (i.e. you can hoover over cells for more details) confusion matrix.
Arguments
* conf: 2D np.array representing the confusion matrix. Element on the same row belong to the same class, Element on the same column are predicted to belong to the same class.
Example of conf:
```python
array([[343,   9,  23,  39],
       [  6, 200,   0,   2],
       [ 39,   2, 161,  10],
       [ 59,   2,  25, 108]])
```
343 is the prediction of class 1 given the ground truth is class 1. 6 is the prediction of class 1 given that the ground truth is class 2.

* order: list containing the labels


### Learning Curves


# Terminology (Based on WandB):

- **Project**: A collection of one or more experiments. (Each _Project_ has one or more days sub-folders, and then one or more time sub-folders) 
- **Experiment**: A collection of one or more runs. Each experiment contains one or more runs subfolders 
- **Run**: A training of a learning algorithm plus its performance evaluation 

# Formatting the hydra file
All parameters beloging to an indentation group called "hyperparameters", for instance:
```
hyperparameters:
  lm_bs: 128 
  lm_last_layer_epochs: 7
  lm_all_layers_epochs: 6
```
will appear together in the resulting pd.DataFrame. Same for the "dataset" group.
All the other parameters will be categorized in the "other" group.
Parallel coordinate plots will only look at the hyperparameters group. 

# To Do 
1) Add documentation for learning curves
