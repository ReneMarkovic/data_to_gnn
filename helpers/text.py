import streamlit as st

intro = """
        This tool helps you prepare a dataset for graph neural networks. Start by uploading
        your node table. This table should contain node-specific information. Next, you will
        upload your edge table, which defines the relationships between nodes.
    """

def show_intro():
    st.title("Graph Dataset Preparation Tool")
    st.write(intro)