import click
import os
import pandas as pd
from flatten_dict import flatten
from typing import Callable
from pathlib import Path
from datetime import datetime
from . import utils
import yaml
import warnings
from ..base_logger import logger

class BaseLoader():
    def __init__(self):
        pass

    def load_project(self, base_project_path: Path, filter_date: datetime = None, filter_hms: datetime = None):
        """
        base_project_path: folder containing multiple experiments (e.g. a folder with inside multiples year-month-day/hour-min-sec folders)
        """
        if filter_date == "last" or filter_hms == "last":
            # Iterarate over the folders and get the last one
            dates = os.listdir(base_project_path)
            dates = [x for x in dates if x != ".DS_Store"]
            dates = [datetime.strptime(x, "%Y-%m-%d") for x in dates]
            dates.sort()
            filter_date = dates[-1]
            hms = os.listdir(Path(os.path.join(base_project_path, filter_date.strftime("%Y-%m-%d"))))
            hms = [x for x in hms if x != ".DS_Store"]
            hms = [datetime.strptime(x, "%H-%M-%S") for x in hms]
            hms.sort()
            filter_hms = hms[-1]
            filter_date = filter_date.strftime("%Y-%m-%d")
            filter_hms = filter_hms.strftime("%H-%M-%S")


        dfs = []
        for date, h_m_s in utils.traverse_folders(base_project_path):
            if filter_date is not None and date != filter_date:
                continue
            if filter_hms is not None and h_m_s != filter_hms:
                continue
            str_time = date + " " + h_m_s
            try:
                exp_time = datetime.strptime(str_time, "%Y-%m-%d %H-%M-%S")
            except ValueError:
                logger.warn(f"Could not parse time {str_time}")
                continue
            curr_df = self.load_experiment(base_project_path, exp_time)
            if len(curr_df)==0:
                logger.warn(f"No data for {exp_time}")
                continue
            t = pd.MultiIndex.from_tuples([(str_time,x) for x in curr_df.index])
            curr_df.index = t
            dfs.append(curr_df)
        
        if len(dfs)==0:
            raise ValueError("No experiments data found")
    
        df = pd.concat(dfs, axis=0)
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
        if self.logic == "multirun":
            if not runs:
                logger.warn(f"No runs for {date} {time}")
            for run in runs:
                curr_path = Path(os.path.join(path,run))
                df = self.return_pandas(curr_path)
                if len(df)>0:
                    df.index = [int(curr_path.stem)]
                dfs.append(df)
        elif self.logic == "singlerun":
            df = self.return_pandas(path)
            if len(df)>0:
                df.index = [0]
            dfs.append(df)
        else:
            raise KeyError("logic must be either multirun or singlerun")
        
        if not dfs:
            return pd.DataFrame()
        else: 
            return pd.concat(dfs, axis=0)

    def return_pandas(self,path) -> pd.DataFrame:
        NotImplementedError

    @staticmethod
    def create_metadata_df(path: Path):
        with open(os.path.join(path, Path(".hydra/config.yaml")), "r") as metadata:
            metadata = yaml.safe_load(metadata)
        
        
        other = flatten(metadata, reducer='path')
        df_other = pd.DataFrame.from_dict(other, orient="index")
        df_other.index = [x for x in other]
        #dfs.append(df_other)
        return df_other



@click.command()
@click.argument("folder")
def save_df(folder):
    df = load_lightning(folder)
    pd.to_pickle(df, "{}.df".format(folder))


if __name__ == "__main__":
    load_results("multirun")
