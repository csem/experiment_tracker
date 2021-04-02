import click
import os
import pandas as pd
from flatten_dict import flatten
from typing import Callable
from pathlib import Path
from datetime import datetime
from . import utils
import yaml


class BaseLoader():
    def __init__(self):
        pass

    def load_folder(self, folder: Path):
        dfs = []
        for dates, h_m_s in utils.traverse_folders(folder):
            exp_time = datetime.strptime(dates + " " + h_m_s, "%Y-%m-%d %H-%M-%S")
            curr_df = self.load_experiment(folder, exp_time)
            dfs.append(curr_df)
        df = pd.concat(dfs, axis=1)
        df = df.drop_duplicates()
        return df

    def load_experiment(self, folder: Path, time: datetime):
        dfs = []
        date = time.strftime("%Y-%m-%d")
        h_m_s = time.strftime("%H-%M-%S")
        path = Path(os.path.join(folder, date, h_m_s))
        runs = os.listdir(path)
        if not runs:
            print(f"WARNING: No runs for {time}")
        for run in runs:
            curr_path = Path(os.path.join(path,run))
            dfs.append(self.return_pandas(curr_path))
        return pd.concat(dfs, axis=1)

    def return_pandas(self,path) -> pd.DataFrame:
        NotImplementedError


def create_metadata_df(path: Path):
    with open(os.path.join(path.parent, ".hydra/config.yaml"), "r") as metadata:
        metadata = yaml.safe_load(metadata)
    hyp_dict = flatten(metadata.get("hyperparameters", {}), reducer='path')
    df_hyp = pd.DataFrame.from_dict(hyp_dict, orient="index")

    if "hyperparameters" in metadata:
        exp_dict = flatten(metadata.get("hyperparameters", {}), reducer='path')
        df_hyp.index = pd.MultiIndex.from_tuples(
            [("hyp", x) for x in exp_dict]
        )
    
    dateset_dict = flatten(metadata.get("dataset", {}), reducer='path')
    df_dataset = pd.DataFrame.from_dict(dateset_dict, orient="index")
    if "dataset" in metadata:
        dateset_dict = flatten(metadata.get("dataset", {}), reducer='path')
        df_dataset.index = pd.MultiIndex.from_tuples(
            [("dataset", x) for x in dateset_dict]
        )

    metadata.pop("hyperparameters", None)
    other = flatten(metadata, reducer='path')
    df_other = pd.DataFrame.from_dict(other, orient="index")
    df_other.index = pd.MultiIndex.from_tuples([("other", x) for x in other])
    return pd.concat([df_hyp, df_dataset, df_other])


@click.command()
@click.argument("folder")
def save_df(folder):
    df = load_lightning(folder)
    pd.to_pickle(df, "{}.df".format(folder))


if __name__ == "__main__":
    load_results("multirun")
