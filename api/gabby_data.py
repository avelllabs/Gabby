

from sqlalchemy import create_engine
import psycopg2 
import io
import pandas as pd
import numpy as np

conn_string = 'postgresql+psycopg2://gabbydbuser:gabbyDBpass@localhost:5432/gabbyDB'
db = create_engine(conn_string)
conn = db.connect()


def filter_phrases_containing_brand_model_terms(df, brand_model_terms):
    pattern = '(' + '|'.join(brand_model_terms) + ')'
    return df[ ~df['phrase'].str.match(pattern, case=False)]

def is_alpha_numeric(df):
    """
    checking if every token in the phrase is not a string of punctuations
    """
    alnums =  df['phrase'].apply(lambda p: all([t.isalnum() for t in p.split()]))
    return df[alnums]

def drop_numeric_phrases(df):
    """
    remove phrases that are just numbers
    """
    return df[~df['phrase'].apply(lambda p: len(p.split()) == 1 and p.isnumeric())]


def get_attributes_list(n_attributes=75):
    negative_attributes_query = \
    '''SELECT  P.key_phrase_id, P.phrase, S.n_positive, S.n_negative, S.reviewer_idf, S.n_reviews, S.n_reviewers
    FROM key_phrase_root P, 
    (SELECT * 
    FROM key_phrase_scores 
    WHERE  n_positive - n_negative < 0 
    ORDER BY n_negative DESC LIMIT 50) S
    WHERE P.key_phrase_id=S.key_phrase_id 
    ORDER BY n_reviewers DESC
    '''
    negative_phrases = pd.read_sql(negative_attributes_query, conn)

    positive_attributes_query = \
     '''SELECT  P.key_phrase_id, P.phrase, S.n_positive, S.n_negative, S.reviewer_idf, S.n_reviews, S.n_reviewers
    FROM key_phrase_root P, 
    (SELECT * 
    FROM key_phrase_scores 
    WHERE  n_positive - n_negative > 0 
    ORDER BY n_positive DESC LIMIT 50) S
    WHERE P.key_phrase_id=S.key_phrase_id 
    ORDER BY n_positive DESC
    '''
    positive_phrases = pd.read_sql(positive_attributes_query, conn)

    monitor_brands_query = \
    '''SELECT DISTINCT(brand)
        FROM baseline_products 
        WHERE title ILIKE '%%inch%%' 
        AND title ILIKE '%%monitor%%' 
    '''
    monitor_brands = pd.read_sql(monitor_brands_query, conn)

    attributes = pd.concat([positive_phrases, negative_phrases]).reset_index(drop=True)

    attributes_filtered = \
        filter_phrases_containing_brand_model_terms(
                drop_numeric_phrases(
                        is_alpha_numeric(attributes)
                ), 
                monitor_brands[monitor_brands['brand'].str.len() > 1]['brand'].tolist()
        )
    
    return attributes_filtered[['key_phrase_id', 'phrase']].sample(50)
