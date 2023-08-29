import plotly
import plotly.graph_objects as go
import plotly.express as px
from .. import pandas_utils
import plotly.figure_factory as ff
import numpy as np
import pandas as pd
import streamlit as st

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



def interactive_confusion_matrix(conf, class_names=None, colorscale="electric", width=600, height=500, ispercent = False):
    """
    args:
        conf: confusion matrix
        classes: list of classes
        colorscale: colorscale
        width: width of plot
        height: height of plot
        ispercent: if true, plot is in percentage
    """
    x = class_names
    y = class_names
    if ispercent:
        z_text_train = [[str(np.round(y,2)*100)[:3] + "%" for y in x] for x in conf.T]
    else:
        z_text_train = [[str(y) for y in x] for x in conf.T]

    hover1 = []
    for z in range(len(z_text_train)):
        hover1.append(
            return_annotations(z,z_text_train,x,y)
        )

    fig1 = ff.create_annotated_heatmap(
        z=conf.T,
        x=x,
        y=y,
        annotation_text=z_text_train, #list(zip(*z_text_train)),
        text=hover1,
        hoverinfo="text",
        colorscale=colorscale,
        name="Absolute",
        visible=True,
    )
    fig1.update_yaxes(autorange="reversed")
    fig1.update_layout(
        width=width, height=height, autosize=False, margin=dict(t=0, b=0, l=0, r=0)
    )
    return fig1

def return_annotations(z,z_text_train, x,y):
    tmp_array = []
    for i, _ in enumerate(z_text_train[z]):      
        tmp = "Actual Class:"+ x[i] + "<br>" + "Predicted:" + y[z] + "<br>" + "Instances:" + str(z_text_train[z][i]) 
        tmp_array.append(tmp)
    return tmp_array
                
        
    

def parallel_coordinates(param_df:pd.DataFrame,perf_df:pd.DataFrame):  
    param_df = param_df.loc[:, perf_df.index]
    entries = _create_parallel_coordiante_dict(param_df,perf_df)
    fig = go.Figure(data=
        go.Parcoords(
            line = dict(color = perf_df.iloc[:,0].replace(None).values,
                    colorscale = 'Jet',
                    showscale = True,
                    cmin = perf_df.iloc[:,0].min(),
                    cmax = perf_df.iloc[:,0].max()),
            dimensions = entries
        )
    )
    fig.update_layout(
        autosize=True,
        width=2000,
        height=1000)
    st.write(fig)
    return fig

def _create_parallel_coordiante_dict(param_df, perf_df):
    cols = sorted(set(param_df.columns.get_level_values(1))) 
    date_to_idx = {val:idx for idx, val in enumerate(set(param_df.columns.get_level_values(0)))}
    date_runs = param_df.columns.get_level_values(0)
    runs = param_df.columns.get_level_values(1)
    dimensions_date = [
            #Dates
            dict(ticktext = [str(x)[5:16] for x in set(param_df.columns.get_level_values(0))],
                tickvals = list(date_to_idx.values()),
                label = 'Date', values =[date_to_idx[x] for x in date_runs]),
            
            #Runs
            dict(range = [0,max([x for x in runs])],
                 label = 'Run', values = [x for x in runs])]

    if ("other","random_seed") in param_df.index:
        values = [str(x) for x in param_df.loc["other","random_seed"].values]
        unique_values = sorted(set(values))
        val_to_idx = {val:idx for idx, val in enumerate(unique_values)}
        random_seed = [dict(ticktext = [str(x)for x in unique_values],
                tickvals = list(val_to_idx.values()),
                label = "Random Seed", values =[val_to_idx[x] for x in values])]
    else:
        random_seed = [None]
            
    dimension_hyp = []
    hyp_df = param_df.loc["hyperparameters"]
    for row in hyp_df.index:
        if all([type(x) == int or type(x) == float for x in hyp_df.loc[row].values]):
            entry = dict(range = [min(hyp_df.loc[row].values),max(hyp_df.loc[row].values)],
                 label = str(row), values = hyp_df.loc[row].values)
        else:
            values = [str(x) for x in hyp_df.loc[row].values]
            unique_values = sorted(set(values))
            val_to_idx = {val:idx for idx, val in enumerate(unique_values)}
            entry = dict(ticktext = [str(x)for x in unique_values],
                 tickvals = list(val_to_idx.values()),
                 label = str(row), values =[val_to_idx[x] for x in values])
        dimension_hyp.append(entry)

    dimension_metrics = []
    for col in perf_df.columns:
        values = perf_df.loc[:,col].values
        min_val = min(values)
        max_val = max(values)
        entry = dict(range = [min_val,max_val],
                label = str(col), values = values)
        dimension_metrics.append(entry)
    dimensions = dimensions_date + random_seed + dimension_hyp + dimension_metrics
    dimensions = [x for x in dimensions if x]
    return dimensions