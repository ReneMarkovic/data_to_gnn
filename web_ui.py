import streamlit as st
import pandas as pd
import torch
import numpy as np
from torch_geometric.data import Data
import Utils as hf1
import os
import matplotlib.pyplot as plt
def clear_session_state():
    for key in st.session_state.keys():
        del st.session_state[key]

# Main function
def main():
    logo_path = os.path.join("img", "logo.png")  # Replace with the correct path to your logo image
    st.image(logo_path, width=600)
    hf1.show_intro()
    
    # Add a reset button at the end
    if st.button('Reset'):
        clear_session_state()
        st.experimental_rerun()

    # Initialize session state variables if not already set
    if "node_choice" not in st.session_state:
        st.session_state["node_choice"] = False
    if "expander_state_step1" not in st.session_state:
        st.session_state['expander_state_step1'] = True

    st.header("Step 1: Upload OR Generate Node Data")
    node_data_choice = hf1.node_data()
    st.session_state["node_choice"] = node_data_choice

    dB = False
    if st.session_state["node_choice"]:
        dB = hf1.edge_data()

    if dB:
        db = hf1.generate_DB(st.session_state)
        st.session_state['db'] = db

    if 'db' in st.session_state:
        # Generate the dataset
        st.write("")
        st.write("-----------------------------------------------------------------")
        st.write("")
        st.header("Step 3: Generate Dataset")

        root = os.path.join('data')
        os.makedirs(root, exist_ok=True)
        if st.button('Generate Graph Data'):
            st.write("Dataset generation started...")
            db = st.session_state['db']
            generated_dataset = db.create_graph()  # This should save the .pt file in 'path/to/data/processed'
            st.write("Dataset processed...")
            st.write("Dataset generated successfully!")
            st.write("Here is a sample of the processed data:")
            st.write(generated_dataset)
            db.draw_G(generated_dataset)
            # Provide download link
            with open(os.path.join('data', 'processed', 'data.pt'), "rb") as file:
                st.download_button(label="Download Processed Data (.pt file)", data=file, file_name='processed_graph_data.pt', mime='application/octet-stream')

if __name__ == "__main__":
    main()