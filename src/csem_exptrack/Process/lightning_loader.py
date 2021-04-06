import pandas as pd
from . import utils
from datetime import datetime
from . import base_loader
import click
from pathlib import Path
import os
import glob
import json
from datetime import datetime
from collections import defaultdict
import numpy as np

class LightningLoader(base_loader.BaseLoader):
    def return_pandas(self,path:Path) -> pd.DataFrame:
        #files = os.listdir(path)
        pytorch_json = glob.glob(os.path.join(path,"*.json"))
        if not pytorch_json:
            print(f"WARNING: No logger for {path}")
            return pd.DataFrame()
        logger = Path(pytorch_json[0])
        with open(logger, "r") as fout:
            json_logger = json.load(fout)
        run = int(path.stem)
        exp_time = datetime.strptime(path.parent.parent.stem + " " + path.parent.stem, "%Y-%m-%d %H-%M-%S")
        df_epochs = create_epoch_df(json_logger, exp_time, run)
        if not len(df_epochs):
            print(f"WARNING: No epochs in {path}")
            return df_epochs
        else:
            df_res = base_loader.create_metadata_df(logger)
            df_res = df_res[np.repeat(df_res.columns.values, len(df_epochs.columns))]
            df_res.columns = df_epochs.columns
            df = pd.concat([df_epochs, df_res])
            metric_min = np.expand_dims(df.loc["epoch"].min().values,0)
            metric_max = np.expand_dims(df.loc["epoch"].max().values,0)
            metric = np.concatenate([metric_min,metric_max],axis=0)
            df_metric = pd.DataFrame(metric, columns=df.columns)
            df_metric.index =  pd.MultiIndex.from_tuples([("metric", "min"),("metric", "max")])
            df = pd.concat([df,df_metric])
        return df


def create_epoch_df(json_dict, exp_time: datetime, run: int):
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





