"""
Flask API for GetGabby baseline version
"""

from flask import Flask
app = Flask(__name__)

from collections import defaultdict

import phrase_data_model
phrase_data_model.load_data_models()



@app.route('/')
def hello_flask():
    return "hello"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")