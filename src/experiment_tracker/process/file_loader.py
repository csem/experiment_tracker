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
from ..base_logger import logger


class FileLoader(base_loader.BaseLoader):
    """
    This class allows to collect hydra parameters and file paths speficified during the class instantiation in a pandas dataframe
    
    Usage:
    loader = FileLoader(query_string="*.pkl") # Will look for all files path with suffix .pkl in each hydra run folder
    df = loader.load_folder("my_experiment/2021-08-17/12-32-14") # Will return the df with all the information"
    """
    def __init__(self,query_string, logic="multirun", min_required_files=1):
        if type(query_string) == str:
            self.query_string = [query_string]
        elif type(query_string) == list:
            self.query_string = query_string
        else:
            raise TypeError
        
        assert logic in ["multirun","singlerun"], "logic keyword must be either multirun or singlerun"
        assert type(min_required_files) == int, "required_files keyword must be an integer"
        self.logic = logic
        self.min_required_files = min_required_files


    def return_pandas(self,path:Path) -> pd.DataFrame:
        """
        path: Path to the folder containing the files to be loaded, with format my_experiment/2021-08-17/12-32-14
        """

        npy_file_paths = []
        for query_string in self.query_string:
            npy_file_paths.extend(glob.glob(os.path.join(path,query_string)))

        if not npy_file_paths:
            logger.warn(f"No files of type {self.query_string} in {path} found")
            return pd.DataFrame()
        else:
            if len(npy_file_paths) < self.min_required_files:
                logger.warn(f"Not enough files of type {self.query_string} in {path} found")
                return pd.DataFrame()
            else:
                index = [f"collected_path_{i}" for i in range(len(npy_file_paths))]
                df = pd.DataFrame({"path":npy_file_paths},index=index)
                df_res = self.create_metadata_df(path)
                df_res = df_res[np.repeat(df_res.columns.values, len(df.columns))]
                df.columns = df_res.columns
                # Combine index in just one level
                
                df = pd.concat([df_res,df]).T
        return df

