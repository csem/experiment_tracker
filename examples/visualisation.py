import streamlit as st
import experiment_tracker

def main():
    # Make the layout wider
    st.set_page_config(layout="wide")
    st.markdown("## Results")

    # This command load all the multirun experiments (i.e. the one run with the flag -m) in the folder "multirun" 
    df_multirun = experiment_tracker.load_project(base_path="multirun", query_string="*", logic="multirun")
    # This command load all the singlerun experiments (i.e. the one run without the flag -m) in the folder "output"
    df_singlerun = experiment_tracker.load_project(base_path="outputs", query_string="*", logic="singlerun")

    breakpoint()

if __name__ == "__main__":
    main()