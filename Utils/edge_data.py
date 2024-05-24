import streamlit as st
from .webui_datahandling import convert_df_to_csv, read_data, describe_node_data, generate_edge_data, describe_edge_data


def step_2_init():
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
        return edge_data_choice

def edge_data():
    if 'node_data' in st.session_state:
        st.write("")
        st.write("-----------------------------------------------------------------")
        st.write("")
        st.header("Step 2: Data Relationship")
        st.session_state['step 2 extended'] = True
        with st.expander("Add table connections",expanded = st.session_state['step 2 extended']):
            st.write("Establish connection between tables:")
            
            # Initialize relations in session state
            if 'relations' not in st.session_state:
                st.session_state['relations'] = []

            col1, col2, col3, col4 = st.columns(4)
            t1 = col1.selectbox("Select table 1", list(st.session_state['node_data'].keys()), key='t1')
            t2 = col2.selectbox("Select table 2", list(st.session_state['node_data'].keys()), key='t2')
            fkey_table = col3.selectbox("Select fkey table", [t1, t2], key='fkey_table')
            column_names = st.session_state['node_data'][fkey_table]['data'].columns
            fkey = col4.selectbox("Select fkey", column_names, key='fkey')
            
            if st.button('Add Relation'):
                relation = {
                    'table1': t1,
                    'table2': t2,
                    'fkey_table': fkey_table,
                    'fkey': fkey
                }
                st.session_state['relations'].append(relation)
                st.success('Relation added successfully!')

            # Display all added relations
            st.write("Current Relations:")
            for rel in st.session_state['relations']:
                st.write(f"Table 1: {rel['table1']}, Table 2: {rel['table2']}, Foreign Key Table: {rel['fkey_table']}, Foreign Key Column: {rel['fkey']}")
    
    if 'relations' in st.session_state:
        if st.button('Continue to Step 3: Generate Database'):
            st.session_state['step 2 extended'] = False
            return True
    return False