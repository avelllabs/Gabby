import pandas as pd
import numpy as np
import configparser
import db_utils

# Read config file and set up DB connection object
# Either GCP Cloud SQL from App Engine, or bundled SQLite, or public IP Postgres
config = configparser.ConfigParser()
config.read('db_config.ini')    

print(f'''WARNING: db_profile set to { config['database_config']['db_profile'] } in db_config.ini!''')

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
                                  

def add_subscriber(em, dt):
    print("subscribing " + em + " " + dt)
    conn.execute(text("INSERT INTO subscribers (email, signup_date) VALUES (:em,:dt)"),{"em":em,"dt":dt} )
    return {"status": "success"}
    
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


def get_attributes_list_v2(category):

    # basic checks
    category = category.lower()
    if category.endswith('s'):
        category = category[:-1]

    shortlisted_attributes_query = \
        f'''
        SELECT *
        FROM shortlisted_attributes
        WHERE category='{category}'
        '''

    n_qphrase_attrs=10
    if category in ['laptop', 'tv', 'monitor']:
        n_qphrase_attrs = 5
    
    shortlisted_attributes = pd.read_sql(shortlisted_attributes_query, conn)
    print(shortlisted_attributes.shape)
    sim_attrs_list = \
        shortlisted_attributes. \
            sort_values('neighbor_distances').sort_values('n_reviews', ascending=False). \
                groupby('qphrase'). \
                    head(n_qphrase_attrs). \
                        reset_index(drop=True)[['key_phrase_id', 'phrase', 'qphrase']].sort_values('qphrase')
    print(sim_attrs_list.shape)
    sim_attrs_list_deduped =  sim_attrs_list[['key_phrase_id', 'phrase']].drop_duplicates()
    return sim_attrs_list_deduped.sample(min(50, sim_attrs_list_deduped.shape[0]))


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
            WHERE LOWER(title) LIKE '%%inch%%' 
            AND LOWER(title) LIKE '%%monitor%%' 
        '''
    
    monitor_brands = pd.read_sql(monitor_brands_query, conn)

    attributes = pd.concat([positive_phrases, negative_phrases]).reset_index(drop=True)

    attributes_filtered = \
        filter_phrases_containing_brand_model_terms(
                drop_numeric_phrases(
                        is_alpha_numeric(attributes)
                ), 
                monitor_brands[monitor_brands['brand'].str.len() > 1]['brand'].tolist()
        );
    
    return attributes_filtered[['key_phrase_id', 'phrase']].sample(50)


def get_reviews_for_attributes_asin_sentiment_v2(category, query_attributes, asin, sentiment=None):

    phrase_ids_query = \
    f'''SELECT key_phrase_id, phrase 
        FROM key_phrase_root 
        WHERE phrase IN ('{"','".join(query_attributes)}')
        AND category='{category}'
    '''
    query_phrases = pd.read_sql(phrase_ids_query, conn)

    review_results_query = \
    f'''SELECT key_phrase_id, review_id 
        FROM key_phrase_reviews 
        WHERE key_phrase_id IN 
        (SELECT key_phrase_id 
            FROM key_phrase_root 
            WHERE phrase IN ('{"','".join(query_attributes)}')
            AND category='{category}'
        )
    '''
    review_ids_for_query = pd.read_sql(review_results_query, conn)
    review_ids_for_query = review_ids_for_query.merge(query_phrases, on='key_phrase_id', how='left')
    review_ids_for_query = review_ids_for_query.groupby('review_id')['phrase'].apply(list).reset_index()
    review_ids_for_query['n_matches'] = review_ids_for_query['phrase'].apply(len)
    #top_matched_reviews = review_ids_for_query.sort_values('n_matches', ascending=False).head(10)

    
    # TODO: we may decided to build a version of this function with an optional asin (first iteration)
    
    fetch_matched_reviews_query = \
    f'''SELECT *
        FROM baseline_reviews
        WHERE review_id IN (
                {','.join(review_ids_for_query['review_id'].astype(str).tolist())}
            ) AND
            asin='{asin}'
    '''
    matched_reviews = pd.read_sql(fetch_matched_reviews_query, conn)
    matched_reviews = matched_reviews.merge(review_ids_for_query, on='review_id', how='left')

    if sentiment:
        matched_reviews = matched_reviews[matched_reviews['sentiment'] == sentiment]

    return matched_reviews


def get_reviews_for_attributes_and_asin(query_attributes, asin, sentiment=None):
    """
    Returns reviews for selected attributes, for a specific asin, for an optionally specified sentiment

    Parameters
    ----------
    query_attributes : array_like
        attributes provided
    asin : string
        asin or product unique identifier
    sentiment : string
        either 'positive' or 'negative'. default = None

    Returns
    -------
    dataframe
        a dataframe of matched reviews that satisfy constraints as specified by the function parameters

    Raises
    ------
    
    """


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
    #top_matched_reviews = review_ids_for_query.sort_values('n_matches', ascending=False).head(10)

    
    # TODO: we may decided to build a version of this function with an optional asin (first iteration)
    
    fetch_matched_reviews_query = \
    f'''SELECT *
        FROM baseline_reviews
        WHERE review_id IN (
                {','.join(review_ids_for_query['review_id'].astype(str).tolist())}
            ) AND
            asin='{asin}'
    '''
    matched_reviews = pd.read_sql(fetch_matched_reviews_query, conn)
    matched_reviews = matched_reviews.merge(review_ids_for_query, on='review_id', how='left')

    if sentiment:
        matched_reviews = matched_reviews[matched_reviews['sentiment'] == sentiment]

    return matched_reviews

    
def gen_attribute_sentiment_query(attribute_list, sentiment):
    return f""" SELECT BR.asin, PHR.key_phrase_id, PHR.phrase, BR.sentiment, count(*) as count
                FROM (SELECT key_phrase_id, phrase
                    FROM key_phrase_root 
                    WHERE category='Monitor' 
                        AND phrase IN ('{"', '".join(attribute_list)}') 
                    ) as PHR
                LEFT JOIN key_phrase_reviews KPR
                    ON KPR.key_phrase_id=PHR.key_phrase_id
                LEFT JOIN baseline_reviews BR
                    ON BR.review_id=KPR.review_id
                WHERE BR.sentiment='{sentiment}'
                GROUP BY BR.asin, PHR.key_phrase_id, PHR.phrase, BR.sentiment
            """

def get_products_for_attributes(attribute_list):
    
    # Generate query for pos and neg attribute counts
    
    attributes_counts_positive_sql_query = gen_attribute_sentiment_query(attribute_list, 'positive')
    attributes_counts_negative_sql_query = gen_attribute_sentiment_query(attribute_list, 'negative')
    
    positive_attributes_counts = pd.read_sql(attributes_counts_positive_sql_query, conn)
    negative_attributes_counts = pd.read_sql(attributes_counts_negative_sql_query, conn)
    
    attributes_counts = pd.concat([positive_attributes_counts, negative_attributes_counts])
    
    # Calculate distribution of attributes for products incrporating positive and negative occurrences
    
    product_attribute_counts = pd.pivot_table( 
                            attributes_counts.groupby(['asin', 'phrase'])['count'].sum().reset_index(),
                            values='count',
                            index='asin',
                            columns='phrase',
                            aggfunc=sum
                        ).fillna(0).reset_index()
    
    product_attribute_counts['total_reviews_in_context'] = product_attribute_counts[product_attribute_counts.columns[1:]].sum(axis=1)
    
    for phrase in product_attribute_counts.columns[1:-1]:
        product_attribute_counts[f"{phrase}_pbry"] = product_attribute_counts[phrase]/product_attribute_counts['total']
    
    
    pos_counts = positive_attributes_counts[['asin', 'phrase', 'count']]. \
            pivot_table(values='count', index='asin', columns='phrase', aggfunc=sum). \
                fillna(0). \
                    reset_index()
    pos_counts = pos_counts.rename(columns={c:f"{c}_pos" for c in pos_counts.columns[1:]})

    neg_counts = negative_attributes_counts[['asin', 'phrase', 'count']]. \
            pivot_table(values='count', index='asin', columns='phrase', aggfunc=sum). \
                fillna(0). \
                    reset_index()
    neg_counts = neg_counts.rename(columns={c:f"{c}_neg" for c in neg_counts.columns[1:]})

    prod_attr_prby = product_attribute_counts.merge(pos_counts, on='asin', how='left').merge(neg_counts, on='asin', how='left').fillna(0)
    
    for phrase in [c for c in prod_attr_prby.columns if c.endswith('pos') or c.endswith('neg')]:
        prod_attr_prby[f"{phrase}_pbry"] = prod_attr_prby[phrase]/prod_attr_prby['total']
    
    # Ranking function
    
    prod_attr_prby['total_perc_rank'] = prod_attr_prby['total'].rank(pct=True)
    prod_attr_prby_means = prod_attr_prby.mean().to_frame().reset_index().rename(columns={0:'mean'})
    
    for phrase in positive_attributes_counts['phrase'].unique():
        prod_attr_prby[f"{phrase}_score_level"] = prod_attr_prby[f"{phrase}_pos_pbry"]/prod_attr_prby[f"{phrase}_pbry"]
        prod_attr_prby = prod_attr_prby.fillna(0.5)

    prod_attr_prby['total_indicator_prby'] = (prod_attr_prby[[c for c in positive_attributes_counts['phrase'].unique()]] > 0).mean(axis=1)
    
    prod_attr_prby['score'] = prod_attr_prby[[c for c in prod_attr_prby.columns if c.endswith('score_level')]].mean(axis=1) * prod_attr_prby['total_perc_rank'] * prod_attr_prby['total_indicator_prby']
    
    top10_products = prod_attr_prby.sort_values('score', ascending=False).head(10)
    num_prods = prod_attr_prby.shape[0]
    
    fetch_matched_products_query = \
        f'''SELECT bp.*, br.num_reviews
            FROM (
                SELECT asin, count(*) as num_reviews
                FROM baseline_reviews
                WHERE asin IN ('{"','".join(top10_products['asin'].astype(str).tolist())}')
                GROUP BY asin
            ) br
            JOIN baseline_products bp
            ON bp.asin=br.asin
        '''
    matched_products = pd.read_sql(fetch_matched_products_query, conn)
    recommended_list = matched_products.merge(top10_products[['asin', 'score', 'total_perc_rank'] + \
                        [c for c in top10_products.columns if c.endswith('_score_level')]]).sort_values('score', ascending=False)
    
    return recommended_list, num_prods
    
    
def _gen_attribute_sentiment_query_v2(category, attribute_list, sentiment):
    return \
        f""" SELECT BR.asin, PHR.key_phrase_id, PHR.phrase, BR.sentiment, count(*) as count
            FROM (SELECT key_phrase_id, phrase
                FROM key_phrase_root 
                WHERE category='{category}' 
                    AND phrase IN ('{"', '".join(attribute_list)}') 
                ) as PHR
            LEFT JOIN key_phrase_reviews KPR
                ON KPR.key_phrase_id=PHR.key_phrase_id
            LEFT JOIN baseline_reviews BR
                ON BR.review_id=KPR.review_id
            WHERE BR.sentiment='{sentiment}'
            GROUP BY BR.asin, PHR.key_phrase_id, PHR.phrase, BR.sentiment
        """


def get_products_for_attributes_v2(category, attribute_list):
    
    # pos and neg counts
    attributes_counts_positive_sql_query = \
        _gen_attribute_sentiment_query_v2(category, attribute_list, 'positive')
    attributes_counts_negative_sql_query = \
        _gen_attribute_sentiment_query_v2(category, attribute_list, 'negative')
    positive_attributes_counts = pd.read_sql(attributes_counts_positive_sql_query, conn)
    negative_attributes_counts = pd.read_sql(attributes_counts_negative_sql_query, conn)
    
    attributes_counts = pd.concat([positive_attributes_counts, negative_attributes_counts])
    
    # product attribute counts
    product_attribute_counts = pd.pivot_table( 
                            attributes_counts.groupby(['asin', 'phrase'])['count'].sum().reset_index(),
                            values='count',
                            index='asin',
                            columns='phrase',
                            aggfunc=sum
                        ).fillna(0).reset_index()
    product_attribute_counts = product_attribute_counts.rename(columns={ 
                    c:f"{'_'.join(c.split())}_num_reviews" for c in product_attribute_counts.columns[1:]
                })
    product_attribute_counts['total'] = product_attribute_counts[product_attribute_counts.columns[1:]].sum(axis=1)
    for phrase in product_attribute_counts.columns[1:-1]:
        for phrase in product_attribute_counts.columns[1:-1]:
            product_attribute_counts[f"{phrase}_pbry"] = \
                product_attribute_counts[phrase]/product_attribute_counts['total_reviews_in_context']
    
    # within product pos and neg counts
    pos_counts = positive_attributes_counts[['asin', 'phrase', 'count']]. \
            pivot_table(values='count', index='asin', columns='phrase', aggfunc=sum). \
                fillna(0). \
                    reset_index()
    pos_counts = pos_counts.rename(columns={c:f"{'_'.join(c.split())}_pos" for c in pos_counts.columns[1:]})

    neg_counts = negative_attributes_counts[['asin', 'phrase', 'count']]. \
            pivot_table(values='count', index='asin', columns='phrase', aggfunc=sum). \
                fillna(0). \
                    reset_index()
    neg_counts = neg_counts.rename(columns={c:f"{'_'.join(c.split())}_neg" for c in neg_counts.columns[1:]})

    # setting up probability table
    prod_attr_prby = product_attribute_counts. \
                        merge(pos_counts, on='asin', how='left'). \
                            merge(neg_counts, on='asin', how='left').fillna(0)
    
    for phrase in [c for c in prod_attr_prby.columns if c.endswith('pos') or c.endswith('neg')]:
        prod_attr_prby[f"{phrase}_pbry"] = \
            prod_attr_prby[phrase]/prod_attr_prby['total_reviews_in_context']

    # positive leaning factors
    for phrase in positive_attributes_counts['phrase'].unique():
        us_phrase = '_'.join(phrase.split()) 
        prod_attr_prby[f"{phrase}_score_level"] = prod_attr_prby[f"{us_phrase}_pos_pbry"]/prod_attr_prby[f"{us_phrase}_num_reviews_pbry"]
        prod_attr_prby = prod_attr_prby.fillna(0.5)


    # total attribute occurrence adjustment
    prod_attr_prby['total_perc_rank'] = prod_attr_prby['total_reviews_in_context'].rank(pct=True)

    # attribute hits indicators adjustment 
    prod_attr_prby['total_indicator_prby'] = \
        (prod_attr_prby[['_'.join(c.split()) + '_num_reviews' for c in positive_attributes_counts['phrase'].unique()]] > 0).mean(axis=1)
        
    # final score computation
    prod_attr_prby['score'] = \
        prod_attr_prby[[c for c in prod_attr_prby.columns if c.endswith('score_level')]].mean(axis=1) \
            * prod_attr_prby['total_perc_rank'] * prod_attr_prby['total_indicator_prby']
    num_prods = prod_attr_prby.shape[0]

    # top 10 selection
    top10_products = prod_attr_prby.sort_values('score', ascending=False).head(10)

    # get product details
    fetch_matched_products_query = \
        f'''SELECT bp.*, br.num_reviews
            FROM (
                SELECT asin, count(*) as num_reviews
                FROM baseline_reviews
                WHERE asin IN ('{"','".join(top10_products['asin'].astype(str).tolist())}')
                GROUP BY asin
            ) br
            JOIN baseline_products bp
            ON bp.asin=br.asin
        '''
    matched_products = pd.read_sql(fetch_matched_products_query, conn)
    recommended_list = matched_products.merge(top10_products).sort_values('score', ascending=False)
    
    return recommended_list, num_prods
    
    
    
    
    
    
    
    
