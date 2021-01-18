import pickle
import os
import pathlib
from datetime import datetime
import yaml
import pandas as pd
import json


def create_exp_df(json_dict):
    dfs = []
    metrics = json_dict["Metrics"]
    for k in metrics.keys():
        dfs.append(
            pd.DataFrame.from_dict(
                {epoch: data for data, epoch in metrics[k]}, orient="index", columns=[k]
            )
        )
    df = pd.concat(dfs, axis=1)
    return df


def load_results(folder):
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
    # create_row(name, date, metrics)

    # pd.DataFrame()
    #     breakpoint()
    # # for i in os.listdir(os.path.join(folder, dates, t)):
    # breakpoint()
    # exp_name = [x for x in os.listdir(path)]
    # # if not i in ["optimization_results.yaml"]:
    # base_path = os.path.join(folder, dates, t, i)
    # runs.append(base_path)
    # expname = [x for x in os.listdir]
    # if "results" in os.listdir(base_path):
    #     with open(os.path.join(base_path, "results"), "rb") as handle:
    #         results.append(pickle.load(handle))
    #     with open(
    #         os.path.join(base_path, ".hydra/config.yaml"), "rb"
    #     ) as handle:
    #         configs.append(yaml.load(handle))

    breakpoint()

    folder = "output"
    for dates in os.listdir(folder):
        # y_m_d = date.fromisoformat(dates)
        for t in os.listdir(os.path.join(folder, dates)):
            # h_s_m = time.fromisoformat(t)
            exp_time = datetime.strptime(dates + " " + t, "%Y-%m-%d %H-%M-%S")
            base_path = os.path.join(folder, dates, t)
            breakpoint()
    # if file in files:


if __name__ == "__main__":
    load_results("outputs")
