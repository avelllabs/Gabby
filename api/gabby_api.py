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

    # NOTE: sample return
    #return jsonify([{"key_phrase_id":8968,"phrase":"30 days"},{"key_phrase_id":21,"phrase":"the speakers"},{"key_phrase_id":372,"phrase":"the base"},{"key_phrase_id":7152,"phrase":"a company"},{"key_phrase_id":819,"phrase":"monitor"},{"key_phrase_id":200,"phrase":"the brightness"},{"key_phrase_id":4953,"phrase":"the issues"},{"key_phrase_id":4223,"phrase":"the resolution"},{"key_phrase_id":4864,"phrase":"monitors"},{"key_phrase_id":9,"phrase":"the screen"},{"key_phrase_id":57,"phrase":"a monitor"},{"key_phrase_id":2444,"phrase":"great monitor"},{"key_phrase_id":3559,"phrase":"3 months"},{"key_phrase_id":12190,"phrase":"no avail"},{"key_phrase_id":109,"phrase":"gaming"},{"key_phrase_id":90,"phrase":"customer service"},{"key_phrase_id":2351,"phrase":"hdmi"},{"key_phrase_id":39,"phrase":"time"},{"key_phrase_id":7184,"phrase":"no way"},{"key_phrase_id":7338,"phrase":"2 weeks"},{"key_phrase_id":11869,"phrase":"no help"},{"key_phrase_id":18154,"phrase":"a dead pixel"},{"key_phrase_id":41,"phrase":"amazon"},{"key_phrase_id":18621,"phrase":"4k"},{"key_phrase_id":76,"phrase":"brightness"},{"key_phrase_id":8745,"phrase":"crap"},{"key_phrase_id":3,"phrase":"this monitor"},{"key_phrase_id":763,"phrase":"tech support"},{"key_phrase_id":880,"phrase":"speakers"},{"key_phrase_id":37,"phrase":"the quality"},{"key_phrase_id":4101,"phrase":"your time"},{"key_phrase_id":17270,"phrase":"144hz"},{"key_phrase_id":2122,"phrase":"games"},{"key_phrase_id":494,"phrase":"quality"},{"key_phrase_id":2383,"phrase":"the colors"},{"key_phrase_id":3258,"phrase":"this issue"},{"key_phrase_id":1029,"phrase":"this product"},{"key_phrase_id":2007,"phrase":"the box"},{"key_phrase_id":2841,"phrase":"junk"},{"key_phrase_id":450,"phrase":"replacement"},{"key_phrase_id":3660,"phrase":"work"},{"key_phrase_id":5524,"phrase":"garbage"},{"key_phrase_id":1697,"phrase":"your money"},{"key_phrase_id":12691,"phrase":"an hour"},{"key_phrase_id":2323,"phrase":"this problem"},{"key_phrase_id":735,"phrase":"return"},{"key_phrase_id":5506,"phrase":"two stars"},{"key_phrase_id":32248,"phrase":"these issues"},{"key_phrase_id":8067,"phrase":"arrival"},{"key_phrase_id":597,"phrase":"a lot"}])
    

@app.route('/')
def hello_flask():
    return "hello"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")