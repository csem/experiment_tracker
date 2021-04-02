import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
from ... import plots, utils
from ...Process import load_files
from .. import gui_utils
import plotly.graph_objects as go
import os
import pickle
from shutil import rmtree
from plotly.subplots import make_subplots


@st.cache()
def load_data(path):
    with open(path, 'rb') as handle: 
        results = pickle.load(handle)
    return results

@st.cache()
def load_experiment(f,date,time):
    return load_files.load_sklearn_experiment(f,date,time)



def start():
    st.set_page_config(layout="wide")
    gui_utils.header()
    st.title("End Results Cross Validation")
    folder = st.selectbox("Select Experiment Type", options=["STACKED","UV_DATA_RESNET","BERTINO_ALL_IN_ONE"], index=1)
    dates = os.listdir(os.path.join("../gemintelligence/runs/",folder))
    dates = [x for x in dates if os.listdir(os.path.join("../gemintelligence/runs/",folder,x))]
    date = st.selectbox("Select Date", options=dates)

    times = os.listdir(os.path.join("../gemintelligence/runs/",folder,date))
    time = st.selectbox("Select Time", options=times)
    f = os.path.join("../gemintelligence/runs/",folder)
    df = load_experiment(f,date,time)
    if not len(df): 
        st.markdown("Empty Experiment, Delete it?")
        if st.button('Click to delete'):
            rmtree(os.path.join(f,date,time))
    else:

        Curr = st.write(df.loc["hyp"], width=2048, height=768)
        runs = os.listdir(os.path.join("../gemintelligence/runs/",folder,date,time))
        candidates = [os.path.join("../gemintelligence/runs/",folder,date,time,x) for x in runs]
        runs = [x for idx, x in enumerate(runs) if os.path.isdir(candidates[idx])]
        run = st.selectbox("Select Run", options=runs)
        path = os.path.join("../gemintelligence/runs/",folder,date,time,run,"results")
        results = load_data(path)


        st.markdown('### Selet prediction threshold')
        roll = st.slider("Threshold", min_value=0.0, max_value=0.98, value=None, step=0.05, format=None, key=None)
        df = results.return_subsect_roll(roll)
        
        matrices, dropped_index = results.confusion_matrices(df=df)
        buffer = []
        buffer = buffer + ["### Stones Considered: {}% \n".format(100*np.round(len(df)/len(results.df),2))]
        buffer = buffer + ["### Results Overview \n",  "Accuracy: {}  \n F1 Score: {}  \n Cross Entropy {}  \n".format(results.compute_accuracy_score(df),results.compute_F1_score(df),results.compute_cross_entropy(df))]
        # st.write("### Results Overview \n",  "Accuracy: {}  \n F1 Score: {}  \n Cross Entropy {}  \n".format(results.compute_accuracy_score(df),results.compute_F1_score(df),results.compute_cross_entropy(df)).
        # )

        confusion_matrix = np.round(np.array(matrices).sum(axis=0))
        confusion_matrix_normalized = learning_utils.normalize_confusion_matrix(confusion_matrix,mode="precision")
        if len(confusion_matrix_normalized) == 4:
            key_order = ['Sri Lanka', 'Kashmir','Burma','Madagascar']
        else:
            key_order  = ['TE','NTE']


        #col1, col2 = st.beta_columns(2)

        fig1 = interactive_confusion_matrix(confusion_matrix,key_order, colorscale="deep")
        
        # canvas1.add_trace(fig1.data[0])
        # canvas1.update_layout(fig1.layout)
        #col1.plotly_chart(fig1, use_column_width=True, filename='first')


        fig2 = interactive_confusion_matrix(confusion_matrix_normalized,key_order, colorscale="deep")
        
        # canvas2 = create_matrix_template()
        # canvas2.add_trace(fig2.data[0]) 
        # canvas2.update_layout(fig2.layout) 
        
        #col2.plotly_chart(fig2, use_column_width=True, filename='second')

        fig = make_subplots(rows=1, cols=2)
        fig.add_trace(
        fig1.data[0],
        row=1, col=1
    )
        fig.add_trace(
            fig2.data[0],
            row=1, col=2
        )
        fig.update_yaxes(autorange="reversed", row=1, col=1)
        fig.update_yaxes(autorange="reversed", row=1, col=2)
        fig.update_layout(
            width=1100, height=500, autosize=False, margin=dict(t=0, b=0, l=0, r=0)
        )

        for annot in fig2['layout']['annotations']:
            annot['xref'] = 'x2'
        fig.layout.update(annotations= [*fig1.layout.annotations, *fig2.layout.annotations]) 
        fig['layout'].update(height=550, width=1200)
        fig.layout.xaxis.side = "top"
        fig.layout.xaxis2.side = "top"

        st.write(*buffer, "### Confusion Matrices",  fig)


    

# breakpoint()   