#index flask 
#coding=utf-8

import re

import pandas as pd

from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request

import cost_analysis


app = Flask(__name__)

@app.route('/')
def index_flask():
    return render_template('index_flask.html')

@app.route('/get_income_boq_json')
def return_incomeboq():
    frame1 = cost_analysis.get_income_boq()
    json1 = frame1.to_json(orient='records',force_ascii=False)
    return jsonify(json1)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
