from .table_instance import Table
from .database_instance import Database
import streamlit as st

def generate_table_dataset(session_state):
    print()
    print("Adding tables to the database:")
    print(st.session_state['node_data_list'])
    print()
    for data in session_state['node_data_list']:
        print("working on:",data['name'], "table...")
        table = Table(data['name'], data['data'], pkey_col = data['pkey'])
        st.session_state[data['name']] = table

def generate_DB(session_state):
    print(f"Line1 {session_state['node_data_list']}")
    db = Database()
    generate_table_dataset(session_state)
    for table in st.session_state['node_data_list']:
        print(table["name"])
        db.add_table(st.session_state[table['name']])
        
    for relation in session_state['relations']:
        db.add_table_connections(session_state[relation['table1']], session_state[relation['table2']], relation['fkey'])
    return db