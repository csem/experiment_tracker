import pandas as pd
from . import utils
from datetime import datetime
from . import base_loader
import click


def load_lightning(folder):
    dfs = []
    for dates, h_m_s in utils.traverse_folders(folder):
        exp_time = datetime.strptime(dates + " " + h_m_s, "%Y-%m-%d %H-%M-%S")
        path = Path(os.path.join(folder, dates, h_m_s))
        loggers = list(path.glob("**/*.json"))
        for logger in loggers:
            if logger.parent.name.isdigit():
                run = int(logger.parent.name)
            else:
                run = 0
            dfs.append(base_loader.return_pandas(exp_time, run, logger))
    df = pd.concat(dfs, axis=1)
    df = df.drop_duplicates()
    return df


@click.command()
@click.argument("folder")
def save_df(folder):
    df = load_lightning(folder)
    pd.to_pickle(df, "{}.df".format(folder))


if __name__=="__main__":
    save_df()