"""
We extract key terms and phrases using various algorithms in this module
"""

import pandas as pd
from tqdm.notebook import tqdm
tqdm.pandas()

import nltk
from nltk import BigramCollocationFinder, TrigramCollocationFinder
from nltk.collocations import BigramAssocMeasures, TrigramAssocMeasures

import spacy
nlp = spacy.load('en_core_web_sm')

import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

import textacy
from textacy.extract import keyterms

from collections import Counter


def featurization(df):
    df['contents'] = df['title'] + '. ' + df['review']
    df['review_tokens'] = df['contents'].apply(lambda x: [t.text.lower() for t in nlp(x)])
    return df


def keyterm_extraction_mutual_information(df):
    """
    Gets bigram and trigram phrases with mi_like scoring
    """
    corpus = df['review_tokens'].sum()

    bigram_measures = BigramAssocMeasures()
    bigrams = BigramCollocationFinder.from_words(corpus)
    scored_bigrams = bigrams.score_ngrams(bigram_measures.mi_like)

    trigram_measures = TrigramAssocMeasures()
    trigrams = TrigramCollocationFinder.from_words(corpus)
    scored_trigrams = trigrams.score_ngrams(trigram_measures.mi_like)

    ngram_df = pd.DataFrame({
        'phrase': [' '.join(p) for p, score in (scored_bigrams + scored_trigrams)],
        'score': [score for p, score in (scored_bigrams + scored_trigrams)]
    })
    return ngram_df


def keyterm_extraction_tfidf(df):
    """
    Gets bigram and trigram phrases with tfidf scoring
    """
    tfidf_vect = TfidfVectorizer(ngram_range=(2,3), preprocessor=lambda x: ' '.join(x), lowercase=False)
    Xtfidf = tfidf_vect.fit_transform(df['review_tokens'].tolist())
    ngram_idf = dict([(word, tfidf_vect.idf_[index]) for word, index in tfidf_vect.vocabulary_.items() ])
    ngram_idf_df = pd.DataFrame({
        'phrase': list(ngram_idf.keys()),
        'score': list(ngram_idf.values())
    })
    return ngram_idf_df

    
def keyterm_extraction_frequency(df):
    """
    Gets bigram and trigram phrases with 'frequency of occurence' scoring
    """
    count_vect = CountVectorizer(ngram_range=(2,3), preprocessor=lambda x: ' '.join(x), lowercase=False)
    Xcount = count_vect.fit_transform(df['review_tokens'].tolist())
    word_counts = Xcount.sum(axis=0)
    ngram_freq = dict([(word, word_counts[0, index]) for word, index in count_vect.vocabulary_.items() ])
    ngram_freq_df = pd.DataFrame({
        'phrase': list(ngram_freq.keys()),
        'score': list(ngram_freq.values())
    })
    return ngram_freq_df


def _construct_textacy_document(df):
    massive_doc = ' \n\n '.join(df['contents'].tolist() )
    print(f"massive doc length = ", len(massive_doc))
    massive_spacy_doc = nlp(massive_doc)
    return massive_spacy_doc


def keyterm_extraction_textrank(df, topk=1000):
    """
    Returns top 1000 keyterms/keyphrases using the TextRank algorithm
    """
    massive_spacy_doc = _construct_textacy_document(df)

    textrank_df = pd.DataFrame.from_dict(
        dict(keyterms.textrank(massive_spacy_doc, normalize='lemma', topn=topk)),
        orient='index').reset_index().rename(
            columns={'index': 'phrase', 0:'score'}
        )
    return textrank_df


def keyterm_extraction_scake(df, topk=1000):
    """
    Returns top 1000 keyterms/keyphrases using the sCake algorithm
    """
    massive_spacy_doc = _construct_textacy_document(df)

    scake_df = pd.DataFrame.from_dict(
        dict(keyterms.scake(massive_spacy_doc, normalize='lemma', topn=topk)),
        orient='index').reset_index().rename(columns={'index': 'phrase', 0:'score'}) 
                    
    return scake_df


def keyterm_extraction_yake(df, topk=1000):
    """
    Returns top 1000 keyterms/keyphrases using the Yake algorithm
    """
    massive_spacy_doc = _construct_textacy_document(df)

    yake_df = pd.DataFrame.from_dict(
        dict(keyterms.yake(massive_spacy_doc, normalize='lemma', topn=topk)),
        orient='index').reset_index().rename(columns={'index': 'phrase', 0:'score'}) 

    return yake_df


def keyterm_extraction_entities_and_noun_chunks(df):
    """
    Returns spacy entities and noun chunks as phrases along with occurrence frequency as score
    """
    spacy_docs = df['contents'].progress_apply(lambda review: nlp(review))
    all_noun_chunks = [e.text.lower() for sd in spacy_docs for sent in sd.sents for e in sent.noun_chunks]
    all_entities = [e.text.lower() for sd in spacy_docs for sent in sd.sents for e in sent.ents]

    spacy_counts = Counter(all_noun_chunks + all_entities)

    spacy_count_df = pd.DataFrame({
        'phrase': list(spacy_counts.keys()),
        'score': list(spacy_counts.values())
    })
    return spacy_count_df