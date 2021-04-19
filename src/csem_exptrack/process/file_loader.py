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

class FileLoader(base_loader.BaseLoader):
    """This class allows to collect any file with the name speficified during the class instantiation"""
    """It returns the path in the pandas dataframe"""
    def __init__(self,query_string):
        self.query_string = query_string

    def return_pandas(self,path:Path) -> pd.DataFrame:
        #files = os.listdir(path)
        npy_file_paths = glob.glob(os.path.join(path,self.query_string))
        if not npy_file_paths:
            print(f"WARNING: No files of type {self.query_string} in {path} found")
            return pd.DataFrame()
        else:

            index = pd.MultiIndex.from_tuples([("path", i) for i in range(len(npy_file_paths))])
            df = pd.DataFrame({"path":npy_file_paths},index=index)
            df_res = self.create_metadata_df(path)
            df_res = df_res[np.repeat(df_res.columns.values, len(df.columns))]
            df.columns = df_res.columns
            df = pd.concat([df_res,df])
        return df

