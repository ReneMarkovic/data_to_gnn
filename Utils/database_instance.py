import torch
import os
from torch_geometric.data import HeteroData
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from torch_geometric.utils import to_networkx
from tqdm.auto import tqdm
import streamlit as st
class Database:
    """
    A class representing a database.

    Attributes:
        tables (list): A list of tables in the database.
        table_connections (dict): A dictionary storing table connections.

    Methods:
        add_table: Add a table to the database.
        add_table_connections: Add table connections to the database.
        create_node_array: Create an array of node features.
        add_node_number_to_table: Add a node number to each table.
        create_edge_index: Create the edge index and edge attributes.
        create_graph: Create a PyTorch geometric data object representing the graph.
    """

    def __init__(self):
        self.tables = []
        self.table_connections = {}

    def add_table(self, table):
        """
        Add a table to the database.

        Args:
            table (Table): The table to be added.
        """
        self.tables.append(table)

    def add_table_connections(self, table, foreign_table, foreign_key_col):
        """
        Add table connections to the database.

        Args:
            table (Table): The table to connect.
            foreign_table (Table): The foreign table to connect.
            foreign_key_col (str): The foreign key column name.
        """
        if table in self.table_connections:
            self.table_connections[table].append((foreign_table, foreign_key_col))
        else:
            self.table_connections[table] = [(foreign_table, foreign_key_col)]

    def one_hot_encode_nonnumerical_cols(self, df):
        col_groups = df.columns.to_series().groupby(df.dtypes).groups        
        try:
            non_numeric_cols = col_groups[np.dtype('O')]
            for col in non_numeric_cols:
                encoded_df = pd.get_dummies(df[col], prefix=str(col), dtype=int)
                df = pd.concat([df, encoded_df], axis=1).drop(str(col), axis=1)
        except KeyError:
            pass
        return df
    
    def create_node_array(self):
        """
        Create an array of node features.

        Returns:
            HeteroData: The node features.
        """
        data = HeteroData()
        for table in self.tables:
            oh_table = self.one_hot_encode_nonnumerical_cols(table.df)
            node_features = []
            for row in oh_table.to_numpy():
                node_features.append(row)
                
            data[table.name].x = node_features
        
        return data
    
    def add_node_number_to_table(self):
        """
        Add a node number to each table.
        """
        node_counter = 0
        for table in self.tables:
            table.df['node_nr'] = pd.RangeIndex(start=node_counter + 1, stop=node_counter + len(table.df) + 1)
            node_counter += len(table.df)

    def create_edge_index(self, graph):
        """
        Create the edge index and edge attributes.

        Args:
            graph (HeteroData): The graph data.

        Returns:
            HeteroData: The graph data with edge index and attributes.
        """
        
        #TODO: Verjetno je narobe indexing - moralo bi biti pkey-pkey v edge_indexu, brez reindexinga.
        
        for table in self.tables:
            if table in self.table_connections.keys():
                for connection in self.table_connections[table]:
                    foreign_table, foreign_key_col = connection
                    edge_index_transpose = []
                    for row_nr in range(len(table.df)):
                        for row_nr2 in range(len(foreign_table.df)):
                            if table.df[table.pkey_col][row_nr] == foreign_table.df[foreign_key_col][row_nr2]:
                                edge_index_transpose.append([table.df[table.pkey_col][row_nr], foreign_table.df[foreign_table.pkey_col][row_nr2]])
                                edge_index = [[edge_index_transpose[j][i] for j in range(len(edge_index_transpose))] for i in range(len(edge_index_transpose[0]))]
                                edge_index = torch.stack([torch.tensor(edge_index[0]), torch.tensor(edge_index[1])])
                    
                    graph[table.name, foreign_table.name].edge_index = edge_index
        return graph

    def create_graph(self):
        """
        Create a PyTorch geometric data object representing the graph.

        Returns:
            HeteroData: The graph data object.
        """
        node_features = self.create_node_array()
        
        self.add_node_number_to_table()
        
        data = self.create_edge_index(node_features)
        data.num_nodes_dict = {table.name: len(table.df) for table in self.tables}
        return data
    
    def draw_G(self,Graph,label=None):
        graph_hom = Graph.to_homogeneous()
        colors = np.array(graph_hom.node_type)
        G = to_networkx(graph_hom)
        colors = []
        for node in G.nodes():
            if node<10000:
                colors.append("cyan")
            else:
                colors.append("green")
            G.nodes[node]['label'] = node
        plt.figure(figsize=(12,12))
        plt.axis('off')
        if label==None:
            label = []
        nx.draw_networkx(G,
                        pos=nx.spring_layout(G, seed=0, k=0.1, iterations=50),
                        with_labels=True,
                        node_size=800,
                        node_color = colors,
                        cmap="hsv",
                        vmin=-2,
                        vmax=3,
                        width=0.8,
                        edge_color="grey",
                        font_size=14
                        )
        plt.tight_layout()
        st.pyplot(plt)
        filepath = os.path.join("img","graph.png")
        plt.savefig(filepath)