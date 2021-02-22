import py.test
from CSEM_ExperimentTracker import load_files, plots, utils
import pandas as pd

def test_compute_rolling_window_metrics():
    curr = load_files.load_lightning("runs/UV_DATA_RESNET")
    df = utils.return_exp_based_on_datetime(curr,'2021-02-15', "09:29:13")
    df = utils.compute_rolling_window_metrics(df, roll=1)
    assert df["metric","roll_max"]
    breakpoint()

def test_create_parallel_coordiante_dict():
    curr = load_files.load_lightning("runs/UV_DATA_RESNET")
    df = utils.return_exp_based_on_datetime(curr,'2021-02-13', "09:02:15")
    df2 = utils.return_exp_based_on_datetime(curr,'2021-02-15', "09:29:13")
    df = pd.concat([df,df2],axis=1)
    df = utils.compute_rolling_window_metrics(df, roll=1)
    hyp_cols = utils.drop_not_changing_row(df.loc["hyp"]).dropna()
    utils.create_parallel_coordiante_dict(df,hyp_cols)