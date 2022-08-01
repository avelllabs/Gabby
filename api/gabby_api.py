"""
Flask API for GetGabby baseline version
"""


import json

import gabby_data


from flask import Flask, jsonify, request



app = Flask(__name__)





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

    

@app.route('/')
def hello_flask():
    return "hello"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")