import streamlit as st
import experiment_tracker
from experiment_tracker import hydra_utils
from pathlib import Path
import pandas as pd

def main():
    # Make the layout wider
    st.set_page_config(layout="wide")
    st.markdown("## Results")

    query_string = st.text_input("Which rows do you want to load?", "*") # This means we are going to collect all the files in the folder
    # This command load all the multirun experiments (i.e. the one run with the flag -m) in the folder "multirun" 
    df_multirun = experiment_tracker.load_project(base_path="multirun", query_string=query_string, logic="multirun")
    # This command load all the singlerun experiments (i.e. the one run without the flag -m) in the folder "output"
    try:
        df_singlerun = experiment_tracker.load_project(base_path="outputs", query_string=query_string, logic="singlerun")
    except ValueError:
        df_singlerun = pd.DataFrame()

    st.markdown("### Multirun experiments")
    st.write(df_multirun)

    st.markdown("### Singlerun experiments")
    st.write(df_singlerun)

    # Hydra configu columns:
    hydra_config_columns = [x for x in df_multirun.columns if not x.startswith("collected_path")]
    # Columns with the collected paths
    collected_path_columns = [x for x in df_multirun.columns if x.startswith("collected_path")]

    st.markdown("### Hydra config columns")
    st.write(hydra_config_columns)

    st.markdown("### Collected path columns")
    st.write(collected_path_columns)
    print("Hydra config columns in multirun:", hydra_config_columns)
    print("Collected path columns in multirun:", collected_path_columns)

    # You can filter by any condition you want
    # For example, let's say we want to filter by the dataset
    dataset = st.selectbox("Dataset", ["digits","iris"])
    df_multirun = df_multirun[df_multirun["dataset"] == dataset]
    df_singlerun = df_singlerun[df_singlerun["dataset"] == dataset]

    # Let's say we want to filter by the estimator
    estimator = st.selectbox("Estimator", ["random_forest","svm","knn"])
    df_multirun = df_multirun[df_multirun["estimator"] == estimator]

    # Let's say we want to filter by the normalize flag
    normalize = st.selectbox("Normalize", [True,False])
    df_multirun = df_multirun[df_multirun["normalize"] == normalize]

    # Once you have the dataframe you can also open the specific files and do whatever you want with them
    # For example, let's say we want to plot the confusion matrix

    result_dict = {}
    for row, path in hydra_utils.iterate_paths(df_multirun, "test.pkl"):

        current = pd.read_pickle(path)
        # Compute the confusion matrix
        confusion_matrix = pd.crosstab(current["y_true"], current["y_pred"], rownames=['Actual'], colnames=['Predicted'])

        result_dict[row] = confusion_matrix

    st.markdown("### Confusion matrix")
    entry = st.selectbox("Confusion matrix", result_dict)
    # Write also the parameters
    col1, col2 = st.columns(2)
    col1.write(df_multirun.loc[entry][hydra_config_columns])
    col2.write(result_dict[entry])



if __name__ == "__main__":
    main()