import pandas as pd
import numpy as np
import streamlit as st


def convert_df_to_csv(df):
    # Convert DataFrame to CSV string
    return df.to_csv(index=False).encode('utf-8')
# Read data
def read_data(uploaded_file):
    if uploaded_file.name.lower().endswith('.csv'):
        return pd.read_csv(uploaded_file)
    elif uploaded_file.name.lower().endswith('.xlsx'):
        return pd.read_excel(uploaded_file)
    elif uploaded_file.name.lower().endswith('.json'):
        return pd.read_json(uploaded_file)

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

def describe_node_data(node_data:pd.DataFrame):
    Number_of_nan = node_data.isnull().sum().sum()
    df_clean = node_data.dropna()
    N_unique = node_data.nunique()
    N_duplicated = node_data.duplicated().sum()
    N_rows = node_data.shape[0]
    N_columns = node_data.shape[1]
    columns = node_data.columns
    st.title("Node Data Description:")
    st.write(f"  - Number of NaN values: {Number_of_nan}")
    st.write(f"  - Number of unique values in each column: {N_rows}")
    st.write(f"  - Number of duplicated rows: {N_duplicated}")
    st.write(f"  - Number of columns: {N_columns}")
    st.write(f"  - Columns: {columns}")
    st.write(f"  - Data (first 5 rows):")
    st.dataframe(node_data.head(5))

def generate_edge_data(node_data, f_edges:float = 0.1):
    # Check if there are enough nodes to create the requested number of edges
    num_nodes = len(node_data)
    n_edges = int(f_edges*(num_nodes-1))
    # Generate random pairs of nodes
    
    edges = []
    for i in range(num_nodes):
        for j in np.random.choice(node_data['ID'], n_edges, replace=False):
            node_i = node_data['ID'][i]
            if node_i != j:
                edges.append([node_i, j])
            else:
                pass

    # Optionally, add random weights or other features to the edges
    weights = np.random.uniform(1, 10, size=(len(edges), 1))  # Random weights between 1 and 10

    # Create a DataFrame
    edge_data = pd.DataFrame(edges, columns=['Source', 'Target'])
    edge_data['Weight'] = np.round(weights, 2)
    return edge_data

def describe_edge_data(edge_data:pd.DataFrame):
    Number_of_nan = edge_data.isnull().sum().sum()
    df_clean = edge_data.dropna()
    N_unique = edge_data.nunique()
    N_duplicated = edge_data.duplicated().sum()
    N_rows = edge_data.shape[0]
    N_columns = edge_data.shape[1]
    columns = edge_data.columns
    st.title("Edge Data Description:")
    st.write(f"  - Number of NaN values: {Number_of_nan}")
    st.write(f"  - Number of unique values in each column: {N_rows}")
    st.write(f"  - Number of duplicated rows: {N_duplicated}")
    st.write(f"  - Number of columns: {N_columns}")
    st.write(f"  - Columns: {columns}")
    st.write(f"  - Data  (first 5 rows):")
    st.dataframe(edge_data.head(5))