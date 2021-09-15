from . import gui
from . import process
from . import utils 
from . import loggers
from .gui.gui_utils import header
from .process.file_loader import FileLoader


def load_project(base_path, query_string):
    """
    Utility function for using process.load_experiment easily.
    args:
        base_path: Path to the base directory in Hydra Hieracrchy
        query_string: String to be used in the file_loader for deciding which path to load
    returns:
        df: A pandas dataframe of the data from the experiment (aka param_df)
    """
    file_loader = FileLoader(query_string)
    return file_loader.load_project(base_path) 

def load_run(run_path, query_string):
    """
    Utility function for using process.file_loader easily.
    args:
        base_path: Path to the base directory in Hydra Hieracrchy
        query_string: String to be used in the file_loader for deciding which path to load
    """
    file_loader = FileLoader(query_string)
    return file_loader.return_pandas(run_path)


