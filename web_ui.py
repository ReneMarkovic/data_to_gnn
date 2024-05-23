import streamlit as st
import pandas as pd
import torch
import numpy as np
from torch_geometric.data import Data
import Utils as hf1
import os
import matplotlib.pyplot as plt

    
# Main function
check_2 = False
def main():
    logo_path = os.path.join("img","logo.png")  # Replace with the correct path to your logo image
    st.image(logo_path, width=600)
    hf1.show_intro()
    
    st.session_state['expander_state_step1'] = True
    
    with st.expander("Step 1: Upload OR Generate Node Data", expanded=st.session_state['expander_state_step1']):
        node_data_choice = hf1.node_data()
    
    dB = hf1.edge_data(node_data_choice)
    
    if dB:
        db = hf1.generate_DB(st.session_state)
        st.session_state['db'] = db
        
    if 'db' in st.session_state:
        #Generate the dataset
        st.write("")
        st.write("-----------------------------------------------------------------")
        st.write("")
        st.header("Step 3: Generate Dataset")
        
        root = os.path.join('data')
        os.makedirs(root, exist_ok=True)
        if st.button('Generate Graph Data'):
            print("Dataset generation started...")
            db = st.session_state['db']
            print("Dataset object created...")
            generated_dataset = db.create_graph() # This should save the .pt file in 'path/to/data/processed'
            db.draw_G(generated_dataset)
            ##st.pyplot(plt)
            print("Dataset processed...")
            st.write("Dataset generated successfully!")
            st.write("Here is a sample of the processed data:")
            st.write(generated_dataset)
            
            # Provide download link
            with open(os.path.join('data','processed','data.pt'), "rb") as file:
                st.download_button(label="Download Processed Data (.pt file)", data=file, file_name='processed_graph_data.pt', mime='application/octet-stream')

if __name__ == "__main__":
    main()