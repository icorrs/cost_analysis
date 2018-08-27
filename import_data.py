#coding = utf-8
"""
import excel data to mysql,and change the title to english.Mostly about current detail_wbs_quantity and material price.
"""

import os
import re
import datetime

import pandas as pd 
import sqlalchemy
import pymysql
import openpyxl

import cost_analysis

engine = cost_analysis.engine_default


def get_title_dic():
    'get title\'s name in dic which key is chinese and value is english'
    frame1 = pd.read_sql_query('select * from chinese_vs_english_title',engine)
    title_dic = {}
    for i in range(len(frame1['chinese'])):
        title_dic.setdefault(frame1.iloc[i,1],frame1.iloc[i,2])
    return title_dic


def get_path():
    'get path that contains the excel file need to be imported'
    path = input('please enter excel file path:')
    if os.path.isdir(path) or os.path.isfile(path):
        return path
    else:
        get_path()


def mysql_mirage():
    'mirage main attribute'
    title_dic = get_title_dic()
    path = get_path()

    #mirage single excel file
    def mirage_file(file):
        if os.path.splitext(file)[1][1:] in ('xlsx','xls'):
            frame_file = pd.read_excel(file)
        elif os.path.splitext(file)[1][1:] in ('csv'):
            frame_file = pd.read_csv(file)
        else:
            print('no file is xlsx or xls or csv,please check:')
        frame_file = frame_file.rename(title_dic,axis='columns')
        print('%s begin to mirage %s to mysql'%(str(datetime.datetime.today()),file))
        if file_name in title_dic.keys():
            frame_file.to_sql(title_dic[file_name].replace(' ',''),engine,if_exists='replace',index=False)
        else:
            frame_file.to_sql(file_name,engine,if_exists='replace',index=False)
    
    if os.path.isdir(path):
        os.chdir(path)
        file_list=os.listdir(path)    
        for file in file_list:
            file_name=os.path.splitext(file)[0]
            mirage_file(file)        
        print('%s finished'%(str(datetime.datetime.today())))
    else:
        os.chdir(os.path.dirname(path))
        file=os.path.basename(path)
        file_name=os.path.splitext(file)[0]
        mirage_file(path)


if __name__=='__main__':
    mysql_mirage()
