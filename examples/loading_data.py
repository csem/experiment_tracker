import streamlit as st
from csem_exptrack import process
from csem_exptrack.gui import gui_utils

def start():
    gui_utils.header()
    st.title('Load results')
    loader = process.file_loader.FileLoader(query_string="metric.npy")
    st.title("Select experiment")
    l = ["runs/lstm_hy_pa_finetuning"]
    df = loader.load_folder("runs/lstm_hy_pa_finetuning").sort_index(axis=1)

if __name__=="__main__":
    start()