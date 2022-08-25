from flask import Flask, jsonify, request
from flask_restful import reqparse
import json

import gabby_data

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/')
def landing_page():
    return app.send_static_file('index.html')
    
@app.route('/app')
def launch_app():
    return app.send_static_file('app.html')
    
@app.route('/hello')
def hello():
    return 'Hello World!'
    
@app.route('/getAttributes')
def get_attributes():
    print('get_attributes')
    # request_data = request.get_json()
    # category = request_data['category']
    # TODO: attributes list: so that we can feed other/more attributes
    # attributes = request_data['framework']
    attributes = gabby_data.get_attributes_list()
    
    #TODO: to jsonify or not to ???
    return attributes[['key_phrase_id', 'phrase']].to_json(orient='records')

    # NOTE: sample return
    #return jsonify(sample_response_attributes)    

@app.route('/getProducts', methods=['POST'])
def get_products():
    print('get_products')
    
    args = request.get_json()
    print(args)

    if 'attributes' not in args or len(args['attributes']) == 0 \
        or 'liked_reviews' not in args:
        print('No attributes or liked_reviews provided to fetch products')
        return jsonify([])


    products = gabby_data.get_products_for_attributes_and_liked_reviews(args['attributes'], args['liked_reviews'])
    return products.to_json(orient='records')
    
    # NOTE: sample return
    #return jsonify(sample_response_products)

@app.route('/getReviews', methods=['POST'])
def get_reviews():
    print('get_reviews')
    
    args = request.get_json()
    print(args)

    if 'attributes' not in args or len(args['attributes']) == 0:
        print('No attributes provided to fetch reviews')
        return jsonify([])


    reviews = gabby_data.get_reviews_for_attributes(args['attributes'])
    return reviews.head().to_json(orient='records')
    

    # NOTE: sample return
    #response = jsonify(sample_response_reviews)
    #response.headers.add('Access-Control-Allow-Origin', '*')
    #return response

if __name__ == '__main__':
    app.run(threaded=True, port=5000)
