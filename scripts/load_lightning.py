from CSEM_ExperimentTracker.Process import lightning_loader
import click
import pandas as pd

@click.command()
@click.argument("folder")
def save_df(folder):
    loader = lightning_loader.LightningLoader()
    df = loader.load_folder(folder)
    pd.to_pickle(df, "{}.df".format(folder))


if __name__=="__main__":
    save_df()