import git
import json
from hydra.core.hydra_config import HydraConfig
from pathlib import Path
import hydra 
from omegaconf import errors 

def save_hash(cfg):
    if cfg.automatic_commit.activated:
        # Check if there is any change in the working directory. If so, raise an error
        repo = git.Repo(cfg.automatic_commit.working_dir)
        
        try: 
            hydra_num = HydraConfig.get().job.num
        except errors.MissingMandatoryValue:
            hydra_num = 0

        if repo.is_dirty() and hydra_num == 0:
            raise ValueError("\n\n Working directory is dirty. Please commit your changes before running the job. \n If you want to run the job anyway, set automatic_commit.activated to False in the config file. \n\n")
        # Get the current commit hash
        commit_hash = repo.head.object.hexsha

        # Create a file with the commit hash
        save_dict = {}
        save_dict["commit_hash"] = commit_hash
        with open(f"commit_{commit_hash}.json", "w") as f:
            json.dump(save_dict, f, indent=4)


def log_book():
    import logging 
    import os 
    
    # Create the asset path and the logbook if it does not exist
    log_book_path = Path(hydra.utils.to_absolute_path("assets/logbook.json"))

    log_book_path.parent.mkdir(parents=True, exist_ok=True)
    Path(log_book_path).touch()

    # Save to the logbook that the file has been run 
    
    # Create a logger
    logger = logging.getLogger(__file__)
    # Set the log level
    logger.setLevel(logging.INFO)
    # Create a file handler
    file_handler = logging.FileHandler(log_book_path)
    # Set the log format
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    # Add the file handler to the logger
    logger.addHandler(file_handler)
    # Add message to the logbook
    return logger