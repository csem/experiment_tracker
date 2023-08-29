import pandas as pd
import pdb
from collections import OrderedDict
import numpy as np
from typing import List, Dict, Tuple, Any

def topk(series, k=5, min=True):
    target = series.sort_values(ascending=min).index.droplevel(-1)
    seen = set()
    found = [x for x in target if not (x in seen or seen.add(x))][:k]
    if len(found) == 1:
        return found[0]
    return found

def subcolumn_group(df, key):
    b = [True if x in key else False for x in df.columns.get_level_values(-1)] 
    return df.loc[:,b]

def compute_rolling_window_metrics(df, roll=1):
    curr_min = df.loc["epoch"].rolling(roll).mean().min()
    curr_max = df.loc["epoch"].rolling(roll).mean().max()
    tmp = pd.concat([curr_min, curr_max],axis=1).T
    fin = []
    for x in set(df.columns.droplevel(-1)):
        tmp_df = tmp[x]
        tmp_df.index = ["roll_min","roll_max"]
        tmp_df.columns = pd.MultiIndex.from_tuples([x + (i,) for i in tmp_df.columns])
        fin.append(tmp_df)
    fin = pd.concat(fin,axis=1)
    fin.index = pd.MultiIndex.from_tuples([("metric",x) for x in fin.index])
    res = pd.concat([df,fin])
    res = res[df.columns].copy()  
    return res
   
    
def list_available_dates(df):
    if df.columns.get_level_values(0).dtype == '<M8[ns]':
        date = df.columns.get_level_values(0)
        return date.unique()
    elif df.columns.get_level_values(1).dtype == '<M8[ns]':
        date = df.columns.get_level_values(1)
        return date.unique()


def list_available_days(df):
    if df.columns.get_level_values(0).dtype == '<M8[ns]':
        date = df.columns.get_level_values(0).normalize()
        return date.unique()
    elif df.columns.get_level_values(1).dtype == '<M8[ns]':
        date = df.columns.get_level_values(1).normalize()
        return date.unique()

def return_exp_based_on_datetime(df,date,time=None):
    type_table = -1
    if df.columns.get_level_values(0).dtype == '<M8[ns]':
        if not time:
            return df[date]
        else:
            return df[date + " " + time]
    elif df.columns.get_level_values(1).dtype == '<M8[ns]':
        if not time:
            bool_date = df.columns.get_level_values(1).normalize() == date
        else: 
            bool_date = df.columns.get_level_values(1) == date + " " + time
        return df.loc[:,bool_date]

def is_unique(s):
    a = s.to_numpy() 
    return (a[0] == a).all()

def groupby_random_seed(df, keys_metrics):
    """This function groups runs that shares the random seed"""
    values = list(df.index.droplevel([1]))
    if "epoch" in values:
        df = df.drop("epoch")
    if "metrics" in values:
        df = df.drop("metrics")
    if "metric" in values:
        df = df.drop("metric") 
    df_tmp = df.T
    df_tmp.dropna(axis=1,inplace=True)
    groups = {}
    available_lines = set()
    for k in keys_metrics:
        group = []
        imp_idx = [("hyperparameters",x) for x in  list(df.loc["hyperparameters"].index)]
        for _, values in df_tmp.groupby(by=imp_idx):
            runs = set(values.index)
            cols = [idx for idx, x in enumerate(df.columns) if (x in runs)]
            group.append(cols) 
            available_lines.add(str(dict(values.iloc[0])))
        groups[k] = (group)
    return groups, available_lines

def find_identical_runs(param_df, attributes: List[Tuple]):
    """
    Returns a list of list of runs that have the same value at the given attributes
    args:
        param_df: a dataframe with param_df format (see check_param_df_format)
        attributes: a list of tuples that are in the param_df
    returns: 
        resuls: a list with each element being a list of runs that have the same value for the given attributes
    """
    # First check that all attributes are present in the param_df
    for attr in attributes:
        assert attr in param_df.index, (f"Attribute {attr} not present in the param_df")
    
    # Then we use groupby to find the runs that have the same value for the attributes
    # We use a set to avoid duplicates

    param_df_T = param_df.T # Transposed needed for groupby
    result = list()
    for values, df in param_df_T.groupby(by=attributes,axis=0):
        result.append(df.index)
    return result

def get_first_entry_for_each_run(param_df, runs):
    """
    Given a param_df and runs returns a pandas dataframe with all the first entry with each run
    """
    first_runs = [x[0] for x in runs]
    return param_df.loc[:,first_runs]




def return_mean_and_std_of_runs(perf_df, runs):
    """
    Return a dataframe with the mean and std of the runs
    args:
        perf_df: a dataframe with the performance of the runs
        runs: a list of runs that are in the performance dataframe
    returns: 
        res: a perf_df dataframe-like with the mean and std of the runs (the index are the first entry of the runs)
    """
    res = pd.DataFrame()
    index = [x[0] for x in runs]
    for run in runs:
        mean_df = perf_df.loc[run].mean()
        mean_df.index = [x + "_mean" for x in mean_df.index]

        std_df = perf_df.loc[run].std()
        std_df.index = [x + "_std" for x in std_df.index]
        res[run[0]] = pd.concat([mean_df, std_df])
    
    perf_df_res = res.T # Be compliant with perf_df format
    perf_df_res.index = pd.MultiIndex.from_tuples(index)
    return perf_df_res



def drop_not_changing_row(df):
    return df.loc[~df.apply(is_unique,axis=1)]

def return_exps_date(df: pd.DataFrame):
    """Given a dataframe with columns format: "Datetime"/"Run" returns a list of all datetimes"""
    return list(OrderedDict.fromkeys([x[0] for x in df.columns])) 

def return_first_col_per_run(df):
    exps = return_exps_date(df)
    return [list(df.columns.droplevel(-1)).index(x) for x in exps]


def normalize_confusion_matrix(cm, mode="recall"):
    if mode == "recall":
        cm = np.round(cm.astype("float") / cm.sum(axis=1)[:, np.newaxis], 2)
    else:
        cm = np.round(cm.astype("float") / cm.sum(axis=0)[np.newaxis, :], 2)
    return cm


def edit_entry(df, previous_entry, new_entry):
    """
    This returns a dataframe identical to the input one, but with the entry specified in previous_entry replaced by new_entry
    args:
        df: dataframe
        previous_entry: str/tuple/int
        new_entry: str/tuple/int

    Example: 
        return_df = edit_entry(df, ("other", 2), ("hyper", 2))
        with df:
                          metric_1  metric_2  metric_3  ... 
            other 0       0.702448       3
                  2       0.681733       9

        with return_df:
                          metric_1  metric_2  metric_3  ... 
            hyper 0       0.702448       3
            other 2       0.681733       9    
    """

    df = df.copy()
    df.loc[new_entry,:] = df.loc[previous_entry]
    
    # remove the previous entry
    df = df.drop(previous_entry)

    return df

def check_param_df_format():
    raise NotImplementedError

def create_perf_df(param_df, performance_metrics):
    """
    Utility function to create a performance dataframe (aka perf_df) conventiently.
    args:
        param_df: a dataframe with param_df format (see check_param_df_format)
        performance_metrics: a dictionary of list of performance metrics. The list order must be the same as the columns in the param_df
    returns:
        perf_df: a dataframe with the following format:
                                        metric_1  metric_2  metric_3  ... 
            2021-01-26 17-07-39 0       0.702448       3
                                2       0.681733       9

    """
    perf_df = pd.DataFrame(columns=performance_metrics.keys(), index=param_df.columns)
    for k, v in performance_metrics.items():
        perf_df[k] = v
        
    return perf_df

