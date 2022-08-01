"""
Flask API for GetGabby baseline version
"""


import json

import gabby_data


from flask import Flask, jsonify, request
from flask_restful import reqparse



app = Flask(__name__)




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
    #return jsonify(gabby_data.sample_response_reviews)




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
    #return jsonify(gabby_data.sample_response_attributes)
    

@app.route('/')
def hello_flask():
    return "hello"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=True)