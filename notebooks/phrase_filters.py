"""
This module helps to filter phrases based on
- presence of stopwords
- presence of brand names and model numbers
"""
import re
import pandas as pd
import spacy
nlp = spacy.load('en_core_web_sm')

spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS

def is_alpha_numeric(doc):
    """
    checking if every token in the doc is not a string of punctuations
    """
    if all([t.isalnum() for t in doc.split()]):
        return True
    return False

def contains_stopword(phrase):
    """
    Returns True if any phrase is a stopword
    """
    if any([t in spacy_stopwords for t in phrase.split()]):
        return True
    return False

def contains_more_than_n_stopwords(phrase, n=1):
    """
    Returns True if number of stopwords exceed n
    """
    if sum([t in spacy_stopwords for t in phrase.split()]) > n:
        return True
    return False


def filter_phrases_containing_punctuation(df):
    return df[df['phrase'].apply(lambda p: is_alpha_numeric(p))]

def filter_phrases_containing_stopwords(df):
    return df[df['phrase'].apply(lambda p: not contains_stopword(p))]

def filter_phrases_containing_more_than_n_stopwords(df, n=1):
    return df[df['phrase'].apply(lambda p: not contains_more_than_n_stopwords(p))]

def filter_phrases_containing_brand_model_terms(df, brand_model_terms):
    pattern = '(' + '|'.join(brand_model_terms) + ')'
    return df[ ~df['phrase'].str.contains(pattern, case=False)]