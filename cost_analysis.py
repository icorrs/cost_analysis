#coding=utf-8
'''
   A module get cost data from mysql,return cost_analysis sheet.
   at this moment(2018.04.03）,does not consider how can be showed in web,
   just process in localmachine.
'''

import datetime
import os
import re

import pandas as pd
import pymysql
import sqlalchemy

import consts 

#default arg
date_default = consts.DATE_DEFAULT
route_default = 'localmachine'

class MetaSingleton(type):
    _instances = {}
    def __call__(cls,*args,**kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton,cls).__call__(
                *args,**kwargs)
        return cls._instances[cls]


class Database(metaclass=MetaSingleton):
    engine_default = None
    def myweb_engine(self):
        self.engine_str = consts.ENGINE_STR
        if self.engine_default is None:
            self.engine_default = sqlalchemy.create_engine(self.engine_str)
        return self.engine_default


def get_income_boq(engine=Database().myweb_engine()):
    'get income boq '
    frame_income_boq = pd.read_sql_query('select * from income_boq',engine)
    return frame_income_boq


def get_sub_contract_boq(engine=Database().myweb_engine()):
    'get sub_contract_boq'
    frame_sub_contract_boq = pd.read_sql_query('select * from \
        sub_contract_boq',engine)
    return frame_sub_contract_boq[['sub_contract_boq_code','sub_contract_boq_name',
            'sub_contract_boq_unit','sub_contract_boq_price']]


def get_wbs(engine=Database().myweb_engine()):
    'get wbs in calculate system'
    frame_wbs = pd.read_sql_query('select * from wbs',engine)
    return frame_wbs


def get_sub_contractor_account(engine=Database().myweb_engine()):
    'get sub_contractor_account'
    frame_sub_contractor_account = pd.read_sql_query('select * \
        from sub_contractor_account',engine)
    return frame_sub_contractor_account


def get_sub_contractor_list(engine=Database().myweb_engine()):
    'get all the sub_contractor\'s short name,return as list'
    frame1 = pd.read_sql_query('select sub_contractor_short_name \
                                from sub_contractor_account',engine)\
                                ['sub_contractor_short_name']
    list1 = list(frame1)
    return list1


def get_cal_and_payed(engine=Database().myweb_engine()):
    'get sub_contractor calculated num and payed num'
    frame1 = pd.read_sql_query('select * from cal_and_payed',engine)
    frame1['total_payed'] = frame1['bill_payed']+frame1['cash_payed']
    frame1['rate_of_payed'] = frame1['total_payed'].div(frame1['pure_cal'],fill_value=0)
    frame1['rate_of_bill'] = frame1['bill_payed'].div(frame1['total_payed'],fill_value=0)
    return frame1

def get_translate_dic(engine=Database().myweb_engine()):
    'get translate title table'
    frame1 = pd.read_sql_query('select chinese,english \
                                from chinese_vs_english_title',engine)
    translate_dic = {'total_material_cost':'甲供材总费用',
                    'actural_quantity':'完成工程量',
                    'id_of_legal_representative':'法人代表身份证号',
                    'income':'收入',
                    'income_cal':'收入结算',
                    'sub_cal':'分包结算'}
    for i in range(len(frame1['chinese'])):
        translate_dic.setdefault(frame1.iloc[i,1],frame1.iloc[i,0])
    return translate_dic
    

def translate_title(source_frame,engine=Database().myweb_engine()):
    '''
       get translate_dict which's key is english and 
       value is chinese.so the sheet's title can be translated to chinese.
       only be used when route='localmachine' and 
       rename in out_put csv file.in web and 
       import condition return english title.
    '''
    #get defualt translate_dict
    translate_dic = get_translate_dic()
    add_word_dic = {'cost':'费用','quantity':'工程量','sub_quantity':'优化后工程量',
                  'totalquantity':'总工程量','actrualquantity':'完成工程量'}
    def add_translate_item(title):
        # if title in default translate_dict,pass.else use re to check 
        # if the group(1) part is in defualt translate_dict.\
        # combine chinese to groupe(2)
        if title in translate_dic.keys():
            return title 
        else:
            if re.match(r'(.+)_(.+)$',title):     
            #for the frame's columns that not have '_',such as sub_contractor_short_name pivoted table.
                match_obj = re.match(r'(.+)_(.+)$',title)
                if match_obj.group(1) in translate_dic.keys():
                    if match_obj.group(2) not in add_word_dic.keys():
                        return translate_dic[match_obj.group(1)]+'_'+match_obj.group(2)
                    else:
                        return translate_dic[match_obj.group(1)]+'_'+add_word_dic[match_obj.group(2)]
                else:
                    return title
            else:
                return title 
    for title in source_frame.columns:
        if isinstance(title,tuple):
            title_word = add_translate_item(title[0])
            for i in range(1,len(title)):
                title_word = title_word+'_'+add_translate_item(title[i])
            translate_dic.setdefault(title,title_word)
        else:
            translate_dic.setdefault(title,add_translate_item(title))
    source_frame = source_frame.rename(columns=translate_dic)
    return source_frame
            

def income_analysis(date=date_default,engine=Database().myweb_engine(),route=route_default):
    '''
    income analysis.return a sheet contain income can be calculate
    if route is localmachine,get path to be saved.
    else pass(when need to show in web,change the code.).20180403
    '''
    frame_income_boq = get_income_boq()
    frame_worked_income = get_income_boq_detail(date=date)
    frame_worked_income = frame_worked_income[['income_boq_code',\
        'actural_quantity']]
    frame_worked_income = pd.pivot_table(frame_worked_income,\
        index=['income_boq_code'],values=['actural_quantity'],aggfunc='sum')
    frame_worked_income = pd.merge(frame_worked_income,frame_income_boq,\
        right_on='income_boq_code',left_index=True,how='outer')
    frame_worked_income['finished_income'] = (frame_worked_income\
        ['actural_quantity']*frame_worked_income['income_boq_price'])
    if route is 'localmachine':
        path = input('please enter save path:')
        print('%s:saving income_analysis excel file'%(datetime.datetime.today()))
        translate_title(frame_worked_income).to_csv\
            ('%s\\%s_income.csv'%(path,date),encoding='utf-8-sig')
        print('%s:save completeed'%(datetime.datetime.today()))
    else:  
        return frame_worked_income


def get_income_boq_detail(date=date_default,engine=Database().myweb_engine(),route=route_default):
    'get income boq  join detail_wbs'
    worked_income_sql = '''
                    select income_boq.income_boq_code,
                           detail_wbs.income_boq_proportion,
                           %s_quantity.%s_quantity,
                           detail_wbs.detail_wbs_quantity,
                           detail_wbs.detail_wbs_content,
                           detail_wbs.detail_wbs_beginning_mileage,
                           detail_wbs.detail_wbs_ending_mileage,
                           detail_wbs.detail_wbs_code
                    from income_boq join wbs join detail_wbs join %s_quantity 
                    on income_boq.income_boq_code=wbs.income_boq_code and 
                        wbs.wbs_code=detail_wbs.wbs_code and 
                        detail_wbs.detail_wbs_code=%s_quantity.detail_wbs_code 
                    where detail_wbs.detail_wbs_quantity>0
                    '''%(date,date,date,date)
    frame_worked_income = pd.read_sql_query(worked_income_sql,engine)
    frame_worked_income['actural_quantity'] = (frame_worked_income
        ['income_boq_proportion']*frame_worked_income['%s_quantity'%(date)])
    frame_worked_income['finished_income_quantity'] = frame_worked_income['actural_quantity']
    frame_worked_income['detail_wbs_income_quantity'] = (frame_worked_income
        ['detail_wbs_quantity']*frame_worked_income['income_boq_proportion'])
    return frame_worked_income


def income_wbs(date=date_default,engine=Database().myweb_engine(),route=route_default):
    'get income_wbs quantity need to be calculated'
    frame_wbs = get_wbs()
    query = '''
             select detail_wbs.detail_wbs_code,
                    detail_wbs.income_boq_proportion,
                    detail_wbs.wbs_code,
                    %s_quantity.%s_quantity
                    from detail_wbs join %s_quantity
                         on detail_wbs.detail_wbs_code=%s_quantity.detail_wbs_code
                    where %s_quantity.%s_quantity>0
            '''%(date,date,date,date,date,date)
    frame_income_wbs = pd.read_sql_query(query,engine)
    frame_income_wbs['actual_income_quantity'] = frame_income_wbs\
        ['income_boq_proportion']*frame_income_wbs['%s_quantity'%(date)]
    frame_income_wbs = frame_income_wbs.pivot_table(\
        'actual_income_quantity',index='wbs_code',aggfunc='sum')
    frame_income_wbs = pd.merge(frame_wbs,frame_income_wbs,\
        left_on='wbs_code',right_index=True,how='outer')
    if route=='localmachine':
        path = input('please enter path: ')
        print('%s:saving income_wbs_quantity'%(datetime.datetime.today()))
        translate_title(frame_income_wbs).to_csv\
            (os.path.join(path,'%s_income_wbs.csv'%(date)),encoding='utf-8-sig')
        print('%s:income_wbs_quantity save complete'%(datetime.datetime.today()))


def get_sub_contractor_quantity(date=date_default,engine=Database().myweb_engine()):
    '''
       query detail sub_contractor quantity,
       result contains wbs_code,income_boq_code,sub_contract_boq_code，
       which can be used in command_post_sub_contract_analysis(wbs vs sub_contract) and 
       cost_analysis(income_boq_code vs sub_contract)
       20180829 added sub_quantity column
    '''
    sub_contractor_quantity_sql = """
        select  wbs.wbs_code,
                wbs.income_boq_code,
                detail_wbs.detail_wbs_content,
                detail_wbs.detail_wbs_beginning_mileage,
                detail_wbs.detail_wbs_ending_mileage,
                detail_wbs.income_boq_proportion,
                detail_wbs.detail_wbs_code,
                detail_wbs.detail_wbs_quantity,
                detail_wbs.sub_contract_boq_code,
                detail_wbs.sub_contract_boq_proportion,
                detail_wbs_code_vs_sub_contractor_short_name.sub_contractor_short_name,
                %s_quantity.%s_quantity,
                %s_quantity.%s_sub_quantity                            
        from wbs join detail_wbs join detail_wbs_code_vs_sub_contractor_short_name join %s_quantity
        on wbs.wbs_code=detail_wbs.wbs_code and
                detail_wbs.detail_wbs_code=detail_wbs_code_vs_sub_contractor_short_name.detail_wbs_code and
                detail_wbs.detail_wbs_code=%s_quantity.detail_wbs_code
        where detail_wbs.detail_wbs_quantity>0
                     """%(date,date,date,date,date,date)
    frame_sub_contractor_quantity = pd.read_sql_query\
        (sub_contractor_quantity_sql,engine)
    frame_sub_contractor_quantity['actural_quantity'] = \
        (frame_sub_contractor_quantity['sub_contract_boq_proportion']*
        frame_sub_contractor_quantity['%s_quantity'%(date)])
    frame_sub_contractor_quantity['actural_sub_quantity'] = \
        (frame_sub_contractor_quantity['sub_contract_boq_proportion']*
        frame_sub_contractor_quantity['%s_sub_quantity'%(date)])  
    frame_sub_contractor_quantity['total_sub_quantity'] = (
        frame_sub_contractor_quantity['detail_wbs_quantity']*
        frame_sub_contractor_quantity['sub_contract_boq_proportion'])  
    frame_sub_contractor_quantity['income_boq_acturalquantity'] = \
        (frame_sub_contractor_quantity['income_boq_proportion']*
        frame_sub_contractor_quantity['%s_quantity'%(date)])
    return frame_sub_contractor_quantity[['detail_wbs_content',
        'detail_wbs_code','detail_wbs_beginning_mileage','detail_wbs_ending_mileage',
        'wbs_code','income_boq_code','sub_contract_boq_code',
        'sub_contractor_short_name','actural_quantity','total_sub_quantity',
        'actural_sub_quantity','income_boq_acturalquantity']]


def sub_contractor_analysis_command_post(date=date_default,route=route_default):
    '''
      sub_contractor_quantity analysis that command post asked.
      contrast quantity by wbs_code to sub_contract_boq_code
    '''
    frame1 = get_sub_contractor_quantity()
    frame_wbs = get_wbs()
    frame_sub_contract_boq = get_sub_contract_boq()
    frame_out = frame1.pivot_table('actural_quantity',
        index=['wbs_code','sub_contract_boq_code'],
        columns=['sub_contractor_short_name'],aggfunc='sum')
    frame_out = frame_out.reset_index()
    frame_out = pd.merge(frame_out,frame_wbs,on=['wbs_code'],how='outer')
    frame_out = pd.merge(frame_out,frame_sub_contract_boq,
        on=['sub_contract_boq_code'],how='outer')
    if route is 'localmachine':
        path = input('please enter save path:')
        print('%s:saving sub_contract_analysis command post asked')
        translate_title(frame_out).to_csv\
            ('%s\\%s_sub_contractor_analysis_command_post.csv'%(path,date),
            encoding='utf-8-sig')
        print('%s:save completed'%(datetime.datetime.today()))
    else:
        return frame_out


def sub_contractor_analysis_command_post2(date=date_default,route=route_default):
    '''
    the sub_contractyor_analysis command post asked at 201804 that 
    contrast quantity by income_boq_code to sub_contract_boq
    '''
    keys = ['detail_wbs_code','income_boq_code',
        'sub_contract_boq_code','sub_contractor_short_name']
    frame0 = get_sub_contractor_quantity(date=202001)
    frame0 = frame0[['detail_wbs_code','income_boq_code','income_boq_acturalquantity',
        'sub_contract_boq_code','sub_contractor_short_name','actural_quantity']]
    frame0 = frame0.rename(columns=
         {'income_boq_acturalquantity':'income_boq_totalquantity',
         'actural_quantity':'sub_contractor_totalquantity'})
    frame1 = get_sub_contractor_quantity()
    frame_income_boq = get_income_boq()
    frame_sub_contract_boq = get_sub_contract_boq()
    frame_out = pd.merge(frame0,frame1,on=keys,how='outer')
    frame_out = pd.pivot_table(frame_out,values=['income_boq_totalquantity',
        'sub_contractor_totalquantity','actural_quantity','income_boq_acturalquantity'],
        index=keys[1:3],columns=['sub_contractor_short_name'],aggfunc='sum')
    frame_out = pd.merge(frame_out.reset_index(),frame_income_boq,
        on='income_boq_code',how='outer')
    frame_out = frame_out.rename(columns={('sub_contract_boq_code', ''):
        'sub_contract_boq_code'})
    frame_out = pd.merge(frame_out,frame_sub_contract_boq,
        on='sub_contract_boq_code',how='outer')
    if route is 'localmachine':
        path = input('please enter save path:')
        print('%s:saving sub_contract_analysis command post asked2...'%
            (datetime.datetime.today()))
        translate_title(frame_out).to_csv\
            ('%s\\%s_sub_contractor_analysis_command_post2.csv'%(path,date),
            encoding='utf-8-sig')
        print('%s:save completed'%(datetime.datetime.today()))
    else:
        return frame_out
    

def sub_contractor_analysis(date=date_default,route=route_default):
    '''
      sub_contractor cost  analysis,columns are income_boq_code and sub_contract_boq
    '''
    frame1 = get_sub_contractor_quantity()
    frame_income_boq = get_income_boq()
    frame_sub_contract = get_sub_contract_boq()
    sub_contractor_list = get_sub_contractor_list()
    frame_out = frame1.pivot_table(['actural_sub_quantity'],
        index=['income_boq_code','sub_contract_boq_code'],
        columns=['sub_contractor_short_name'],aggfunc='sum')
    frame_out = frame_out.reset_index()
    frame_out = pd.merge(frame_out,frame_income_boq,
        on=['income_boq_code'],how='outer')
    frame_out = pd.merge(frame_out,frame_sub_contract,
        on=['sub_contract_boq_code'])
    for short_name in sub_contractor_list:
        if short_name in frame_out.columns:
            frame_out['%s_合价'%(short_name)] = frame_out[short_name]\
                *frame_out['sub_contract_boq_price']
        else:
            pass
    if route is 'localmachine':
        path = input('please enter save path:')
        print('%s:saving sub_contractor_analysis'%(datetime.datetime.today()))
        translate_title(frame_out).to_csv \
            ('%s\\%s_sub_contractor_analysis.csv'%(path,date),
            encoding='utf-8-sig')
        print('%s:save completed'%(datetime.datetime.today()))
    else:
        return frame_out


def get_material_quantity(material,date=date_default,engine=Database().myweb_engine(),route='web'):
    'get single material\'s quantity'
    frame_price = pd.read_sql_query('select * from price_of_%s'%(material),engine)
    if 'price_of_%s_%s'%(material,date) in frame_price.columns:
        price_now = 'price_of_%s_%s'%(material,date)
    else:
        price_now = 'price_of_%s'%(material)
    if 'remaining_%s_price_%s'%(material,date) in frame_price.columns:
        price_remaining = 'remaining_%s_price_%s'%(material,date)
    else:
        price_remaining = 'remaining_%s_price'%(material)
    if '%s_actural_proportion_%s'%(material,date) in frame_price.columns:
        actural_proportion = '%s_actural_proportion_%s'%(material,date) 
    else:
        actural_proportion = '%s_actural_proportion'%(material)
    get_material_quantity_sql = '''
                           select price_of_%s.%s_kind,
                                  price_of_%s.%s,
                                  price_of_%s.%s,
                                  price_of_%s.%s,
                                  %s.%s_proportion,
                                  %s.sub_contract_boq_code,
                                  detail_wbs.detail_wbs_code,
                                  detail_wbs.detail_wbs_quantity,
                                  detail_wbs.sub_contract_boq_proportion,
                                  %s_quantity.%s_quantity,
                                  wbs.income_boq_code,
                                  detail_wbs_code_vs_sub_contractor_short_name.sub_contractor_short_name
                            from price_of_%s join %s join detail_wbs join %s_quantity join wbs join 
                                 detail_wbs_code_vs_sub_contractor_short_name
                            on   price_of_%s.%s_kind=%s.%s_kind and
                                 %s.sub_contract_boq_code=detail_wbs.sub_contract_boq_code and
                                 detail_wbs.detail_wbs_code=%s_quantity.detail_wbs_code and
                                 detail_wbs.wbs_code=wbs.wbs_code and
                                 detail_wbs_code_vs_sub_contractor_short_name.detail_wbs_code 
                                 = detail_wbs.detail_wbs_code
                            where price_of_%s.%s_kind!='无'
                                '''%(material,material,
                                     material,price_now,
                                     material,price_remaining,
                                     material,actural_proportion,
                                     material,material,
                                     material,
                                     date,date,
                                     material,material,date,
                                     material,material,material,material,
                                     material,date,
                                     material,material)
    frame_material = pd.read_sql_query(get_material_quantity_sql,engine)
    #not use '' for actural_proportion and price_now because they are var
    frame_material['%s_quantity'%(material)] = (
            frame_material[actural_proportion]*
            frame_material['%s_quantity'%(date)]*
            frame_material['sub_contract_boq_proportion']*
            frame_material['%s_proportion'%(material)])
    frame_material['%s_totalquantity'%(material)] = (
            frame_material[actural_proportion]*
            frame_material['detail_wbs_quantity']*
            frame_material['sub_contract_boq_proportion']*
            frame_material['%s_proportion'%(material)])
    frame_material['%s_cost'%(material)] = (frame_material[price_now]
            *frame_material['%s_quantity'%(material)])
    return frame_material


def get_materials_quantity(date=date_default,engine=Database().myweb_engine(),route=route_default):
    '''
       get detail material quantity should be used and acturally used,
       contains income_boq_code,sub_contract_code,kind_of_material,material_actrual_proportion
       so can be analysis in income_boq,diffrent sub_contractor,diffrent work_area
    '''
    list_material = ['concrete','steel','flooring_material',
        'formwork','other_mateiral']
    income_boq_frame = get_income_boq()
    sub_contract_boq = get_sub_contract_boq()
    frame_steel = get_material_quantity('steel')
    frame_concrete = get_material_quantity('concrete')
    frame_flooring_material = get_material_quantity('flooring_material')
    frame_formwork = get_material_quantity('formwork')
    frame_other_material = get_material_quantity('other_material')
    
    '''
    if use default concat to connect diffrent frame,there will be 
    multiple lines in the result for those detail_wbs that
    use more than two diffrent material(for example the 209-3-b 
    c20-concrete-mixed-stone-wall).this can be fixed 
    when frame_out.the code as below:

        frame_out=pd.concat([frame_steel,frame_concrete,
            frame_flooring_material,frame_other_material,frame_formwork],
            ignore_index=True,keys=['steel','concrete',
            'flooring_material','other_material'])
    
     use merge/join to connect diffrent material frame,use merge,
     but the keys contain detail_wbs_code to make sure not 
     return Descartes with duplicate result.
     and the keys contain all the same columns between 
     material_frame,so the result will have no _x _y.
    '''
    keys_list = ['detail_wbs_code','%s_quantity'%(date),'detail_wbs_quantity',
         'income_boq_code','sub_contract_boq_code','sub_contract_boq_proportion',
         'sub_contractor_short_name']
    frame_out = pd.merge(frame_steel,frame_concrete,on=keys_list,how='outer')
    frame_out = pd.merge(frame_out,frame_flooring_material,on=keys_list,how='outer')
    frame_out = pd.merge(frame_out,frame_formwork,on=keys_list,how='outer')
    frame_out = pd.merge(frame_out,frame_other_material,on=keys_list,how='outer')
    frame_out['total_material_cost'] = frame_out['concrete_cost'].fillna(0)+\
        frame_out['steel_cost'].fillna(0)+frame_out['formwork_cost'].fillna(0)+\
        frame_out['flooring_material_cost'].fillna(0)+\
        frame_out['other_material_cost'].fillna(0)
    if route is 'localmachine':
        path = input('enter path to save:')
        frame_out = translate_title(frame_out)
        print('%s:saving material_quantity'%(datetime.datetime.today()))
        frame_out.to_csv('%s\\%s_material.csv'%(path,date),encoding='utf-8-sig')
        print('%s:save completed'%(datetime.datetime.today()))
    else:
        return frame_out
    

if __name__=='__main__':
    #income_analysis()
    #sub_contractor_analysis()
    #income_wbs()
    sub_contractor_analysis_command_post()
    #sub_contractor_analysis_command_post2()
    #get_materials_quantity()
