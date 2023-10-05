import git
import json
from hydra.core.hydra_config import HydraConfig


def save_hash(cfg):
    if cfg.automatic_commit.activated:
        # Check if there is any change in the working directory. If so, raise an error
        repo = git.Repo(cfg.automatic_commit.working_dir)
        if repo.is_dirty() and HydraConfig.get().job.num == 0:
            raise ValueError("Working directory is dirty. Please commit your changes before running the job.")
        # Get the current commit hash
        commit_hash = repo.head.object.hexsha

        # Create a file with the commit hash
        save_dict = {}
        save_dict["commit_hash"] = commit_hash
        with open("commit_info.yaml", "w") as f:
            json.dump(save_dict, f, indent=4)

