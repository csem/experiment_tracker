import pandas as pd
import pdb
from collections import OrderedDict

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
    values = list(df.index)
    df_tmp = df.T
    dicts = {}
    available_lines = set()
    for k in keys_metrics:
        groups = []
        bool_cond = k == df.columns.get_level_values(-1)
        runs_col = [idx for idx, x in enumerate(bool_cond) if x]
        for keys, values in df_tmp.groupby(by=list(df_tmp.columns)):
            runs = set(values.index.droplevel([0,3]))
            cols = [idx for idx, x in enumerate(df.columns.droplevel([0,3])) if (x in runs) and (idx in runs_col)]
            groups.append(cols) 
            available_lines.add(str(dict(values.iloc[0])))
        dicts[k] = (groups)
    return dicts, available_lines

def drop_not_changing_row(df):
    return df.loc[~df.apply(is_unique,axis=1)]

def return_runs_columns(df):
    return list(OrderedDict.fromkeys([x[:3] for x in df.columns])) 

def return_first_col_per_run(df):
    exps = return_runs_columns(df)
    return [list(df.columns.droplevel(-1)).index(x) for x in exps]

def create_parallel_coordiante_dict(df, hyp, metric_labels=["val_loss", "val_accuracy"]):
    date_to_idx = {val:idx for idx, val in enumerate(sorted(set(df.columns.get_level_values(1))))}
    exps = return_runs_columns(df)
    imp_cols = return_first_col_per_run(df)
    metrics = set(df.columns.get_level_values(3))
    dimensions_date = list([
            dict(ticktext = [str(x)[5:16] for x in set(df.columns.get_level_values(1))],
                 tickvals = list(date_to_idx.values()),
                 label = 'Date', values =[date_to_idx[x[1]] for x in exps]),
            dict(range = [0,max([x[-1] for x in exps])],
                 label = 'Run', values = [x[-1] for x in exps])])

    values = [str(x) for x in df.loc["other","random_seed"].values]
    unique_values = sorted(set(values))
    val_to_idx = {val:idx for idx, val in enumerate(unique_values)}
    random_seed = [dict(ticktext = [str(x)for x in unique_values],
            tickvals = list(val_to_idx.values()),
            label = "Random Seed", values =[val_to_idx[x] for x in values])]

            
    dimension_hyp = []
    for row in hyp.index:
        if all([type(x) == int or type(x) == float for x in hyp.loc[row].values]):
            entry = dict(range = [min(hyp.loc[row].values),max(hyp.loc[row].values)],
                 label = str(row), values = hyp.loc[row].iloc[imp_cols].values)
        else:
            values = [str(x) for x in hyp.loc[row].iloc[imp_cols].values]
            unique_values = sorted(set(values))
            val_to_idx = {val:idx for idx, val in enumerate(unique_values)}
            entry = dict(ticktext = [str(x)for x in unique_values],
                 tickvals = list(val_to_idx.values()),
                 label = str(row), values =[val_to_idx[x] for x in values])
        dimension_hyp.append(entry)

    df_metric = df.loc["metric"]
    dimension_metrics = []
    for row in set(df.columns.get_level_values(3)):
        if not row in metric_labels:
            continue
        if "loss" in row:
            imp = df.columns.get_level_values(3) == row
            values = df_metric.loc["roll_min",imp].fillna(1).values
            entry = dict(range = [max(values),min(values)],
                    label = str(row), values = values)
        elif "accuracy" in row:
            imp = df.columns.get_level_values(3) == row
            values = df_metric.loc["roll_max",imp].fillna(0).values
            entry = dict(range = [min(values),max(values)],
                    label = str(row), values = values)
        dimension_metrics.append(entry)

    dimensions = dimensions_date + random_seed + dimension_hyp + dimension_metrics
    return dimensions