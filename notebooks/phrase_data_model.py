"""
The data structures and nearest neighbor models for deployment through the dash app
NOTE: the data was prepared using notebook `07`
"""

import pandas as pd

import spacy
nlp = spacy.load('en_core_web_sm')

import pickle

from sklearn.neighbors import NearestNeighbors
import numpy as np


#load data structs
algo_names = ['phrases_mi', 'phrases_tfidf', 'phrases_freq', 'phrases_yake', 'phrases_scake', 'phrases_trank', 'phrases_ent_nc']

keyterms = {}

def load_data_models():
    global algo_names
    global keyterms
    for algo in algo_names:
        keyterms[algo] = {}
        
        with open('data_structs/' + algo + '_phrase2idx.pkl', 'rb') as infile:
            keyterms[algo]['phrase2idx'] = pickle.load(infile)
            keyterms[algo]['idx2phrase'] = {v:k for k, v in keyterms[algo]['phrase2idx'].items()}
        
        with open('data_structs/' + algo + '_phrase2vector.pkl', 'rb') as infile:
            keyterms[algo]['phrase2vector'] = pickle.load(infile)

        keyterms[algo]['df'] = pd.read_pickle('data_structs/' + algo + '_df.pkl')
        
        keyterms[algo]['NN'] = NearestNeighbors(n_neighbors=5).fit(np.vstack(list(keyterms[algo]['phrase2vector'].values())))


def select_top_terms(topn=10):
    global algo_names
    global keyterms
    seed_terms = set()
    for algo in algo_names:
        _terms = keyterms[algo]['df'].head(topn)['phrase'].tolist()
        seed_terms.update(_terms)
    #print(len(seed_terms))
    return np.random.choice(list(seed_terms), topn, replace=False)


def get_close_terms(query, topn=10):
    global algo_names
    global keyterms
    qvec = nlp(query).vector.reshape(1, -1)
    close_terms = set()
    for algo in algo_names:
        dists, idxs = keyterms[algo]['NN'].kneighbors(qvec)
        _terms = [keyterms[algo]['idx2phrase'][i] for i in idxs.reshape(-1)]
        close_terms.update(_terms)
    #print(len(close_terms))
    return np.random.choice(list(close_terms), topn, replace=False)