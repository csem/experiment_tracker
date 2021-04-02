import click

def return_pandas(exp_time, run, logger):
    with open(logger, "r") as fout:
        json_logger = json.load(fout)
    df_epochs = create_epoch_df(json_logger, exp_time, run)
    if not len(df_epochs):
        return df_epochs
    else:
        df_res = create_metadata_df(logger)
        df_res = df_res[np.repeat(df_res.columns.values, len(df_epochs.columns))]
        df_res.columns = df_epochs.columns
        df = pd.concat([df_epochs, df_res])
        metric_min = np.expand_dims(df.loc["epoch"].min().values,0)
        metric_max = np.expand_dims(df.loc["epoch"].max().values,0)
        metric = np.concatenate([metric_min,metric_max],axis=0)
        df_metric = pd.DataFrame(metric, columns=df.columns)
        df_metric.index =  pd.MultiIndex.from_tuples([("metric", "min"),("metric", "max")])
        df = pd.concat([df,df_metric])
    return df


def create_metadata_df(logger):
    with open(os.path.join(logger.parent, ".hydra/config.yaml"), "r") as metadata:
        metadata = yaml.safe_load(metadata)
    exp_dict = flatten(metadata.get("hyperparameters", {}), reducer='path')
    df_hyp = pd.DataFrame.from_dict(exp_dict, orient="index")

    if "hyperparameters" in metadata:
        exp_dict = flatten(metadata.get("hyperparameters", {}), reducer='path')
        df_hyp.index = pd.MultiIndex.from_tuples(
            [("hyp", x) for x in exp_dict]
        )

    metadata.pop("hyperparameters", None)
    other = flatten(metadata, reducer='path')
    df_other = pd.DataFrame.from_dict(other, orient="index")
    df_other.index = pd.MultiIndex.from_tuples([("other", x) for x in other])
    return pd.concat([df_hyp, df_other])


@click.command()
@click.argument("folder")
def save_df(folder):
    df = load_lightning(folder)
    pd.to_pickle(df, "{}.df".format(folder))


if __name__ == "__main__":
    load_results("multirun")
