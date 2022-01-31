import base64
import streamlit as st
from pathlib import Path
from . import resources
import os

def render_svg(path):
    """Renders the given svg string."""
    with open(path, 'r+') as file:
        svg = file.read()
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    return html

def header():
    st.set_page_config(layout="wide")
    col1, col2 = st.beta_columns(2)
    title = """
                <style>
                .big-font {
                    font-size:66px !important;
                }
                </style>
                <p class="big-font">Experiment Tracker</p>"""

    col1.markdown(title, unsafe_allow_html=True)
    p = Path(resources.__path__._path[0])
    col2.write(render_svg(os.path.join(p,"logo_csem.svg")), unsafe_allow_html=True)