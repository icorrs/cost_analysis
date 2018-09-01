#coding=utf-8

import json

import cost_analysis

def get_translate_dic():
    dic1 = cost_analysis.get_translate_dic()
    json1 = json.dumps(dic1,ensure_ascii=False,separators=(',',':'))
    f = open('/var/www/myweb/static/js/translate_dic.js','w')
    f.write('translate_dic = '+json1)
    f.close()

if __name__ == '__main__':
    get_translate_dic()
