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

def edge_data(node_data_choice:str):
    if 'node_data' in st.session_state:
        st.write("")
        st.write("-----------------------------------------------------------------")
        st.write("")
        st.header(" Step 2: Data Relationship")
        if node_data_choice == 'Generate NODE Data':
            with st.expander("Generate Edge Table"):
                edge_data = generate_edge_data(st.session_state['node_data'], f_edges = 0.1)
                describe_edge_data(edge_data)
                # Convert DataFrame to CSV for downloading
                csv = convert_df_to_csv(edge_data)
                # Create a download button and provide the CSV file to download
                st.download_button(
                    label="Download Edge Data as CSV",
                    data=csv,
                    file_name='edge_data.csv',
                    mime='text/csv',
                )
                st.session_state['edge_data'] = edge_data
                check_2 = True
        else: 
            with st.expander("Add table connections"):
                st.write("Establish connectoin between tables:")
                
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
                        
                        
        # Button to finalize and generate the database
        if st.button('Continue to Step 3: Generate Database'):
            return True
    
    