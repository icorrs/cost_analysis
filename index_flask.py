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


@app.route('/')
def index_flask():
    return render_template('index_flask.html')


@app.route('/get_income_json')
def get_income():
    if '%s_income.json'%(consts.DATE_DEFAULT) in cache_file_list:
        f = open('/var/www/myweb/static/cachedata/%s_income.json'\
            %(consts.DATE_DEFAULT),'r')
        json1 = f.read()
    else:
        frame1 = cost_analysis.income_analysis(route='web')
        frame1 = frame1[frame1['income_boq_quantity']>0]
        json1 = frame1.to_json(orient='records',force_ascii=False)
        f = open('/var/www/myweb/static/cachedata/%s_income.json'\
            %(consts.DATE_DEFAULT),'w')
        f.write(json1)
    return jsonify(json1)

def get_income_detail():
    if  '%s_income_detail.json'%(consts.DATE_DEFAULT) in cache_file_list:
        f = open('/var/www/myweb/static/cachedata/%s_income_detail.json'
            %(consts.DATE_DEFAULT),'r')
        json1 = f.read()
        frame1 = pd.read_json(json1)
    else:
        frame1 = cost_analysis.get_income_boq_detail()
        frame1 = frame1[['detail_wbs_code','detail_wbs_content',
            'detail_wbs_beginning_mileage','detail_wbs_ending_mileage',
            'detail_wbs_income_quantity','finished_income_quantity',
            'income_boq_code',]]
        json1 = frame1.to_json(orient='records',force_ascii=False)
        f = open('/var/www/myweb/static/cachedata/%s_income_detail.json'
            %(consts.DATE_DEFAULT),'w')
        f.write(json1)
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
def get_sub_contractor_account():
    if 'sub_contractor_account.json' in cache_file_list:
        f = open('/var/www/myweb/static/cachedata/sub_contractor_account.json','r')
        json1 = f.read()
    else:
        frame1 = cost_analysis.get_sub_contractor_account()
        frame1 = frame1[frame1['sub_contractor_name'].notna()]
        json1 = frame1.to_json(orient='records',force_ascii=False)
        f = open('/var/www/myweb/static/cachedata/sub_contractor_account.json','w')
        f.write(json1)
    return jsonify(json1)

'''
@app.route('/get_translate_dic')
def get_translate_dic():
    if 'translate_dic.json' in cache_file_list:
        f = open('/var/www/myweb/static/cachedata/translate_dic.json','r')
        json1 = f.read()
    else:
        dic1 = cost_analysis.get_translate_dic()
        json1 = json.dumps(dic1,ensure_ascii=False,separators=(',',':'))
        f = open('/var/www/myweb/static/cachedata/translate_dic.json','w')
        f.write(json1)
    return jsonify(json1)
'''


@app.route('/get_cal_and_payed_json')
def get_cal_and_payed_json():
    if 'cal_and_payed.json' in cache_file_list:
        f = open('/var/www/myweb/static/cachedata/cal_and_payed.json','r')
        json1 = f.read()
    else:
        frame1 = cost_analysis.get_cal_and_payed()
        json1 = frame1.to_json(orient='records',force_ascii=False)
        f = open('/var/www/myweb/static/cachedata/cal_and_payed.json','w')
        f.write(json1)
    return jsonify(json1)


@app.route('/get_material_quantity_json/<material>')
def get_material_quantity(material):
    if '%s_material_quantity_%s.json'%(consts.DATE_DEFAULT,material) in cache_file_list:
        f = open('/var/www/myweb/static/cachedata/%s_material_quantity_%s.json'\
            %(consts.DATE_DEFAULT,material),'r')
        json1 = f.read()
    else:
        frame1 = cost_analysis.get_material_quantity(material)
        frame1 = frame1[['%s_kind'%(material),'%s_quantity'%(material),\
                 '%s_totalquantity'%(material),'sub_contractor_short_name']]
        frame1 = frame1[frame1['%s_totalquantity'%(material)]>0]
        frame1 = pd.pivot_table(frame1,index=['sub_contractor_short_name',\
                 '%s_kind'%(material)],aggfunc='sum')
        frame1 = frame1.reset_index()
        json1 = frame1.to_json(orient='records',force_ascii=False)
        f = open('/var/www/myweb/static/cachedata/%s_material_quantity_%s.json'\
            %(consts.DATE_DEFAULT,material),'w')
        f.write(json1)
    return jsonify(json1)
        

def get_all_sub_contractor_income():
    'get all sub_contractor_income detail from cost_analysis module'
    if '%s_all_sub_contractor_income.json'%(consts.DATE_DEFAULT) in cache_file_list:
        f = open('/var/www/myweb/static/cachedata/%s_all_sub_contractor_income.json'\
            %(consts.DATE_DEFAULT),'r')
        json1 = f.read()
        frame1 = pd.read_json(json1)
    else:
        frame1 = cost_analysis.get_sub_contractor_quantity()
        frame1 = frame1[['detail_wbs_code','detail_wbs_beginning_mileage',
            'detail_wbs_ending_mileage','sub_contractor_short_name',
            'sub_contract_boq_code','total_sub_quantity','actural_sub_quantity']]
        f = open('/var/www/myweb/static/cachedata/%s_all_sub_contractor_income.json'\
            %(consts.DATE_DEFAULT),'w')
        json1 = frame1.to_json(orient='records',force_ascii=False)
        f.write(json1)
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
        frame1 = frame1[['detail_wbs_code','detail_wbs_beginning_mileage',
            'detail_wbs_ending_mileage','total_sub_quantity','actural_sub_quantity']]       
    else:
        frame1 = frame1[['detail_wbs_code','sub_contractor_short_name',
            'detail_wbs_beginning_mileage','detail_wbs_ending_mileage',
            'total_sub_quantity','actural_sub_quantity']]
    json1 = frame1.to_json(orient='records',force_ascii=False)
    return jsonify(json1)


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
