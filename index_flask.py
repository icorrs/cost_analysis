#index flask 
#coding=utf-8

import re
import os 
import json

import pandas as pd

from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request

import cost_analysis
import consts


app = Flask(__name__)
cache_file_list = os.listdir('/var/www/myweb/static/cachedata')
cache_file_path = '/var/www/myweb/static/cachedata'


@app.route('/')
def index_flask():
    return render_template('index_flask.html')


def use_cache(filename,level='json'):
    '''
    if filename exist in cache dir,read file and return jsonify, if not,
    use func to get frame,and write frame\'json to file before returning jsonnify
    '''
    def decorator(func):
        def wrapper():
            if filename in cache_file_list:
                f = open(os.path.join(cache_file_path,filename),'r')
                json1 = f.read()
                f.close()
            else:
                f = open(os.path.join(cache_file_path,filename),'w')
                frame1 = func()
                json1 = frame1.to_json(orient='records',force_ascii=False)
                f.write(json1)
                f.close()
            if level == 'json':
                return jsonify(json1)
            else:
                return pd.read_json(json1)
        wrapper.__name__ = func.__name__
        #see as https://stackoverflow.com/questions/17256602
        return wrapper
    return decorator


@app.route('/get_income_json')
@use_cache('%s_income.json'%(consts.DATE_DEFAULT))
def get_income():
    frame1 = cost_analysis.income_analysis(route='web')
    frame1 = frame1[frame1['finished_income']>0]
    frame1 = frame1[['income_boq_code','income_boq_name','income_boq_unit',
            'income_boq_price','income_boq_quantity','income_boq_total_price',
            'actural_quantity','finished_income']]
    return frame1


@use_cache('%s_income_detail.json'%(consts.DATE_DEFAULT),level='frame')
def get_income_detail():
    frame1 = cost_analysis.get_income_boq_detail()
    frame1 = frame1[['detail_wbs_code','detail_wbs_content',
            'detail_wbs_beginning_mileage','detail_wbs_ending_mileage',
            'detail_wbs_income_quantity','finished_income_quantity',
            'income_boq_code',]]
    return frame1


@app.route('/get_income_boq_detail_json/<income_boq_code>')
def get_income_boq_detail(income_boq_code):
    'get every income_boq_code\'s detail quantity'
    frame1 = get_income_detail()
    frame1 = frame1[frame1['income_boq_code'] == income_boq_code]
    frame1 = frame1[frame1['detail_wbs_income_quantity']>0]
    frame1 = (frame1[['detail_wbs_code','detail_wbs_content',
            'detail_wbs_beginning_mileage','detail_wbs_ending_mileage',
            'detail_wbs_income_quantity','finished_income_quantity']])
    json1 = frame1.to_json(orient='records',force_ascii=False)
    return jsonify(json1)  


@app.route('/get_sub_contractor_account_json')
@use_cache('sub_contractor_account.json',level='json')
def get_sub_contractor_account():
    frame1 = cost_analysis.get_sub_contractor_account()
    frame1 = frame1[frame1['sub_contractor_name'].notna()]
    return frame1


@app.route('/get_cal_and_payed_json')
@use_cache('cal_and_payed.json')
def get_cal_and_payed_json():
    frame1 = cost_analysis.get_cal_and_payed()
    return frame1



@use_cache('%s_materials_quantity.json'%(consts.DATE_DEFAULT),level='frame')
def get_materials_quantity():
    frame1 = cost_analysis.get_materials_quantity(route='web')
    return frame1


@app.route('/get_material_quantity_json/<material>')
def get_materiral_quantity(material):
    frame1 = get_materials_quantity()
    frame1 = frame1[['%s_kind'%(material),'%s_quantity'%(material),\
                 '%s_totalquantity'%(material),'sub_contractor_short_name']]
    frame1 = frame1[frame1['%s_totalquantity'%(material)]>0]
    frame1 = pd.pivot_table(frame1,index=['sub_contractor_short_name',\
                 '%s_kind'%(material)],aggfunc='sum')
    frame1 = frame1.reset_index()
    json1 = frame1.to_json(orient='records',force_ascii=False)
    return jsonify(json1)
        

@use_cache('%s_all_sub_contractor_income.json'%(consts.DATE_DEFAULT),level='frame')
def get_all_sub_contractor_income():
    'get all sub_contractor_income detail from cost_analysis module'
    frame1 = cost_analysis.get_sub_contractor_quantity()
    frame1 = frame1[['detail_wbs_code','detail_wbs_content',
            'detail_wbs_beginning_mileage', 'detail_wbs_ending_mileage',
            'sub_contractor_short_name','sub_contract_boq_code',
            'total_sub_quantity','actural_sub_quantity']]
    return frame1


@app.route('/get_sub_contractor_income_json/<contractor_short_name>')
def get_sub_contractor_income(contractor_short_name):
    'get one sub_contractor\'s income'
    frame1 = get_all_sub_contractor_income()
    if contractor_short_name == '全部':
        pass
    else:
        frame1 = frame1[frame1['sub_contractor_short_name']==contractor_short_name]
    frame1 = frame1[['sub_contract_boq_code','total_sub_quantity','actural_sub_quantity']]
    frame1 = frame1.pivot_table(values=['total_sub_quantity','actural_sub_quantity'],
        index=['sub_contract_boq_code'],aggfunc='sum')
    frame2 = cost_analysis.get_sub_contract_boq()
    frame1 = pd.merge(frame1,frame2,on='sub_contract_boq_code',how='left')
    frame1['total_sub_income'] = (frame1['sub_contract_boq_price']*\
        frame1['total_sub_quantity'])
    frame1 = frame1[frame1['total_sub_income']>0]
    frame1['actural_sub_income'] = frame1['sub_contract_boq_price']*frame1['actural_sub_quantity']
    frame1 = frame1[['sub_contract_boq_code','sub_contract_boq_name',
        'sub_contract_boq_unit','sub_contract_boq_price',
        'total_sub_quantity','actural_sub_quantity',
        'total_sub_income','actural_sub_income']]
    json1 = frame1.to_json(orient='records',force_ascii=False)
    return jsonify(json1)


@app.route('/get_sub_contractor_income_detail_json/<contractor_short_name>/<contract_boq_code>')
def get_sub_contractor_income_detail(contractor_short_name,contract_boq_code):
    'get detail of single sub_contract_boq_code of one sub_contractor'
    frame1 = get_all_sub_contractor_income()
    frame1 = frame1[frame1['sub_contract_boq_code'] == contract_boq_code]
    if contractor_short_name != '全部':        
        frame1 = frame1[frame1['sub_contractor_short_name'] == contractor_short_name]
        frame1 = frame1[['detail_wbs_code','detail_wbs_content','detail_wbs_beginning_mileage',
            'detail_wbs_ending_mileage','total_sub_quantity','actural_sub_quantity']]       
    else:
        frame1 = frame1[['detail_wbs_code','detail_wbs_content','sub_contractor_short_name',
            'detail_wbs_beginning_mileage','detail_wbs_ending_mileage',
            'total_sub_quantity','actural_sub_quantity']]
    json1 = frame1.to_json(orient='records',force_ascii=False)
    return jsonify(json1)


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
