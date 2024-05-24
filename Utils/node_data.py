import streamlit as st
import pandas as pd
import chardet
import numpy as np
from .webui_datahandling import convert_df_to_csv, read_data, describe_node_data, generate_edge_data
import os

def generate_dummy_node_data():
    st.write("Generate Dummy Node Data:")
    num_nodes = st.number_input("Enter the number of nodes:", min_value=1, value=11, key='num_nodes')
    num_features = st.number_input("Enter the number of features:", min_value=0, value=5, key='num_features')
    edge_density = st.number_input("Edge density (0 - 100):", min_value=0, value=10, max_value=100, key='edge_density')
    submit_button = st.form_submit_button(label='Generate Node Data')
    return [submit_button, num_nodes, num_features, edge_density]

# Generate data
def generate_node_data(num_nodes, num_features):
    data = {
        "ID": range(1, num_nodes + 1),
        "Name": [f"Person{i}" for i in range(1, num_nodes + 1)]
    }
    for i in range(num_features - 1):
        data[f"Feature_{i + 1}"] = np.random.rand(num_nodes)
    data[f"Feature_{num_features}"] = np.random.choice(["A", "B", "C"], num_nodes)
    return pd.DataFrame(data)

def display_node_data_form(node_data, i):
    default_name = f"Table{i+1}"
    col1, col2 = st.columns(2)
    with col1:
        custom_name = st.text_input(f"Enter a custom name for {default_name}:", value=default_name, key=f"name_{default_name}_{i}")
    with col2:
        pkey_column = st.selectbox(f"Select the pkey column for {custom_name}:", node_data.columns, key=f"pkey_{default_name}_{i}")
    selected_columns = st.multiselect('Select columns to display', node_data.columns.tolist(), default=node_data.columns.tolist(), key=f"select_columns_{default_name}_{i}")
    node_data = node_data[selected_columns]
    st.write(f"Node Table: {default_name}")
    st.dataframe(node_data.head(10))
    return custom_name, pkey_column, node_data

def process_uploaded_files(uploaded_files):
    node_data_list = []
    for ti, uploaded_file in enumerate(uploaded_files):
        node_data = read_data(uploaded_file)
        if node_data is not None:
            custom_name, pkey_column, node_data = display_node_data_form(node_data, ti)
            st.session_state[f'node_data_{custom_name}'] = {
                'data': node_data,
                'pkey': pkey_column
            }
            node_data_list.append({
                'name': custom_name,
                'data': node_data,
                'pkey': pkey_column
            })
    return node_data_list

def node_data():
    node_data_choice = st.radio("Choose how to provide NODE data:", ('Upload NODE Data', 'Generate NODE Data'))

    if node_data_choice == 'Generate NODE Data':
        st.write("Generate Node Table")
        with st.form("node_data_form"):
            submit_button, num_nodes, num_features, edge_density = generate_dummy_node_data()
            if submit_button:
                node_data = generate_node_data(num_nodes, num_features)
                edge_data = generate_edge_data(node_data, f_edges=edge_density/100.0)
                data_source = [node_data, edge_data]

                st.session_state['data_source'] = data_source
                st.session_state['node_data_generated'] = True
                st.session_state['node_choice'] = True

    if st.session_state.get('node_data_generated', False):
        data_source = st.session_state['data_source']
        node_data_list = []
        
        for i, node_data in enumerate(data_source):
            custom_name, pkey_column, node_data = display_node_data_form(node_data, i)
            st.session_state[f'node_data_{custom_name}'] = {
                'data': node_data,
                'pkey': pkey_column
            }
            node_data_list.append({
                'name': custom_name,
                'data': node_data,
                'pkey': pkey_column
            })

        if node_data_list and st.button('Data generated: Define table relations'):
            st.session_state['node_data_list'] = node_data_list
            st.session_state['node_data'] = {item['name']: item for item in node_data_list}
            st.success('Node data has been successfully set!')
            st.session_state['expander_state_step1'] = False

    elif node_data_choice == 'Upload NODE Data':
        uploaded_files = st.file_uploader("Upload Node Tables", type=['csv', 'xlsx', 'json'], accept_multiple_files=True)
        if uploaded_files:
            node_data_list = process_uploaded_files(uploaded_files)
            if node_data_list and st.button('Continue to Step 2: Define table relations'):
                st.session_state['node_data_list'] = node_data_list
                st.session_state['node_data'] = {item['name']: item for item in node_data_list}
                st.success('Node data has been successfully set!')
                st.session_state['expander_state_step1'] = False
                st.session_state['node_choice'] = True
    return st.session_state.get('node_choice', False)