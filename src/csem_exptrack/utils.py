import pandas as pd
import pdb
from collections import OrderedDict
import numpy as np


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