import pickle
import os
from pathlib import Path
from datetime import datetime
import yaml
import pandas as pd
import shutil
import json
import click


def create_exp_df(json_dict, metrics_key="Metrics"):
    dfs = []
    experience = json_dict[metrics_key]
    metric_col = []

    # Add Metrics
    for stage in experience:
        # metric_col.extend(stage.keys())
        cols = set(stage.keys()) - set(["epoch"])
        dfs.append(
            pd.DataFrame(
                {col: stage[col] for col in cols},
                index=[stage["epoch"]],
            )
        )
    df = pd.concat(dfs, axis=0)
    for i in set(df.index):
        df.loc[i].fillna(axis=0, method="backfill", inplace=True)
        df.loc[i].fillna(axis=0, method="ffill", inplace=True)

    # Add Hyperparameters
    if "hyper" in json_dict:
        try:
            for key, val in json_dict.get("hyper").items():
                df[key] = val
        except:
            print("Issue reading these Hyps {}".join(json_dict.get("hyper")))
    return df


def load_results(folder):
    if folder == "outputs":
        runs = []
        results = []
        configs = []
        folder = folder
        dfs = []
        tuples = []
        for dates in os.listdir(folder):
            # y_m_d = date.fromisoformat(dates)
            for t in os.listdir(os.path.join(folder, dates)):
                # h_s_m = time.fromisoformat(t)
                exp_time = datetime.strptime(dates + " " + t, "%Y-%m-%d %H-%M-%S")
                path = os.path.join(folder, dates, t)
                name_list = [x for x in os.listdir(path) if x[-4:] == "json"]
                if name_list:
                    name = name_list[0]
                    with open(os.path.join(path, name), "r") as fout:
                        json_dict = json.load(fout)
                    if not json_dict or not json_dict["Metrics"]:
                        continue
                    dfs.append(create_exp_df(json_dict))
                    tuples.append((name[:-5], exp_time))
        index = pd.MultiIndex.from_tuples(tuples, names=("Name", "Exp_time"))
        df = pd.concat(dfs, axis=0, keys=index)
        return df
    elif folder == "multirun":
        runs = []
        results = []
        configs = []
        folder = folder
        dfs = []
        tuples = []
        for dates in os.listdir(folder):
            # y_m_d = date.fromisoformat(dates)
            for t in os.listdir(os.path.join(folder, dates)):
                for i in os.listdir(os.path.join(folder, dates, t)):
                    if i.isdigit():
                        # h_s_m = time.fromisoformat(t)
                        exp_time = datetime.strptime(
                            dates + " " + t, "%Y-%m-%d %H-%M-%S"
                        )
                        path = os.path.join(folder, dates, t, i)
                        name_list = [x for x in os.listdir(path) if x[-4:] == "json"]
                        if name_list:
                            name = name_list[0]
                            with open(os.path.join(path, name), "r") as fout:
                                json_dict = json.load(fout)
                            metrics = [
                                x
                                for x in ["metrics", "Metrics"]
                                if x in json_dict.keys()
                            ]
                            if (
                                not json_dict
                                or not metrics
                                or not json_dict[metrics[0]]
                            ):
                                continue
                            dfs.append(create_exp_df(json_dict, metrics_key=metrics[0]))
                            tuples.append((name[:-5], exp_time, i))
        index = pd.MultiIndex.from_tuples(tuples, names=("Name", "Exp_time", "Run"))
        df = pd.concat(dfs, axis=0, keys=index)
        return df


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


# def load_results_multirun(folder):
#     runs = []
#     results = []
#     configs = []
#     folder = folder
#     dfs = []
#     tuples = []
#     for dates in os.listdir(folder):
#         for t in os.listdir(os.path.join(folder, dates)):
#             for i in os.listdir(os.path.join(folder, dates, t)):
#                 path = os.path.join(folder, dates, t, i)
#                 exp_time = datetime.strptime(dates + " " + t, "%Y-%m-%d %H-%M-%S")
#                 path = os.path.join(folder, dates, t)
#                 name_list = [x for x in os.listdir(path) if x[-4:] == "json"]
#                 if name_list:
#                     name = name_list[0]
#                     with open(os.path.join(path, name), "r") as fout:
#                         json_dict = json.load(fout)
#                     if not json_dict or not json_dict["Metrics"]:
#                         continue
#                     dfs.append(create_exp_df(json_dict))
#                     tuples.append((name[:-5], exp_time))
#     index = pd.MultiIndex.from_tuples(tuples, names=("Name", "Exp_time"))
#     df = pd.concat(dfs, axis=0, keys=index)
#     return df


if __name__ == "__main__":
    load_results("multirun")
