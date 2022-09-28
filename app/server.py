import os
from flask import Flask, request, jsonify
import json
import pandas as pd

import gabby_data

app = Flask(__name__, static_folder='static_frontend', static_url_path='')

@app.route('/')
def landing_page():
    return app.send_static_file('index.html')
    
@app.route('/app')
def launch_app():
    return app.send_static_file('app.html')

@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    print('subscribe')
    if request.method == 'POST':
        status = gabby_data.add_subscriber(request.form['email'], request.form['signup_date'])
    return status
        
@app.route('/getAttributes', methods=['POST'])
def get_attributes():
    print('get_attributes')
    
    args = request.get_json()  
    
    attributes = gabby_data.get_attributes_list()
    return attributes.to_json(orient='records')
   
@app.route('/getProducts', methods=['POST'])
def get_products():
    print('get_products')
    
    args = request.get_json()
    if 'attributes' not in args:
        print("Error - no attributes in request")
        return json.dumps({"success": False, "message": "no attributes in request"})
        
    products = gabby_data.get_products_for_attributes(args['attributes'])
    return products.to_json(orient='records')

if __name__ == '__main__':
    app.run(threaded=True, port=5000)
