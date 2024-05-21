import streamlit as st
import pandas as pd
import torch
import numpy as np
from torch_geometric.data import Data
import webui as hf1
import os
import matplotlib.pyplot as plt

    
# Main function
def main():
    hf1.show_intro()
    
    st.header(" Step 1: Upload OR Generate Node Data")
    
    progress = st.progress(0, text = "Step 1/5: Upload Node Table")
    node_data_choice = st.radio(
        "Choose how to provide NODE data:",
        ('Generate NODE Data', 'Upload NODE Data')
    )
    
    if node_data_choice == 'Generate NODE Data':
        with st.expander("Generate Node Table"):
            # Option to generate node data
            with st.form("node_data_form"):
                submit_button, num_nodes, num_features = hf1.generate_dummy_node_data()
            
            if submit_button:
                node_data = hf1.generate_node_data(num_nodes, num_features)
                # Convert DataFrame to CSV for downloading
                csv = hf1.convert_df_to_csv(node_data)
                
                # Create a download button and provide the CSV file to download
                st.download_button(
                    label="Download Node Data as CSV",
                    data=csv,
                    file_name='node_data.csv',
                    mime='text/csv',
                )
                hf1.describe_node_data(node_data)
                st.session_state['node_data'] = node_data
    
    if node_data_choice == 'Upload NODE Data':
        with st.expander("Upload Node Table"):
            uploaded_file = st.file_uploader("Step 1/4: Upload Node Table", type=['csv', 'xlsx', 'json'])
            if uploaded_file is not None:
                node_data = hf1.read_data(uploaded_file)
                st.write("Uploaded Node Table:")
                st.dataframe(node_data)
                # Store node data in session to use later
                st.session_state['node_data'] = node_data
                hf1.describe_node_data(node_data)

    # Upload edge table only if node data is uploaded
    check_2 = False
    if 'node_data' in st.session_state:
        st.write("")
        st.write("-----------------------------------------------------------------")
        st.write("")
        st.header(" Step 2: Upload OR Generate Edge Table")
        progress = st.progress(1/5, text = "")
        #print(st.session_state['node_data'])
        edge_data_choice = st.radio(
            "Choose how to provide edge data:",
            ('Generate Edge Data', 'Upload Edge Data')
        )
        
        if edge_data_choice == 'Generate Edge Data':
            with st.expander("Generate Edge Table"):
                edge_data = hf1.generate_edge_data(st.session_state['node_data'], f_edges = 0.1)
                hf1.describe_edge_data(edge_data)
                # Convert DataFrame to CSV for downloading
                csv = hf1.convert_df_to_csv(edge_data)
                
                # Create a download button and provide the CSV file to download
                st.download_button(
                    label="Download Edge Data as CSV",
                    data=csv,
                    file_name='edge_data.csv',
                    mime='text/csv',
                )
                st.session_state['edge_data'] = edge_data
                check_2 = True
        
        if edge_data_choice == 'Upload Edge Data': 
            with st.expander("Upload Edge Table"):
                if 'node_data' in st.session_state:
                    uploaded_file = st.file_uploader("Step 2/4: Upload Edge Table", type=['csv', 'xlsx', 'json'])
                    if uploaded_file is not None:
                        edge_data = hf1.read_data(uploaded_file)
                        st.write("Uploaded Edge Table:")
                        st.dataframe(edge_data)
                        hf1.describe_edge_data(edge_data)
                        st.session_state['edge_data'] = edge_data
                        check_2 = True
    
    
    
    check_3 = False
    if check_2:
        st.write("")
        st.write("-----------------------------------------------------------------")
        st.write("")
        st.header(" Step 3: Assign Node Columns")
        progress = st.progress(3/5, text = "")
        with st.expander("Node Columns"):
            st.dataframe(st.session_state['node_data'].head(5))
            with st.form("Assign Node Columns"):
                st.write("Assign columns as ID, Name, Label, or Features:")
                columns = st.session_state['node_data'].columns
                col_node_roles = {col: st.selectbox(f"Select role for {col}:", ['Features', 'ID', 'Name', 'Label'], key=col) for col in columns}
                submit_roles_nodes = st.form_submit_button("Assign Roles and Generate Dataset")
                check_3 = True
    
    check_4 = False
    if check_3:
        st.write("")
        st.write("-----------------------------------------------------------------")
        st.write("")
        st.header(" Step 4: Assign Edge Columns")
        progress = st.progress(4/5, text = "Step 4/5")
        with st.expander("Edge Columns"):
            with st.form("Assign Edge Columns"):
                st.write("Assign columns as Source ID, Target ID or Features:")
                columns = st.session_state['edge_data'].columns
                col_edge_roles = {col: st.selectbox(f"Select role for {col}:", ['Source ID', 'Target ID', 'Features', 'Label'], key=col) for col in columns}
                submit_roles_edges = st.form_submit_button("Assign Roles and Generate Dataset")
                check_4 = True
        
    if check_4:
        print(check_2, check_3, check_4)
        #Generate the dataset
        st.write("")
        st.write("-----------------------------------------------------------------")
        st.write("")
        st.header(" Step 5: Generate Dataset")
        progress = st.progress(5/5, text = "Step 5/5")
        node_data = st.session_state['node_data']
        edge_data = st.session_state['edge_data']
        node_roles = col_node_roles
        edge_roles = col_edge_roles
        
        root = os.path.join('data')
        os.makedirs(root, exist_ok=True)
        if st.button('Generate Graph Data'):
            print("Dataset generation started...")
            dataset = hf1.Generate_Dataset(
                root = root,
                node_data = st.session_state['node_data'],
                edge_data = st.session_state['edge_data'],
                node_roles = node_roles,
                edge_roles = edge_roles
            )
            print("Dataset object created...")
            generated_dataset = dataset.process()  # This should save the .pt file in 'path/to/data/processed'
            st.pyplot(plt)
            print("Dataset processed...")
            st.write("Dataset generated successfully!")
            st.write("Here is a sample of the processed data:")
            st.write(generated_dataset)
            
            # Provide download link
            with open(os.path.join('data.pt'), "rb") as file:
                st.download_button(label="Download Processed Data (.pt file)", data=file, file_name='processed_graph_data.pt', mime='application/octet-stream')

        

if __name__ == "__main__":
    main()