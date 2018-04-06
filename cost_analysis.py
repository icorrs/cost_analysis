'''
   A module get cost data from mysql,return cost_analysis sheet.
   at this moment(2018.04.03）,does not consider how can be showed in web,
   just process in localmachine.
'''

import os
import re

import pandas as pd
import sqlalchemy
import pymysql

#default arg
engine_default=sqlalchemy.create_engine('mysql+pymysql://root:nakamura7@localhost:3306/cost_analysis?charset=utf8')
route_default='localmachine'
date_default=input('please enter date:')


def get_income_boq(engine=engine_default):
    'get income boq '
    frame_income_boq=pd.read_sql_query('select * from income_boq',engine)
    return frame_income_boq


def get_sub_contract_boq(engine=engine_default):
    'get sub_contract_boq'
    frame_sub_contract_boq=pd.read_sql_query('select * from sub_contract_boq',engine)
    return frame_sub_contract_boq


def get_wbs(engine=engine_default):
    'get wbs in calculate system'
    frame_wbs=pd.read_sql_query('select * from wbs',engine)
    return frame_wbs


def get_sub_contractor_list(engine=engine_default):
    'get all the sub_contractor\'s short name,return as list'
    frame1=pd.read_sql_query('select sub_contractor_short_name from sub_contractor_account',engine)['sub_contractor_short_name']
    list1=list(frame1)
    return list1


def translate_title(source_frame,engine=engine_default):
    '''
       get translate_dict which\'s key is english and value is chinese.so the sheet\'s title can be translated to chinese.
       only be used when route='localmachine' and rename in out_put csv file.in web and import condition return english title.
    '''
    frame1=pd.read_sql_query('select chinese,english from chinese_vs_english_title',engine)
    translate_dic={}
    add_word_dic={'cost':'费用','quantity':'工程量'}
    for i in range(len(frame1['chinese'])):
        translate_dic.setdefault(frame1.iloc[i,1],frame1.iloc[i,0])
    for title in list(source_frame.columns):  #for the title add date/quantity/cost,process the translate_dic.
        match_obj=re.match(r'(.+)_(.+)$',title)
        if match_obj.group(1) in translate_dic.keys():
            if match_obj.group(2) not in add_word_dic.keys():
                translate_dic.setdefault(title,translate_dic[match_obj.group(1)]+'_'+match_obj.group(2))
            else:
                translate_dic.setdefault(title,translate_dic[match_obj.group(1)]+'_'+add_word_dic[match_obj.group(2)])
        else:
            pass
    source_frame=source_frame.rename(columns=translate_dic)
    return source_frame
            

def income_analysis(date=date_default,engine=engine_default,route=route_default):
    'income analysis.return a sheet contain income can be calculate'
    #if route is localmachine,get path to be saved.else pass(when need to show in web,change the code.).20180403
    worked_income_sql='''
                    select income_boq.income_boq_code,
                           detail_wbs.income_boq_proportion,
                           %s_quantity.%s_quantity 
                    from income_boq join wbs join detail_wbs join %s_quantity 
                    on income_boq.income_boq_code=wbs.income_boq_code and 
                        wbs.wbs_code=detail_wbs.wbs_code and 
                        detail_wbs.detail_wbs_code=%s_quantity.detail_wbs_code 
                    where %s_quantity.%s_quantity>0
                    '''%(date,date,date,date,date,date)
    frame_income_boq=get_income_boq()
    frame_worked_income=pd.read_sql_query(worked_income_sql,engine)
    frame_worked_income['actural_quantity']=frame_worked_income['income_boq_proportion']*frame_worked_income['%s_quantity'%(date)]
    frame_worked_income=frame_worked_income[['income_boq_code','actural_quantity']]
    frame_worked_income=pd.pivot_table(frame_worked_income,index=['income_boq_code'],values=['actural_quantity'],aggfunc='sum')
    frame_worked_income=pd.merge(frame_worked_income,frame_income_boq,right_on='income_boq_code',left_index=True,how='outer')
    if route is 'localmachine':
        path=input('please enter save path:')
        translate_title(frame_worked_income).to_csv('%s\\%s.csv'%(path,date),encoding='utf-8-sig')
    else:  
        return frame_worked_income
       

def get_sub_contractor_quantity(date=date_default,engine=engine_default,route=route_default):
    '''
       query detail sub_contractor quantity,
       result contains wbs_code,income_boq_code and sub_contract_boq_code，
       which can be used in command_post_sub_contract_analysis(wbs vs sub_contract) and 
       cost_analysis(income_boq_code vs sub_contract)
    '''
    sub_contractor_quantity_sql="""
                     select wbs.wbs_code,
                            wbs.income_boq_code,
                            detail_wbs.sub_contract_boq_code,
                            detail_wbs.sub_contract_boq_proportion,
                            detail_wbs_code_vs_sub_contractor_short_name.sub_contractor_short_name,
                            %s_quantity.%s_quantity                            
                     from wbs join detail_wbs join detail_wbs_code_vs_sub_contractor_short_name join %s_quantity
                     on wbs.wbs_code=detail_wbs.wbs_code and
                        detail_wbs.detail_wbs_code=detail_wbs_code_vs_sub_contractor_short_name.detail_wbs_code and
                        detail_wbs.detail_wbs_code=%s_quantity.detail_wbs_code
                     where %s_quantity.%s_quantity>0
                     """%(date,date,date,date,date,date)
    frame_sub_contractor_quantity=pd.read_sql_query(sub_contractor_quantity_sql,engine)
    frame_sub_contractor_quantity['actural_quantity']=(frame_sub_contractor_quantity['sub_contract_boq_proportion']*
                                                       frame_sub_contractor_quantity['%s_quantity'%(date)])
    return frame_sub_contractor_quantity[['wbs_code','income_boq_code','sub_contract_boq_code','sub_contractor_short_name','actural_quantity']]


def sub_contractor_analysis_command_post(date=date_default,route=route_default):
    '''
      sub_contractor_quantity analysis that command post asked.
      contrast quantity by wbs code to sub_contract
    '''
    frame1=get_sub_contractor_quantity()
    frame_wbs=get_wbs()
    frame_sub_contract_boq=get_sub_contract_boq()
    frame_out=frame1.pivot_table('actural_quantity',index=['wbs_code','sub_contract_boq_code'],columns=['sub_contractor_short_name'],aggfunc='sum')
    frame_out=frame_out.reset_index()
    frame_out=pd.merge(frame_out,frame_wbs,on=['wbs_code'],how='outer')
    frame_out=pd.merge(frame_out,frame_sub_contract_boq,on=['sub_contract_boq_code'],how='outer')
    if route is 'localmachine':
        path=input('please enter save path:')
        translate_title(frame_out).to_csv('%s\\%s_sub_contractor_analysis_command_post.csv'%(path,date),encoding='utf-8-sig')
    else:
        return frame_out


def sub_contractor_analysis(date=date_default,route=route_default):
    '''
      sub_contractor cost  analysis,columns are income_boq_code and sub_contract_boq
    '''
    frame1=get_sub_contractor_quantity()
    frame_income_boq=get_income_boq()
    frame_sub_contract=get_sub_contract_boq()
    sub_contractor_list=get_sub_contractor_list()
    frame_out=frame1.pivot_table('actural_quantity',index=['income_boq_code','sub_contract_boq_code'],columns=['sub_contractor_short_name'],aggfunc='sum')
    frame_out=frame_out.reset_index()
    frame_out=pd.merge(frame_out,frame_income_boq,on=['income_boq_code'],how='outer')
    frame_out=pd.merge(frame_out,frame_sub_contract,on=['sub_contract_boq_code'])
    for short_name in sub_contractor_list:
        if short_name in frame_out.columns:
            frame_out['%s_合价'%(short_name)]=frame_out[short_name]*frame_out['sub_contract_boq_price']
        else:
            pass
    if route is 'localmachine':
        path=input('please enter save path:')
        translate_title(frame_out).to_csv('%s\\%s_sub_contractor_analysis.csv'%(path,date),encoding='utf-8-sig')
    else:
        return frame_out


def get_material_quantity(date=date_default,engine=engine_default,route=route_default):
    '''
       get detail material quantity should be used and acturally used,
       contains income_boq_code,sub_contract_code,kind_of_material,material_actrual_proportion
       so can be analysis in income_boq,diffrent sub_contractor,diffrent work_area
    '''
    list_material=['concrete','steel','flooring_material','formwork','other_mateiral']
    income_boq_frame=get_income_boq()
    sub_contract_boq=get_sub_contract_boq()

    def get_material_quantity(material):
        'get single material\'s quantity'
        frame_price=pd.read_sql_query('select * from price_of_%s'%(material),engine)
        if 'price_of_%s_%s'%(material,date) in frame_price.columns:
            price_now='price_of_%s_%s'%(material,date)
        else:
            price_now='price_of_%s'%(material)
        if 'remaining_%s_price_%s'%(material,date) in frame_price.columns:
            price_remaining='remaining_%s_price_%s'%(material,date)
        else:
            price_remaining='remaining_%s_price'%(material)
        if '%s_actural_proportion_%s'%(material,date) in frame_price.columns:
            actural_proportion='%s_actural_proportion_%s'%(material,date) 
        else:
            actural_proportion='%s_actural_proportion'%(material)
        get_material_quantity_sql='''
                           select price_of_%s.%s_kind,
                                  price_of_%s.%s,
                                  price_of_%s.%s,
                                  price_of_%s.%s,
                                  %s.%s_proportion,
                                  %s.sub_contract_boq_code,
                                  detail_wbs.detail_wbs_code,
                                  detail_wbs.sub_contract_boq_proportion,
                                  %s_quantity.%s_quantity,
                                  wbs.income_boq_code
                            from price_of_%s join %s join detail_wbs join %s_quantity join wbs
                            on   price_of_%s.%s_kind=%s.%s_kind and
                                 %s.sub_contract_boq_code=detail_wbs.sub_contract_boq_code and
                                 detail_wbs.detail_wbs_code=%s_quantity.detail_wbs_code and
                                 detail_wbs.wbs_code=wbs.wbs_code
                            where %s_quantity.%s_quantity>0 and price_of_%s.%s_kind!='无'
                                '''%(material,material,\
                                     material,price_now,\
                                     material,price_remaining,\
                                     material,actural_proportion,\
                                     material,material,\
                                     material,\
                                     date,date,\
                                     material,material,date,\
                                     material,material,material,material,\
                                     material,date,\
                                     date,date,material,material)
        frame_material=pd.read_sql_query(get_material_quantity_sql,engine)
        frame_material['%s_quantity'%(material)]=frame_material[actural_proportion]*\
                                       frame_material['%s_quantity'%(date)]*\
                                       frame_material['sub_contract_boq_proportion']
        frame_material['%s_cost'%(material)]=frame_material[price_now]*frame_material['%s_quantity'%(material)]
        return frame_material
    frame_steel=get_material_quantity('steel')
    frame_concrete=get_material_quantity('concrete')
    frame_flooring_material=get_material_quantity('flooring_material')
    frame_formwork=get_material_quantity('formwork')
    frame_other_material=get_material_quantity('other_material')
    
    '''
     if use default concat to connect diffrent frame,there will be multiple lines in the result for those detail_wbs that
     use more than two diffrent material(for example the 209-3-b c20-concrete-mixed-stone-wall).this can be fixed 
     when frame_out.the code as below:

        frame_out=pd.concat([frame_steel,frame_concrete,frame_flooring_material,frame_other_material,frame_formwork],\
                       ignore_index=True,keys=['steel','concrete','flooring_material','other_material'])
    
     use merge/join to connect diffrent material frame,use merge,
     but the keys contain detail_wbs_code to make sure not return Descartes with duplicate result.
     and the keys contain all the same columns between material_frame,so the result will have no _x _y.
    '''
    keys_list=['detail_wbs_code','%s_quantity'%(date),'income_boq_code','sub_contract_boq_code','sub_contract_boq_proportion']
    frame_out=pd.merge(frame_steel,frame_concrete,on=keys_list,how='outer')
    frame_out=pd.merge(frame_out,frame_flooring_material,on=keys_list,how='outer')
    frame_out=pd.merge(frame_out,frame_formwork,on=keys_list,how='outer')
    frame_out=pd.merge(frame_out,frame_other_material,on=keys_list,how='outer')
    if route is 'localmachine':
        path=input('enter path to save:')
        frame_out=translate_title(frame_out)
        frame_out.to_csv('%s\\material_%s.csv'%(path,date),encoding='utf-8-sig')
    else:
        return frame_out
    

if __name__=='__main__':
    get_material_quantity()
