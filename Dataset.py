from torch.utils.data import Dataset, DataLoader
import pandas as pd
import torch
import json
from llama.llama import tokenizer as llama_tokenizer

tokenizer = llama_tokenizer("llama/tokenizer.model")



def load_corpus(path):
    json_list = []
    corpus_dict = {}
    with open(path, 'r') as json_file:
        for json_obj in json_file:
            json_dict = json.loads(json_obj)
            json_list.append(json_dict)
    for json_obj in json_list:
        corpus_dict[json_obj["_id"]] = json_obj["title"] + "\n" + json_obj["text"]
    return corpus_dict


def load_query(path):
    json_list = []
    query_dict = {}
    with open(path, 'r') as json_file:
        for json_obj in json_file:
            json_dict = json.loads(json_obj)
            json_list.append(json_dict)
    for json_obj in json_list:
        query_dict[json_obj["_id"]] = json_obj["text"]
    return query_dict


class ArxivDataset(Dataset):
    """Arxiv dataset."""

    def __init__(self, tsv_file, query_file, corpus_file):
        """
        Arguments:
            tsv_file (string): Path to the tsv training file.
            query_file: Path to query file
            corpus_file: Path to answers file
        """
        self.tsv = pd.read_csv(tsv_file,sep='\t')
        self.query = load_query(query_file)
        self.corpus = load_corpus(corpus_file)
        self.score = list(self.tsv["score"])

    def __len__(self):
        return len(self.self.tsv)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
        
        sample = {}
        sample["query"] = tokenizer.encode(self.query(self.tsv.loc[idx,"query-id"]))
        sample["corpus"] = tokenizer.encode(self.query(self.tsv.loc[idx,"corpus-id"]))

        return sample
    
