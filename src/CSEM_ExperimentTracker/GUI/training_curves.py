import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
from CSEM_ExperimentTracker import load_files, plots, utils
import plotly.graph_objects as go
import os
from shutil import rmtree
import plotly.express as px
from pathlib import Path
import matplotlib 
from dataclasses import dataclass

@dataclass
class Options:
    metrics: list
    data: list
    roll: int

class Container:
    key =  ["val_loss","val_accuracy", "val_ht_accuracy"]



def training_curves(fin_df,exp,opt):
    fig = go.Figure()
    colors = px.colors.qualitative.Plotly
    color_counter = 0
    col1, col2 = st.beta_columns(2)
    measurement = False
    if col1.button("Cut measurements"):
        measurement = True
    if col2.button("Complete measurements"):
        measurement = False 
    for metric in groups.keys():
        for to_average in groups[metric]:
            if not str(dict(exp.iloc[:,to_average[0]])) in entries:
                continue
            if len(str(dict(exp.iloc[:,to_average[0]]))) > 100:
                name = ""
            else:
                name = str(dict(exp.iloc[:,to_average[0]]))
                
            important = fin_df.iloc[:,to_average]
            if measurement:
                data = important.loc["epoch"].dropna()
            else:
                data = important.loc["epoch"].dropna(how="all")
            mean = list(data.mean(axis=1).rolling(opt.roll).mean())
            color = colors[color_counter]
            fig.add_trace(
                go.Scatter(
                    x=list(data.index),
                    y=mean,
                    name=name,
                    line=dict(color=color),
                )
            )
        
            y_upper = mean + data.std(axis=1,skipna=True,ddof=0).rolling(roll).mean().values
            y_lower = mean - data.std(axis=1,skipna=True,ddof=0).rolling(roll).mean().values
            rgb_color = ",".join([str(x) for x in matplotlib.colors.to_rgba(color)[:3] + (0.2,)])
            for col in data.columns:
                pos = data[col].dropna().index[-1]
                fig.add_vline(x=pos, line_width=1, line_dash="dash", line_color=color)
            
            fig.add_trace(go.Scatter(
                x=list(data.index)+list(data.index)[::-1], # x, then x reversed
                y=np.concatenate([y_upper,y_lower[::-1]]), # upper, then lower reversed
                fill='toself',
                fillcolor=f'rgba({rgb_color})',
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip"))
            color_counter = (color_counter + 1) % len(colors)

    fig.update_yaxes(type="log",range=[-0.2,0])
    fig.update_layout(
        autosize=True,
        width=1450,
        height=750)
    st.write(fig)

    fig = go.Figure()
    for idx, i in enumerate(set(df_plot.columns.droplevel(-1))):
        for x in key:
            fig.add_trace(
                go.Scatter(
                    x=list(df_plot.loc["epoch"].index),
                    y=list(df_plot.loc["epoch", i + (x,)].rolling(roll).mean()),
                    name=str(str(exp[i + (x,)])[:50])
                )
            )
    fig.update_yaxes(type="log",range=[-0.2,0])
    fig.update_layout(
        autosize=True,
        width=2000,
        height=1000)
    st.write(fig)

def parallel_coordinates(fin_df,exp,opt):
    df = utils.compute_rolling_window_metrics(fin_df, roll=opt.roll)
    hyp = utils.drop_not_changing_row(df.loc["hyp"]).dropna()
    groups, available_dates = utils.groupby_random_seed(exp,opt.metrics)

    type_exp = st.radio("Select type", options=["all","aggregate"])

    if type_exp == "all":
        for key in groups.keys():
            for val in groups[key]:
                pool.extend(val)
        df = df.iloc[:,pool] 
        hyp = hyp.iloc[:,pool]
    elif type_exp == "aggregate":
        dfs = []
        group_fin = []
        for key in groups.keys():
            for group in groups[key]:
                df_tmp = df.iloc[:,group[0]].copy()
                df_tmp.loc["metric"] = df.iloc[:,group].loc["metric"].mean(axis=1).values
                dfs.append(df_tmp)
                group_fin.append(group[0])
        df = pd.concat(dfs,axis=1)        
        hyp = hyp.iloc[:,group_fin]
    include_random_seed = type_exp == "all"
    entries = plots.create_parallel_coordiante_dict(df,hyp, metric_labels=metrics, include_random_seed=include_random_seed)
    fig = go.Figure(data=
        go.Parcoords(
            line = dict(color = df.loc[("metric","min")].values,
                    colorscale = 'Jet',
                    showscale = True,
                    cmin = df.loc[("metric","min")].min(),
                    cmax = df.loc[("metric","min")].max()),
            dimensions = entries
        )
    )
    fig.update_layout(
        autosize=True,
        width=2000,
        height=1000)
    st.write(fig)


def fresh():
    folder = st.selectbox("Select Experiment Source", options=["UV_DATA_RESNET","UV_DATA_TIMEINCEPTION","BERTINO_ALL_IN_ONE"])
    base_bath = "../gemintelligence/runs/"
    if st.button('Recreate Dataset'):
        f = os.path.join(base_bath,folder)
        df = load_files.load_lightning(f)
        pd.to_pickle(df, "{}.df".format(folder))
    st.title("Current Results")
    st.write("Results")
    curr = pd.read_pickle(f"{folder}.df")
        
    #TotalDf = st.write(pd.DataFrame(curr))
    possibilities = list(utils.list_available_dates(curr))
    labels = [str(x)[:19] for x in sorted(list(utils.list_available_dates(curr)))]

    options = [st.selectbox("Select Date", options=labels)]
    if st.button('Click to delete this date'):
        if st.button('Are you sure?'):
            for opt in options:
                date = opt.split(" ")[0]
                time = opt.split(" ")[1].replace(":","-")
                rmtree(os.path.join(base_bath,folder,date,time))
    if options:
        dfs = []
        for opt in options:
            df = utils.return_exp_based_on_datetime(curr,opt[:10], opt[10:19])
            dfs.append(df)
        fin_df = pd.concat(dfs, axis=1)

    name =st.text_input("Store with a different name")
    if st.button('Save'):
        fin_df.to_pickle(f"data/{name}")
            #     break
            # if col2.button('Cancel'):
            #     break
    return fin_df

def stored():
    base_path = "."
    data_path = os.path.join(base_path, "data/")
    exps = [Path(os.path.join(data_path,x)) for x in os.listdir(data_path)]
    if not exps:
        st.write("Not experiments available, check if the data folder is populated")
        st.stop()
    else:
        option = st.selectbox("Select Experiment", options=[x.stem for x in exps])
        fin_df = pd.read_pickle(os.path.join(data_path,option))
    return fin_df


if __name__=="__main__":
    st.set_page_config(layout="wide")
    col1, col2 = st.beta_columns(2)
    col1.title("CSEM Experiment Tracker")
    breakpoint()
    col2.image("CSEM_Experiement")
    type_exp = st.radio("Select source", options=["Fresh","Stored"])
    if type_exp == "Fresh":
        fin_df = fresh()
    else:
        fin_df = stored()
    if len(utils.drop_not_changing_row(fin_df.loc["hyp"].dropna(how="all"))):
        exp = utils.drop_not_changing_row(fin_df.loc["hyp"].dropna(how="all"))
    else:
        exp = fin_df.loc["hyp"].dropna(how="all")
    st.markdown('### Select rolling window length for computing statistics')
    roll = st.slider("Length", min_value=1, max_value=10, value=None, step=1, format=None, key=None)
    key = Container.key
    metrics = st.multiselect("Select Metric", options=key, default=[key[-1]])
    df_plot = utils.subcolumn_group(fin_df,metrics)
    groups, available_dates = utils.groupby_random_seed(exp,metrics)
    data = st.multiselect("Available data", options=list(available_dates))
    opt = Options(metrics=metrics, dates=data, roll=roll)
    Curr = st.write(exp, width=2048, height=768)
    options = ["Training Curves", "Parallel Coordinate"]
    if options:
        visualizer = st.radio("Select Visualization Type", options, index=0, key=None)
    if visualizer ==  "Training Curves":
        training_curves(fin_df,exp, opt)
    elif visualizer == "Parallel Coordinate":
        parallel_coordinates(fin_df,exp, opt) 

    