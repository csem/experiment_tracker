import py.test
from CSEM_ExperimentTracker import load_files, plots, utils

def test_compute_rolling_window_metrics():
    curr = load_files.load_lightning("runs/UV_DATA_RESNET")
    df = utils.return_exp_based_on_datetime(curr,'2021-02-15', "09:29:13")
    df = utils.compute_rolling_window_metrics(df, roll=1)
    assert df["metric","roll_max"]
    breakpoint()
