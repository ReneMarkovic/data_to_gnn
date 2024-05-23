import streamlit as st
import pandas as pd
import chardet
import numpy as np
from .webui_datahandling import convert_df_to_csv, read_data, describe_node_data
import os

def generate_dummy_node_data():
    st.write("Generate Dummy Node Data:")
    num_nodes = st.number_input("Enter the number of nodes:", min_value=1, value=11)
    num_features = st.number_input("Enter the number of features:", min_value=0, value=5)
    submit_button = st.form_submit_button(label='Generate Node Data')
    return [submit_button, num_nodes, num_features]

# Generate data
def generate_node_data(num_nodes, num_features):
    data = {
        "ID": range(1, num_nodes + 1),
        "Name": [f"Person{i}" for i in range(1, num_nodes + 1)]
    }
    for i in range(num_features-1):
        data[f"Feature_{i+1}"] = np.random.rand(num_nodes)
    data[f"Feature_{num_features}"]=np.random.choice(["A","B","C"],num_nodes)
    return pd.DataFrame(data)

def node_data() -> str:
    st.header(" Step 1: Upload OR Generate Node Data")
    node_data_choice = st.radio(
        "Choose how to provide NODE data:",
        ('Upload NODE Data', 'Generate NODE Data')
    )
    
    if node_data_choice == 'Generate NODE Data':
        st.write("Generate Node Table")
        with st.form("node_data_form"):
            submit_button, num_nodes, num_features = generate_dummy_node_data()
        if submit_button:
            node_data = generate_node_data(num_nodes, num_features)
            # Convert DataFrame to CSV for downloading
            csv = convert_df_to_csv(node_data)
            
            # Create a download button and provide the CSV file to download
            st.download_button(
                label="Download Node Data as CSV",
                data=csv,
                file_name='node_data.csv',
                mime='text/csv',
            )
            describe_node_data(node_data)
            st.session_state['node_data'] = node_data
            st.session_state['expander_state_step1']=False
        return node_data_choice

    if node_data_choice == 'Upload NODE Data':
        uploaded_files = st.file_uploader("Step 1/4: Upload Node Tables", type=['csv', 'xlsx', 'json'], accept_multiple_files=True)
        if uploaded_files is not None:
            node_data_list = []
            for ti, uploaded_file in enumerate(uploaded_files):
                node_data = read_data(uploaded_file)
                if node_data is not None:
                    #node_data_list[uploaded_file.name]=node_data
                    default_name = os.path.splitext(uploaded_file.name)[0]
                    col1, col2 = st.columns(2)
                    with col1:
                        custom_name = st.text_input(f"Enter a custom name for the table {uploaded_file.name}:", value=default_name, key=f"name_{uploaded_file.name}")
                    
                    with col2:
                        pkey_column = st.selectbox(f"Select the pkey column for {custom_name}:", node_data.columns, key=f"pkey_{uploaded_file.name}")
                    
                    selected_columns = st.multiselect('Select columns to display', node_data.columns.tolist(), default=node_data.columns.tolist())
                    node_data = node_data[selected_columns]
                    
                    st.write(f"Uploaded Node Table: {uploaded_file.name}")
                    st.dataframe(node_data.head(10))
                    
                    # Store the node data and its pkey in session state
                    st.session_state[f'node_data_{custom_name}'] = {
                        'data': node_data,
                        'pkey': pkey_column
                    }
                    
                    # Append to the list
                    node_data_list.append({
                        'name': custom_name,
                        'data': node_data,
                        'pkey': pkey_column
                    })
    
        if node_data_list:
            if st.button('Continue to Step 2: Define table relations'):
                st.session_state['node_data_list'] = node_data_list
                st.session_state['node_data'] = {item['name']: item for item in node_data_list}
                st.success('Node data has been successfully set!')
                st.session_state['expander_state_step1']=False
        return node_data_choice