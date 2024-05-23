import os
import torch
from sklearn.preprocessing import LabelEncoder
from torch_geometric.data import Dataset, Data
import pandas as pd
import json
from torch_geometric.utils import to_networkx
import matplotlib.pyplot as plt
import networkx as nx

class Generate_Dataset(Dataset):
    def __init__(self, root, node_data, edge_data, node_roles, edge_roles, transform=None, pre_transform=None):
        # Initialize these first to avoid any issues during superclass initialization
        self.node_data = node_data
        self.edge_data = edge_data
        self.node_roles = node_roles
        self.edge_roles = edge_roles
        #print(self.node_roles)
        self._root = root  # Store root in a private attribute if needed for later use
        self.data_embedding = self.generate_embedding()
        # Ensure directory exists before calling superclass init which might process files
        processed_dir = os.path.join(root, 'processed')
        os.makedirs(processed_dir, exist_ok=True)

        # Now call the superclass constructor
        super(Generate_Dataset, self).__init__(root, transform, pre_transform)

        # After super init to avoid issues if processing is triggered

    def generate_embedding(self):
        """ Generate encoding for categorical variables in nodes and edges. """
        le = LabelEncoder()
        embeddings = {"nodes": {}, "edges": {}, "meta":{"nodes":{}, "edges":{}}}
        
        # Ensure the role 'ID' is handled properly if it's intended to be encoded
        print("Generating NODE embeddings...")
        info_b = self.node_data.dtypes.to_frame('dtypes').reset_index()
        info_b = info_b.set_index('index')["dtypes"].astype(str).to_dict()
        #print(info_b)
        
        col_id = None
        for col, role in self.node_roles.items():
            info_a = role
            #print("    -",col, role, info_a, info_b[col])
            embeddings["meta"]["nodes"][col] = [info_a, info_b[col]]
            #print("   -",col, role, self.node_data[col].nunique())
            
            temp = sorted(self.node_data[col].unique())
            temp = [str(i) for i in temp]
            mapped_temp = le.fit_transform(temp)
            mapped_temp = mapped_temp.tolist()
            mapped_temp = [str(i) for i in mapped_temp]
            embeddings["nodes"][col] = dict(zip(temp, mapped_temp))
            print("   -",col, role,embeddings["nodes"][col])
            if role == 'ID':
                col_id = col
        
        print("Generating EDGE embeddings...")
        info_b = self.edge_data.dtypes.to_frame('dtypes').reset_index()
        info_b = info_b.set_index('index')["dtypes"].astype(str).to_dict()
        
        for col, role in self.edge_roles.items():
            info_a = role
            #print("   -",col, role, role == 'ID', col_id)
            embeddings["meta"]["edges"][col] = [info_a, info_b[col]]
            if role in  ['Source ID', 'Target ID'] and col_id is not None:
                #print(col,embeddings["nodes"][col_id])
                embeddings["edges"][col]=embeddings["nodes"][col_id]
                #print(col,embeddings["edges"][col])
                #print(col_id, embeddings["edges"][col])
            else:
                temp = sorted(self.edge_data[col].unique())
                temp = [str(i) for i in temp]
                mapped_temp = le.fit_transform(temp)
                mapped_temp = [str(i) for i in mapped_temp]
                embeddings["edges"][col] = dict(zip(temp, mapped_temp))
        
        with open(os.path.join(self._root, 'embedding.json'), 'w') as f:
            json.dump(embeddings, f, indent=4)
        return embeddings

    def draw_G(sefl,G,labels):
        plt.figure(figsize=(12,12))
        plt.axis('off')
        nx.draw_networkx(G,
                        pos=nx.spring_layout(G, seed=0, k=0.5, iterations=50),
                        with_labels=True,
                        node_size=800,
                        node_color = labels,
                        cmap="hsv",
                        vmin=-2,
                        vmax=3,
                        width=0.8,
                        edge_color="grey",
                        font_size=14
                        )
        plt.tight_layout()
        plt.savefig("graph.png")
        
    def process(self):
        #print("Processing data...")
        #print("Node roles:", self.node_roles)
        #print("Edge roles:", self.edge_roles)
        edge_index = None
        edge_attr = None
        
        
        node_features = []
        for col, role in self.node_roles.items():
            temp = self.node_data[col]
            temp = temp.map(self.data_embedding["nodes"][col])
            
            if role == 'Features':
                node_features.append(temp)
            elif role == 'Label':
                labels = [int(self.data_embedding["nodes"][col][i]) for i in self.node_data[col].values]
        
        
        source = None
        target = None
        for col, role in self.edge_roles.items():
            if role == 'Source ID' and col=="Source":
                self.edge_data[col] = self.edge_data[col].astype(str)
                source = self.edge_data[col].map(self.data_embedding["edges"][col]).values
            elif role == 'Target ID' or col=="Target":
                self.edge_data[col] = self.edge_data[col].astype(str)
                target = self.edge_data[col].map(self.data_embedding["edges"][col]).values
        
        
        
        edge_index = [[int(i) for i in source],[int(i) for i in target]]
        edge_attr = []
        for col, role in self.edge_roles.items():
            if role == 'Features':
                edge_attr.append(self.edge_data[col].map(self.data_embedding["edges"][col]).values)
        
        node_features = torch.tensor(node_features).T
        N_nodes = node_features.shape[0]
        N_true = int(N_nodes*0.8)
        N_false = N_nodes - N_true
        print(f"Numer of nodes: {N_nodes}, N_true: {N_true}, N_false: {N_false}")
        print(edge_index)
        edge_index = torch.tensor(edge_index, dtype=torch.int64)
        #print(edge_attr)
        #edge_attr = torch.tensor(edge_attr).T if edge_attr else None
        labels = torch.tensor(labels, dtype=torch.long)
        train_mask = torch.tensor([True]*N_true + [False]*N_false)
        test_mask = torch.tensor([False]*N_true + [True]*N_false)
        
        
        # Save processed data
        print(f" - shape of node_features: {node_features.shape}")
        print(f" - shape of edge_index: {edge_index.shape}")
        #print(f" - shape of edge_attr: {edge_attr.shape if edge_attr is not None else None}")
        print(f" - shape of labels: {labels.shape}")
        
        data = Data(x=node_features, edge_index=edge_index,  y=labels)
        print("file saved to:",self.processed_dir)
        torch.save(data, os.path.join(self.processed_dir, 'data.pt'))
        torch.save(data, 'data.pt')
        print("file saved to:",self.processed_dir)
        G = to_networkx(data)
        self.draw_G(G,labels)
        return data

    # If you need to customize the processed_dir handling, override the property
    @property
    def processed_dir(self):
        return os.path.join(self._root, 'processed')

    @property
    def raw_file_names(self):
        return []

    @property
    def processed_file_names(self):
        return ['data.pt']

    def download(self):
        pass

    def __len__(self):
        return 1

    def __getitem__(self, idx):
        file_path = os.path.join(self.processed_dir, self.processed_file_names[idx])
        return torch.load(file_path)