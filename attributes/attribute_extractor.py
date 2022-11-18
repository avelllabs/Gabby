"""
This module extracts attributes from reviews using the topic rank algorithm as implemented in notebook 12, 15
NOTE: this script expects that the database contains records for requisite product categories
"""
import argparse
import os
import sys
import shutil
import glob
import configparser
import pandas as pd
import numpy as np
import pke
import pickle
from tqdm import tqdm
tqdm.pandas()

sys.path.append('../app/')

import db_utils

# Setting up database connections
print("Loading config...")
config = configparser.ConfigParser()
config.read('../app/db_config.ini')  

conn = None

def set_up_database_connection():
    global conn
    if config['database_config']['db_profile'] == 'gcp_couldsql_internal':
        conn = db_utils.connect_with_connector(config['gcp_couldsql_internal']['DB_USER'],
                                    config['gcp_couldsql_internal']['DB_PASS'], 
                                    config['gcp_couldsql_internal']['INSTANCE_CONNECTION_NAME'], 
                                    config['gcp_couldsql_internal']['DB_NAME'])
    elif config['database_config']['db_profile'] == 'sqlite_bundled':
        conn = db_utils.connect_with_sqlite(config['sqlite_bundled']['DB_NAME'])
    else:
        db_profile = config['database_config']['db_profile']
        conn = db_utils.connect_with_conn_string(config[db_profile]['DB_USER'],
                                    config[db_profile]['DB_PASS'],
                                    config[db_profile]['HOSTNAME_PORT'],
                                    config[db_profile]['DB_NAME'])

    print(f'''WARNING: db_profile set to "{config['database_config']['db_profile']}" in db_config.ini!''')
    return conn


def get_category_pattern_strings(category):
    qprods = {
        'tv': ['TV', 'Television'], 
        'monitor': ['Monitor', 'inch'],
        'headphone': ['Headphone'], # , 'Headphones', 'Head phone', 'Head phones', 'head-phones', 'headset'],
        'mouse': ['Mouse'],
        'laptop': ['Laptop']
    }
    return qprods[category]


def gen_query_reviews_for_category(qpatterns, category):
    
    and_pattern = " AND ".join(f"""title ILIKE '%%{qkw}%%'""" for qkw in qpatterns)
    or_pattern = " OR ".join(f"""title ILIKE '%%{qkw}%%'""" for qkw in qpatterns)

    pattern = and_pattern
    if category in ['tv', 'headphone']:
        pattern = or_pattern

    sql = f'''
        SELECT BR.*
        FROM baseline_reviews BR,  
        (SELECT asin
        FROM baseline_products 
        WHERE {pattern}) AS BP 
        WHERE BR.asin = BP.asin; '''


    if category == 'headphone':
        sql = '''
            SELECT BR.*
            FROM baseline_reviews BR,  
            (SELECT asin
                FROM baseline_products 
                WHERE title ILIKE '%%headphones%%' 
                AND (price ~ '\$[1-9][0-9][0-9].*' 
                    OR price ~ '\$[5-9][0-9].*')) AS BP 
            WHERE BR.asin = BP.asin
        '''

    return sql


def _get_n_phrases_to_extract(text_len):
    n_kp = int(text_len/4.7/50.)
    return max(n_kp, 3)


def get_topic_rank_phrases(text):
    # initialize keyphrase extraction model, here TopicRank
    extractor = pke.unsupervised.TopicRank()

    # load text
    extractor.load_document(input=text, language='en')

    # keyphrase candidate selection, in the case of TopicRank: sequences of nouns
    # and adjectives (i.e. `(Noun|Adj)*`)
    extractor.candidate_selection()

    # candidate weighting, in the case of TopicRank: using a random walk algorithm
    extractor.candidate_weighting()

    # N-best selection, keyphrases contains the 10 highest scored candidates as
    # (keyphrase, score) tuples
    keyphrases = extractor.get_n_best(n=_get_n_phrases_to_extract(len(text)))
    return keyphrases


def _extract_phrases_and_metadata(review, key_phrase_data):

    for k, s in get_topic_rank_phrases(review['contents']):
        # insert into key_phrase_data
        if k not in key_phrase_data:
            key_phrase_data[k] = {
                'reviews': set(), #review ids
                'reviewers': set(),
                'products': set(), #product asins
                'n_positive': 0, #number of occurrences in positive reviews
                'n_negative': 0, #number of occurrences in negative review
                #'n_reviewers_positive': 0, #reviewers ids
                #'n_reviewers_negative': 0, #reviewers ids
            }
        key_phrase_data[k]['reviews'].add(review['review_id'])
        key_phrase_data[k]['reviewers'].add(review['reviewerID'])
        if review['sentiment'] == 'positive':
            key_phrase_data[k]['n_positive'] += 1
            #key_phrase_data[k]['n_reviewers_positive'] += 1
        else:
            key_phrase_data[k]['n_negative'] += 1
            #key_phrase_data[k]['n_reviewers_negative'] += 1
        key_phrase_data[k]['products'].add(review['asin'])     


def extract_key_phrases(category_reviews_df, tmp_dir, category):
    category_reviews_df['contents'] = (category_reviews_df['reviewTitle'] + '. ' + category_reviews_df['reviewText'])
    key_phrase_data = {}
    step = 1000
    print('expected temporary saves = ', category_reviews_df.shape[0]//step + 1)
    for i in tqdm(range(category_reviews_df.shape[0]//step + 1)):
        _from = i*step
        _to = i*step+step
        #print(_from, _to)
        subset = category_reviews_df.iloc[_from: _to]
        subset.progress_apply(lambda review: _extract_phrases_and_metadata(review, key_phrase_data), axis=1)
        subset_phrases = pd.DataFrame.from_dict(key_phrase_data, orient='index')
        subset_phrases.to_pickle(os.path.join(tmp_dir, f"cumulative_subset-{category}-{i:03}.pkl"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="")
    ap.add_argument('category', 
                        help="choose the category of products for which to compute keyterms",
                        choices=['monitor', 'laptop', 'tv', 'headphone', 'mouse'])
    ap.add_argument('--create_tables', 
                        help="flag to create key_phrase tables instead of append (default)" ,
                        action="store_true")
    # ap.add_argument('outfile', 
    #                     help='output file name')
    args = ap.parse_args()

    # setting up db connection
    if conn == None:
        print('Setting up db connection...')
        conn = set_up_database_connection()
    
    # creating tmp dir
    tmp_dir = f"./tmp_dir_{args.category}"
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.mkdir(tmp_dir)
    print(f"created temp directory {tmp_dir}")
    
    # setting up query to fetch reviews
    print('Fetching reviews...')
    qpatterns = get_category_pattern_strings(args.category)
    category_reviews_query = gen_query_reviews_for_category(qpatterns, args.category)
    print(category_reviews_query)

    # fetch the reviews for the category
    category_reviews_df = pd.read_sql(category_reviews_query, conn)    
    print(category_reviews_df.shape)

    # extracting key phrases
    extract_key_phrases(category_reviews_df, tmp_dir, args.category)
    print('Key phrases (attributes) extracted.')

    if conn:
        print('Closing database connection!')
        conn.close()
    # TODO:  db.dispose()
