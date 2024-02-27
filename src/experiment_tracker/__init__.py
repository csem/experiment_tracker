from . import gui
from . import process
from .gui.gui_utils import header
from .process.file_loader import FileLoader
from . import hydra_utils

# Utility function for improving user experience
# See README.md for more information about what a project or run is.


def load_project(base_path, query_string, logic="multirun", min_required_files=1, filter_date=None, filter_hms=None): 
    """
    Utility function for using process.load_experiment easily.
    args:
        base_path: Path to the base directory in Hydra Hierarchy
        query_string: String or List to be used in the file_loader for deciding which path to load
    returns:
        df: A pandas dataframe of the data from the experiment (aka param_df)
    """
    file_loader = FileLoader(query_string, logic, min_required_files)
    return file_loader.load_project(base_path, filter_date=filter_date, filter_hms=filter_hms)

def load_run(run_path, query_string):
    """
    Utility function for using process.file_loader easily.
    args:
        base_path: Path to the base directory in Hydra Hierarchy
        query_string: String to be used in the file_loader for deciding which path to load
    """
    file_loader = FileLoader(query_string)
    return file_loader.return_pandas(run_path)


# Utility function for improving user experience
load = load_project