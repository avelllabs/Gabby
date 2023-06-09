import os
from flask import Flask, request, jsonify

from flask_cors import CORS
import json
import pandas as pd


import gabby_data

app = Flask(__name__, static_folder='static_frontend', static_url_path='')
CORS(app)

# @app.route('/')
# def landing_page():
    # return app.send_static_file('index.html')
    
# @app.route('/app')
# def launch_app():
    # return app.send_static_file('app.html')

# @app.route('/subscribe', methods=['GET', 'POST'])
# def subscribe():
    # print('subscribe')
    # if request.method == 'POST':
        # status = gabby_data.add_subscriber(request.form['email'], request.form['signup_date'])
    # return status
        
@app.route('/getAttributes', methods=['POST'])
def get_attributes():
    print('get_attributes')
    
    args = request.get_json()  

    print('args',  args)

    attributes = gabby_data.get_attributes_list_v2(args['category'])
    return attributes.to_json(orient='records')


@app.route('/getProducts', methods=['POST'])
def get_products():
    print('get_products')
    
    args = request.get_json()
    if 'attributes' not in args:
        print("Error - no attributes in request")
        return json.dumps({"success": False, "message": "no attributes in request"})
        
    products_top10, num_prods = \
        gabby_data.get_products_for_attributes_v2(args['category'], args['attributes'])
    
    return {'num_prods':num_prods, 'top10': products_top10.to_json(orient='records')}
    #return products_top10.to_json(orient='records')


@app.route('/getReviews', methods=['POST'])
def get_reviews():
    print('get_reviews')
    
    args = request.get_json()  
    
    reviews = gabby_data.get_reviews_for_attributes_asin_sentiment_v2(args['category'],
                                                                args['attributes'], 
                                                                args['asin'], 
                                                                args['sentiment'] if 'sentiment' in args else None)
    return reviews.to_json(orient='records')



@app.route('/getCategories', methods=['GET'])
def get_categories():
    print('get_categories')

    return jsonify(['headphone', 'tv', 'monitor', 'mouse', 'laptop'])


if __name__ == '__main__':
    app.run(threaded=True, port=5000)



