import streamlit as st

def generate_dummy_node_data():
    st.write("Generate Dummy Node Data:")
    num_nodes = st.number_input("Enter the number of nodes:", min_value=1, value=11)
    num_features = st.number_input("Enter the number of features:", min_value=0, value=5)
    submit_button = st.form_submit_button(label='Generate Node Data')
    return [submit_button, num_nodes, num_features]