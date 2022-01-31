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
