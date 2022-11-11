"""
This module saves extracted key_phrases into database. 
This is necessary because we are assigning explicit key_phrase_ids and therefore we need to add rows to the db category-wise.
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

sys.path.append('../')

import db_utils

# Setting up database connections
config = configparser.ConfigParser()
config.read('../db_config.ini')  

conn = None

def set_up_database_connection(use_psycopg2=False):
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
                                    config[db_profile]['DB_NAME'],
                                    use_psycopg2)

    print(f'''WARNING: db_profile set to "{config['database_config']['db_profile']}" in db_config.ini!''')
    return conn


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
        conn = set_up_database_connection(use_psycopg2=True)
    
    # creating tmp dir
    tmp_dir = f"./tmp_dir_{args.category}"
    if not os.path.exists(tmp_dir):
        print(f"ERROR: could not find expected temp directory {tmp_dir}. Have your run attribute_extractor.py for {args.category}")
        sys.exit()

    # setting up key phrase dataframes
    save_files = sorted(glob.glob(os.path.join(tmp_dir, "*pkl")))
    key_phrases = pd.read_pickle(save_files[-1])
    print(f"attributes.shape = {key_phrases.shape}")

    key_phrases['category'] = args.category
    key_phrases['n_reviewers'] = key_phrases['reviewers'].apply(lambda r: len(r))
    key_phrases['n_reviews'] = key_phrases['reviews'].apply(lambda r: len(r))
    key_phrases['n_products'] = key_phrases['products'].apply(lambda r: len(r))

    if_exists_setting = 'append'
    if args.create_tables: 
        print("WARNING: Creating key_phrase tables fresh")
        if_exists_setting = 'replace'

    start_kpid = 0
    if if_exists_setting == 'append':
        rs = conn.execute("SELECT MAX(key_phrase_id) FROM key_phrase_root")
        start_kpid = int(rs.first()[0]) + 1
    print('start_kpid', start_kpid)

    key_phrases['key_phrase_id'] = [kid+start_kpid for kid in range(key_phrases.shape[0])]
    key_phrases = key_phrases.reset_index().rename(columns={'index': 'phrase'})[[ 
        'key_phrase_id', 'phrase', 'reviews', 'reviewers', 'products', 'n_positive', 'n_negative', 'n_reviewers', 'n_products', 'n_reviews', 'category'
    ]]
    print('Data frame ready', key_phrases.shape)

    key_phrase_root = key_phrases[['key_phrase_id', 'phrase', 'category']]
    key_phrase_root.to_sql('key_phrase_root', con=conn, method='multi',
                            index=False, if_exists=if_exists_setting)
    print('key phrase root in DB')  

    key_phrase_scores = key_phrases[['key_phrase_id', 'n_reviews', 'n_positive', 'n_negative', 'n_reviewers', 'n_products']]
    key_phrase_scores.to_sql('key_phrase_scores', con=conn, method='multi',
                            index=False, if_exists=if_exists_setting)
    print('key phrase scores in DB')

    key_phrase_reviews = key_phrases[['key_phrase_id', 'reviews']].explode('reviews').rename(columns={'reviews': 'review_id'})
    key_phrase_reviews.to_sql('key_phrase_reviews', con=conn, method='multi',
                            index=False, if_exists=if_exists_setting)
    print('key phrase reviews in DB')

    if conn:
        print('Closing database connection!')
        conn.close()
    # TODO:  db.dispose()
