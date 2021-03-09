import plotly
import plotly.graph_objects as go
import plotly.express as px
from . import utils
import plotly.figure_factory as ff

def plots_epochs(
    df,
    keys,
    mode="lines+markers",
):
    fig = go.Figure()
    if type(keys) != list:
        keys = [keys]
    for j in keys:
        for idx, i in enumerate(set(df.index.droplevel(-1))):
            fig.add_trace(
                go.Scatter(
                    x=list(df.loc[i, j].index),
                    y=list(df.loc[i, j]),
                    mode=mode,
                    name=str(j),
                    hovertemplate="Base Model {} \n".format(
                        None != df.loc[i, ("hyper", "path_base_model")].iloc[0]
                    )
                    + "Units {} \n".format(
                        df.loc[i, ("hyper", "number_of_units")].iloc[0]
                    )
                    + "Dropout {} \n".format(df.loc[i, ("hyper", "dropout")].iloc[0])
                    + "freeze {} \n".format(df.loc[i, ("hyper", "freeze")].iloc[0])
                    + "Date {} \n".format(i),
                    marker_color=px.colors.qualitative.Light24[idx],
                )
            )

    return fig



def interactive_confusion_matrix(conf, order, colorscale="electric"):
    x = order
    y = order
    z_text_train = [[str(y) for y in x] for x in conf.T]
    z_text_test = [[str(y) for y in x] for x in conf.T]
    hover1 = []
    for z in range(len(z_text_train)):
        hover1.append(
            [
                "Actual Class:"
                + x[i]
                + "<br>"
                + "Predicted:"
                + y[z]
                + "<br>"
                + "Instances:"
                + str(
                    conf[i, z]
                )  # + "Variance " +  str(confusion_matrix_variance[i,z])
                for i, _ in enumerate(z_text_train[z])
            ]
        )

    fig1 = ff.create_annotated_heatmap(
        z=conf.T,
        x=x,
        y=y,
        text=hover1,
        hoverinfo="text",
        colorscale=colorscale,
        name="Absolute",
        visible=True,
    )
    fig1.update_yaxes(autorange="reversed")
    fig1.update_layout(
        width=600, height=500, autosize=False, margin=dict(t=0, b=0, l=0, r=0)
    )
    return fig1



def create_parallel_coordiante_dict(df, hyp, metric_labels=["val_loss", "val_accuracy"], include_random_seed=True, cutoff_value=None):
    date_to_idx = {val:idx for idx, val in enumerate(sorted(set(df.columns.get_level_values(1))))}
    exps = utils.return_runs_columns(df)
    imp_cols = utils.return_first_col_per_run(df)
    metrics = set(df.columns.get_level_values(3))
    dimensions_date = list([
            dict(ticktext = [str(x)[5:16] for x in set(df.columns.get_level_values(1))],
                 tickvals = list(date_to_idx.values()),
                 label = 'Date', values =[date_to_idx[x[1]] for x in exps]),
            dict(range = [0,max([x[-1] for x in exps])],
                 label = 'Run', values = [x[-1] for x in exps])])

    
    if include_random_seed:
        values = [str(x) for x in df.loc["other","random_seed"].values]
        unique_values = sorted(set(values))
        val_to_idx = {val:idx for idx, val in enumerate(unique_values)}
        random_seed = [dict(ticktext = [str(x)for x in unique_values],
                tickvals = list(val_to_idx.values()),
                label = "Random Seed", values =[val_to_idx[x] for x in values])]

            
    dimension_hyp = []
    for row in hyp.index:
        if all([type(x) == int or type(x) == float for x in hyp.loc[row].values]):
            entry = dict(range = [min(hyp.loc[row].values),max(hyp.loc[row].values)],
                 label = str(row), values = hyp.loc[row].iloc[imp_cols].values)
        else:
            values = [str(x) for x in hyp.loc[row].iloc[imp_cols].values]
            unique_values = sorted(set(values))
            val_to_idx = {val:idx for idx, val in enumerate(unique_values)}
            entry = dict(ticktext = [str(x)for x in unique_values],
                 tickvals = list(val_to_idx.values()),
                 label = str(row), values =[val_to_idx[x] for x in values])
        dimension_hyp.append(entry)


    df_metric = df.loc["metric"]
    dimension_metrics = []
    for row in set(df.columns.get_level_values(3)):
        if not row in metric_labels:
            continue        
        if "loss" in row:
            imp = df.columns.get_level_values(3) == row
            values = df_metric.loc["roll_min",imp].values
            if row == metric_labels[0] and cutoff_value:
                max_val = cutoff_value
            else:
                max_val = max(values)
            min_val = min(values)
            entry = dict(range = [max_val,min_val],
                    label = str(row), values = values)
        elif "accuracy" in row:
            imp = df.columns.get_level_values(3) == row
            values = df_metric.loc["roll_max",imp].values
            if row == metric_labels[0] and cutoff_value:
                min_val = cutoff_value
            else:
                min_val = min(values)
            max_val = max(values)
            entry = dict(range = [min_val,max_val],
                    label = str(row), values = values)
        dimension_metrics.append(entry)
    if include_random_seed:
        dimensions = dimensions_date + random_seed + dimension_hyp + dimension_metrics
    else:
        dimensions = dimensions_date + dimension_hyp + dimension_metrics
    return dimensions