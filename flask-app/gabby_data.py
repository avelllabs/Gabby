import os
import io
from soupsieve import match
from collections import Counter
import pandas as pd
import numpy as np
from google.cloud.sql.connector import Connector, IPTypes
import pg8000
import sqlalchemy


def connect_unix_socket() -> sqlalchemy.engine.base.Engine:
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.
    db_user = os.environ["DB_USER"]  # e.g. 'my-database-user'
    db_pass = os.environ["DB_PASS"]  # e.g. 'my-database-password'
    db_name = os.environ["DB_NAME"]  # e.g. 'my-database'
    unix_socket_path = os.environ["INSTANCE_UNIX_SOCKET"]  # e.g. '/cloudsql/project:region:instance'

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # postgresql+pg8000://<db_user>:<db_pass>@/<db_name>
        #                         ?unix_sock=<INSTANCE_UNIX_SOCKET>/.s.PGSQL.5432
        # Note: Some drivers require the `unix_sock` query parameter to use a different key.
        # For example, 'psycopg2' uses the path set to `host` in order to connect successfully.
        sqlalchemy.engine.url.URL.create(
            drivername="postgresql+pg8000",
            username=db_user,
            password=db_pass,
            database=db_name,
            query={"unix_sock": "{}/.s.PGSQL.5432".format(unix_socket_path)},
        ),
        # [START_EXCLUDE]
        # Pool size is the maximum number of permanent connections to keep.
        pool_size=5,

        # Temporarily exceeds the set pool_size if no connections are available.
        max_overflow=2,

        # The total number of concurrent connections for your application will be
        # a total of pool_size and max_overflow.

        # 'pool_timeout' is the maximum number of seconds to wait when retrieving a
        # new connection from the pool. After the specified amount of time, an
        # exception will be thrown.
        pool_timeout=30,  # 30 seconds

        # 'pool_recycle' is the maximum number of seconds a connection can persist.
        # Connections that live longer than the specified amount of time will be
        # re-established
        pool_recycle=1800,  # 30 minutes
        # [END_EXCLUDE]
    )
    return pool

# connect_with_connector initializes a connection pool for a
# Cloud SQL instance of Postgres using the Cloud SQL Python Connector.
def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.

    instance_connection_name = os.environ["INSTANCE_CONNECTION_NAME"]  # e.g. 'project:region:instance'
    db_user = os.environ["DB_USER"]  # e.g. 'my-db-user'
    db_pass = os.environ["DB_PASS"]  # e.g. 'my-db-password'
    db_name = os.environ["DB_NAME"]  # e.g. 'my-database'

    ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

    # initialize Cloud SQL Python Connector object
    connector = Connector()

    def getconn() -> pg8000.dbapi.Connection:
        conn: pg8000.dbapi.Connection = connector.connect(
            instance_connection_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=ip_type,
        )
        return conn

    # The Cloud SQL Python Connector can be used with SQLAlchemy
    # using the 'creator' argument to 'create_engine'
    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
        # ...
    )
    return pool

'''
db_user = os.environ["CLOUD_SQL_USERNAME"]
db_pass = os.environ["CLOUD_SQL_PASSWORD"]
db_name = os.environ["CLOUD_SQL_DATABASE_NAME"]
db_connection_name = os.environ["CLOUD_SQL_CONNECTION_NAME"]

#db_user = 'gabbydbuser'
#db_pass = 'gabbyDBpass'
#db_name = 'gabbyDB'
#db_connection_name = 'gabby-f6171:us-central1:gabbydb'

unix_socket_path = '/cloudsql/{}'.format(db_connection_name)

db = sqlalchemy.create_engine(
        # Equivalent URL:
        # postgresql+pg8000://<db_user>:<db_pass>@/<db_name>
        #                         ?unix_sock=<INSTANCE_UNIX_SOCKET>/.s.PGSQL.5432
        # Note: Some drivers require the `unix_sock` query parameter to use a different key.
        # For example, 'psycopg2' uses the path set to `host` in order to connect successfully.
        sqlalchemy.engine.url.URL.create(
            drivername="postgresql+pg8000",
            username=db_user,
            password=db_pass,
            database=db_name,
            query={"unix_sock": "{}/.s.PGSQL.5432".format(unix_socket_path)},
        ),
        # ...
    )
'''

db = connect_with_connector()
#db = connect_unix_socket()

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


def get_attributes_list():
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


def get_reviews_for_attributes(query_attributes):
    phrase_ids_query = \
    f'''SELECT key_phrase_id, phrase 
        FROM key_phrase_root 
        WHERE phrase IN ('{"','".join(query_attributes)}')
    '''
    query_phrases = pd.read_sql(phrase_ids_query, conn)

    review_results_query = \
    f'''SELECT key_phrase_id, review_id 
        FROM key_phrase_reviews 
        WHERE key_phrase_id IN 
        (SELECT key_phrase_id 
        FROM key_phrase_root 
        WHERE phrase IN ('{"','".join(query_attributes)}'))
    '''
    review_ids_for_query = pd.read_sql(review_results_query, conn)
    review_ids_for_query = review_ids_for_query.merge(query_phrases, on='key_phrase_id', how='left')
    review_ids_for_query = review_ids_for_query.groupby('review_id')['phrase'].apply(list).reset_index()
    review_ids_for_query['n_matches'] = review_ids_for_query['phrase'].apply(len)
    top_matched_reviews = review_ids_for_query.sort_values('n_matches', ascending=False).head(25)

    fetch_matched_reviews_query = \
    f'''SELECT *
        FROM baseline_reviews
        WHERE review_id IN (
            {','.join(top_matched_reviews['review_id'].astype(str).tolist())}
        )
        
    '''
    matched_reviews = pd.read_sql(fetch_matched_reviews_query, conn)
    matched_reviews = matched_reviews.merge(top_matched_reviews, on='review_id')
    return matched_reviews



def get_products_for_attributes_and_liked_reviews(attributes, liked_reviews = []):
    # TODO: ignoring the liked reviews for now

    phrase_ids_query = \
    f'''SELECT key_phrase_id, phrase 
        FROM key_phrase_root 
        WHERE phrase IN ('{"','".join(attributes)}')
    '''
    query_phrases = pd.read_sql(phrase_ids_query, conn)

    review_results_query = \
    '''SELECT key_phrase_id, review_id 
        FROM key_phrase_reviews 
        WHERE key_phrase_id IN 
        (SELECT key_phrase_id 
        FROM key_phrase_root 
        WHERE phrase IN ('the price', 'the stand', '2 weeks', 'quality'))
    '''
    review_ids_for_query = pd.read_sql(review_results_query, conn)
    review_ids_for_query = review_ids_for_query.merge(query_phrases, on='key_phrase_id', how='left')
    review_ids_for_query = review_ids_for_query.groupby('review_id')['phrase'].apply(list).reset_index()
    review_ids_for_query['n_matches'] = review_ids_for_query['phrase'].apply(len)

    fetch_matched_reviews_query = \
    f'''SELECT *
        FROM baseline_reviews
        WHERE review_id IN (
            {','.join(review_ids_for_query['review_id'].astype(str).tolist())}
        )
        
    '''
    matched_reviews = pd.read_sql(fetch_matched_reviews_query, conn)
    matched_reviews = matched_reviews.merge(review_ids_for_query, on='review_id')

    product_ranking = matched_reviews.groupby(['asin']).agg({
        'n_matches': 'sum',
        'rating': 'mean',
        'verified': 'sum',
        'vote': 'sum',
        'review_id': 'count',
        'phrase': 'sum'
    }).sort_values(['n_matches', 'verified', 'rating', 'review_id', 'vote'], ascending=False).reset_index()
    product_ranking['phrase'] = product_ranking['phrase'].apply(lambda x: Counter(x))
    product_ranking = product_ranking.rename(columns={'review_id': 'n_reviews'})
    top10_products = product_ranking.head(10)
    fetch_matched_products_query = \
    f'''SELECT *
        FROM baseline_products
        WHERE asin IN ('{"','".join(top10_products['asin'].astype(str).tolist())}')
    '''
    matched_products = pd.read_sql(fetch_matched_products_query, conn)
    top10_products = top10_products.merge(matched_products[['asin', 'title', 'description', 'imageURLHighRes']], on='asin')
    return top10_products