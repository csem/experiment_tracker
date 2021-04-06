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
import pickle

class SklearnGemLoader(base_loader.BaseLoader):
    def return_pandas(self,path:Path)  -> pd.DataFrame:
        with open(os.path.join(path,"results"), 'rb') as handle: 
            results = pickle.load(handle)
        res = defaultdict(list)
        res[("metric","test_acc_mean")].append(np.mean([results.cv_res[i].test_accuracy for i in range(len(results.cv_res))]))
        res[("metric","train_acc_mean")].append(np.mean([results.cv_res[i].train_accuracy for i in range(len(results.cv_res))]))
        res[("metric","test_ce_mean")].append(np.mean([results.cv_res[i].test_cross_entropy for i in range(len(results.cv_res))]))
        res[("metric","train_ce_mean")].append(np.mean([results.cv_res[i].train_cross_entropy for i in range(len(results.cv_res))]))
        res[("other","time")].append(float('inf'))
        df_metrics = pd.DataFrame.from_dict(res, orient="index")
        df_metrics.index = pd.MultiIndex.from_tuples(df_metrics.index, names=("Type", "Detail"))
        df_res = self.create_metadata_df(path)
        df_res = df_res[np.repeat(df_res.columns.values, len(df_metrics.columns))]
        df_res.columns = df_metrics.columns
        df = pd.concat([df_metrics, df_res])
        exp_name = df.loc[("other","exp_name")].iloc[0]
        run = int(path.stem)
        exp_time = datetime.strptime(path.parent.parent.stem + " " + path.parent.stem, "%Y-%m-%d %H-%M-%S")
        df.columns = pd.MultiIndex.from_tuples(((exp_name,exp_time,run),), names=("Name", "Time","Run"))
        return df

