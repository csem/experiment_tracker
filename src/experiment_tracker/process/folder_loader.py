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

class FolderLoader(base_loader.BaseLoader):
    """This class allows to collect any file with the name speficified during the class instantiation"""
    """It returns the path in the pandas dataframe"""

    def return_pandas(self,path:Path) -> pd.DataFrame:
        #files = os.listdir(path)
        folder_path = os.path.join(path)

        index = pd.MultiIndex.from_tuples([("folder", "")])
        df = pd.DataFrame({"folder":folder_path},index=index)
        df_res = self.create_metadata_df(path)
        df_res = df_res[np.repeat(df_res.columns.values, len(df.columns))]
        df.columns = df_res.columns
        df = pd.concat([df_res,df])

        return df

