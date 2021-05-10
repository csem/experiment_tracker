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
            str_time = dates + " " + h_m_s
            exp_time = datetime.strptime(str_time, "%Y-%m-%d %H-%M-%S")
            curr_df = self.load_experiment(folder, exp_time)
            t = pd.MultiIndex.from_tuples([(str_time,x) for x in curr_df.columns])
            curr_df.columns = t
            dfs.append(curr_df)
        
        df = pd.concat(dfs, axis=1)
        try:
            df = df.drop_duplicates()
        except TypeError:
            df.loc[df.astype(str).drop_duplicates().index] # If there are lists in the df due to presence of lists in the hydra config

        return df.sort_index(axis=1)

    def load_experiment(self, folder: Path, time: datetime):
        dfs = []
        date = time.strftime("%Y-%m-%d")
        h_m_s = time.strftime("%H-%M-%S")
        path = Path(os.path.join(folder, date, h_m_s))
        runs = os.listdir(path)
        runs = [x for x in runs if x.isdigit()]
        if not runs:
            print(f"WARNING: No runs for {time}")
        for run in runs:
            curr_path = Path(os.path.join(path,run))
            df = self.return_pandas(curr_path)
            if len(df)>0:
                df.columns = [int(curr_path.stem)]
            dfs.append(df)
        return pd.concat(dfs, axis=1)

    def return_pandas(self,path) -> pd.DataFrame:
        NotImplementedError

    @staticmethod
    def create_metadata_df(path: Path):
        with open(os.path.join(path, ".hydra/config.yaml"), "r") as metadata:
            metadata = yaml.safe_load(metadata)
        
        dfs = []
        for category in ["hyperparameters","dataset"]:

            curr_dict = flatten(metadata.get(category, {}), reducer='path')
            df_curr = pd.DataFrame.from_dict(curr_dict, orient="index")

            if category in metadata:
                exp_dict = flatten(metadata.get(category, {}), reducer='path')
                df_curr.index = pd.MultiIndex.from_tuples(
                    [(category, x) for x in exp_dict]
                )
            
            dfs.append(df_curr)
            metadata.pop(category, None)
        
        other = flatten(metadata, reducer='path')
        df_other = pd.DataFrame.from_dict(other, orient="index")
        df_other.index = pd.MultiIndex.from_tuples([("other", x) for x in other])
        dfs.append(df_other)
        return pd.concat(dfs)



class BaseLoader_fdi():
    def __init__(self, hyperparameters_list):
        self.hyperparameters_list = hyperparameters_list
        pass

    def load_folder(self, folder: Path):
        dfs = []
        for dates, h_m_s in utils.traverse_folders(folder):
            str_time = dates + " " + h_m_s
            exp_time = datetime.strptime(str_time, "%Y-%m-%d %H-%M-%S")
            curr_df = self.load_experiment(folder, exp_time)
            t = pd.MultiIndex.from_tuples([(str_time,x) for x in curr_df.columns])
            curr_df.columns = t
            dfs.append(curr_df)
        
        df = pd.concat(dfs, axis=1)
        try:
            df = df.drop_duplicates()
        except TypeError:
            df.loc[df.astype(str).drop_duplicates().index] # If there are lists in the df due to presence of lists in the hydra config

        return df

    def load_experiment(self, folder: Path, time: datetime):
        dfs = []
        date = time.strftime("%Y-%m-%d")
        h_m_s = time.strftime("%H-%M-%S")
        path = Path(os.path.join(folder, date, h_m_s))
        runs = os.listdir(path)
        runs = [x for x in runs if x.isdigit()]
        if not runs:
            print(f"WARNING: No runs for {time}")
        for run in runs:
            curr_path = Path(os.path.join(path,run))
            df = self.return_pandas(curr_path)
            if len(df)>0:
                df.columns = [int(curr_path.stem)]
            dfs.append(df)
        return pd.concat(dfs, axis=1)


    def return_pandas(self,path) -> pd.DataFrame:
        NotImplementedError


    def create_metadata_df(self, path: Path):
        with open(os.path.join(path, ".hydra/config.yaml"), "r") as metadata:
            metadata = yaml.safe_load(metadata)

        dfs = []
        
        exp_dict_other = flatten(metadata, reducer='path')

        df_other = pd.DataFrame.from_dict(exp_dict_other, orient="index")
        df_other.index = pd.MultiIndex.from_tuples([("other", x) for x in exp_dict_other])
        dfs.append(df_other)

        exp_dict_hyper = {key: exp_dict_other[key] for key in self.hyperparameters_list}
        df_hyper = pd.DataFrame.from_dict(exp_dict_hyper, orient="index")
        df_hyper.index = pd.MultiIndex.from_tuples([("hyperparameters", x) for x in exp_dict_hyper])
        dfs.append(df_hyper)

        return pd.concat(dfs)



@click.command()
@click.argument("folder")
def save_df(folder):
    df = load_lightning(folder)
    pd.to_pickle(df, "{}.df".format(folder))


if __name__ == "__main__":
    load_results("multirun")
