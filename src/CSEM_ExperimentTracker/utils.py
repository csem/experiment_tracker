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
    return pd.concat([df,fin])
   
    
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

def drop_not_changing_row(df):
    return df.loc[~df.apply(is_unique,axis=1)]


def create_parallel_coordiante_dict(df, hyp, metric_labels=["val_loss", "val_accuracy"]):
    date_to_idx = {val:idx for idx, val in enumerate(sorted(set(df.columns.get_level_values(1))))}
    exps = list(OrderedDict.fromkeys([x[:3] for x in df.columns])) 
    imp_cols = [list(df.columns.droplevel(-1)).index(x) for x in exps]
    metrics = set(df.columns.get_level_values(3))
    dimensions_date = list([
            dict(ticktext = [str(x)[5:16] for x in set(df.columns.get_level_values(1))],
                 tickvals = list(date_to_idx.values()),
                 label = 'Date', values =[date_to_idx[x[1]] for x in exps]),
            dict(range = [0,max([x[-1] for x in exps])],
                 label = 'Run', values = [x[-1] for x in exps])])
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
        # else:
        #     values = [str(x) for x in hyp.loc[row].values]
        #     unique_values = sorted(set(values))
        #     val_to_idx = {val:idx for idx, val in enumerate(unique_values)}
        #     entry = dict(ticktext = [str(x)for x in unique_values],
        #          tickvals = list(val_to_idx.values()),
        #          label = str(row), values =[val_to_idx[x] for x in values])

    dimensions = dimensions_date + dimension_hyp + dimension_metrics
    return dimensions