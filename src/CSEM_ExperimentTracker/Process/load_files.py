import pickle
import os
from pathlib import Path
from datetime import datetime
import yaml
import glob
import pandas as pd
import shutil
import json
import click
from collections import defaultdict
import numpy as np
from flatten_dict import flatten


def create_epoch_df(json_dict, exp_time, run):
    df = pd.DataFrame({})
    for metric_key in ["Metrics", "metrics"]:
        experience = json_dict.get(metric_key, None)
        if experience is None or not len(experience) or not type(experience) == dict:
            continue
        else:
            tmp_dict = {}
            for key in experience.keys():
                res = {}
                for update in experience[key]:
                    res[update[1]] = update[0]  # Epoch: Val
                tmp_dict[key] = res
                total_epochs = max(
                    list(
                        set(
                            [
                                epoch + 1
                                for metric in tmp_dict.keys()
                                for epoch in tmp_dict[metric].keys()
                            ]
                        )
                    )
                )
            fin_dict = defaultdict(list)
            for k in experience.keys():
                for i in range(total_epochs):
                    fin_dict[k].append(tmp_dict[k].get(i, float("inf")))
            df = pd.DataFrame(fin_dict)
            df.index = pd.MultiIndex.from_tuples(
                ("epoch", x) for x in range(total_epochs)
            )
            #df.dropna(inplace=True)
            new_columns = pd.MultiIndex.from_tuples(
                [(json_dict["exp_name"], exp_time, run, x) for x in df.columns],
                names=["Name", "Experiment_Time", "Run", "hyp"],
            )
            df.columns = new_columns
    return df




def return_pandas_sklearn(exp_time, run, logger):
    with open(logger, 'rb') as handle: 
        results = pickle.load(handle)
    res = defaultdict(list)
    res[("metric","test_acc_mean")].append(np.mean([results.cv_res[i].test_accuracy for i in range(len(results.cv_res))]))
    res[("metric","train_acc_mean")].append(np.mean([results.cv_res[i].train_accuracy for i in range(len(results.cv_res))]))
    res[("metric","test_ce_mean")].append(np.mean([results.cv_res[i].test_cross_entropy for i in range(len(results.cv_res))]))
    res[("metric","train_ce_mean")].append(np.mean([results.cv_res[i].train_cross_entropy for i in range(len(results.cv_res))]))
    res[("other","time")].append(float('inf'))
    df_metrics = pd.DataFrame.from_dict(res, orient="index")
    df_metrics.index = pd.MultiIndex.from_tuples(df_metrics.index, names=("Type", "Detail"))
    df_res = create_metadata_df(logger)
    df_res = df_res[np.repeat(df_res.columns.values, len(df_metrics.columns))]
    df_res.columns = df_metrics.columns
    df = pd.concat([df_metrics, df_res])
    exp_name = df.loc[("other","exp_name")].iloc[0]
    df.columns = pd.MultiIndex.from_tuples(((exp_name,exp_time,run),), names=("Name", "Time","Run"))
    return df




def load_sklearn(folder):
    dfs = []
    for dates in os.listdir(folder):
        for time in os.listdir(os.path.join(folder, dates)):
            dfs.append(load_sklearn_experiment(folder,dates,time))
    return pd.concat(dfs,axis=1)
    
def load_sklearn_experiment(folder,dates,time):
    dfs = []
    exp_time = datetime.strptime(dates + " " + time, "%Y-%m-%d %H-%M-%S")
    path = Path(os.path.join(folder, dates, time))
    loggers = path.glob("**/results")
    res = {x: [] for x in ("test_acc","train_acc","test_ce","train_ce")}
    for logger in loggers:
        run = logger.parent.name   
        dfs.append(return_pandas_sklearn(exp_time,run, logger))
        
        if logger.parent.name.isdigit():
            run = int(logger.parent.name)
        else:
            run = 0
    if len(dfs) > 0:
        res = pd.concat(dfs,axis=1)
    else:
        res = pd.DataFrame()
    return res

def _delete_empty_multirun(folder):
    for dates in os.listdir(folder):
        for t in os.listdir(os.path.join(folder, dates)):
            exp_path = os.path.join(folder, dates, t)
            cont = os.listdir(os.path.join(folder, dates, t))
            if len(cont) == 1 and cont[0] == "0":
                p = Path(os.path.join(folder, dates, t, cont[0]))
                exp_data = [
                    f for f in p.glob("**/*") if f.name in ("logger.json", "logger")
                ]
                if exp_data:
                    with open(os.path.join(exp_data[0]), "r") as fout:
                        json_dict = json.load(fout)
                    if "metrics" in json_dict and len(json_dict["metrics"]):
                        continue
                shutil.rmtree(exp_path)

    # Delete empty folder
    for folder_path in os.listdir(folder):
        path = os.path.join(folder, folder_path)
        if len(os.listdir(path)) == 0:
            shutil.rmtree(path)


@click.command()
@click.argument("folder")
def delete_empty_folder(folder):
    _delete_empty_multirun(folder)


@click.command()
@click.argument("folder")
def save_df(folder):
    df = load_lightning(folder)
    pd.to_pickle(df, "{}.df".format(folder))


if __name__ == "__main__":
    load_results("multirun")
