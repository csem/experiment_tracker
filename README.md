# Overview
This tool allows to work collect and visualize easily scripts runned with Hydra. With it you can sort runs and experiment per tag, hyperparameters, group, etc.
You can also export and visualize them by different ways using streamlit and plotly. 

# Installation
1) Clone the repo via: `git clone https://github.com/csem/experiment_tracker.git`
2) install it with:
`pip install -e experiment_tracker/`

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

The following code snippets will return a pd.DataFrame containing the parameters for each and the path to all files with npy suffix.

```python
import experiment_tracker
df = experiment_tracker.load_project(base_path="experiments", query_string="*.ckpt", logic="multirun") # logic can either be "multirun" [if hydra is run with -m flag] or "singlerun" 
```

You can also specify "filter_hms" argument in order to collect only day in a specific day
```python
df = experiment_tracker.load_project(base_path="final_results/train_wc_uncond", query_string="results.json", filter_hms="2022-10-09")
```

if you want to return also the path to your log files you can pass a list instead of a string as parameter to query_string 

```python
from experiment_tracker import process
loader = process.file_loader.FileLoader(query_string=["*.npy","*.log"])
df = loader.load_project("my_experiment")
```

The returned pd.DataFrame contains the paths of your results relative to the folder where you run your code the parameters, from .hydra/config, of each run.
The pd.DataFrame has hierchical structure for rows.
- Rows:
  - Level 0: **Date**: The date of your experiment (i.e. 2021-01-26 17-07-39)
  - Level 1: **Run**: The integer representing the value of your run (0 to 3)
- Columns:
  - Level 0: **Parameters**: Hydra config variables + [collected_path_0,..,collected_path_n]

You can know more about hierchical pandas dataframe here: 
https://pandas.pydata.org/pandas-docs/stable/user_guide/advanced.html

Once you have the pandas dataframe you can do whataver you want with it! Here some examples:
1. Going through each run and load the npy file in a list, with the same order as the pd.DataFrame.
```python
results = [np.load(x,allow_pickle=True) for x in  df.loc[:,collected_path_0]]
```


2. Get all parameters for run 1
```python
df.loc[ ('2021-01-26 17-07-39', 1),:]
```



# Terminology:

- **Project**: A collection of one or more experiments. (Each _Project_ has one or more days sub-folders, and then one or more time sub-folders) 
- **Experiment**: A collection of one or more runs. Each experiment contains one or more runs subfolders 
- **Run**: A training of a learning algorithm plus its performance evaluation 


