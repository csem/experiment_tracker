import pytest
from CSEM_ExperimentTracker import load_files


@pytest.mark.parametrize("folder", [("multirun"), ("output")])
@pytest.mark.skip
def test_check_detph_folder(folder):
    """Return where is the log file"""
    raise NotImplementedError
    # load_files.check_detph_folder(folder)

@pytest.mark.parametrize("folder", [("runs/RandomForest_ED_Client_sample")])
def test_load_sklear(folder):
    load_files.load_sklear(folder)


@pytest.mark.parametrize("folder", [("runs/UV_DATA_BERTINO")])
def test_load_lightning(folder):
    load_files.load_lightning(folder)