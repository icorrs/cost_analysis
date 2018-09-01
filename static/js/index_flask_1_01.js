var $income_boq = $('#income')
var $sub_contractor_title = $('#sub_contractor')
var $sub_contractor = $('#tab-2')
var $cal_and_payed = $('#cal_and_payed')
var $material_quantity_title = $('#material_quantity')
var $material_quantity = $('#tab-4')
var $sub_contractor_income_title = $('#sub_contractor_income')
var $sub_contractor_income = $('#tab-5')
var $content = $('#content')
var $footer1 = $('#footer1')
var $tab1 = $('#tab-1');

$(function() {
    $('#tab').tabs();
    $tab1.hide();
})

function round_num(num,point) {
    'if num is number act like python\'s round,else return num'
    if(!num) {
        return ''
    }
    else if((typeof num)=='number') {
        var point_pow = Math.pow(10,point)
        return (Math.round(num*point_pow))/point_pow
    }
    else {
        return num
    }
}


function round_percentage(percentage) {
    'change num to percentage format'
    if(!percentage) {
        return ''
    }
    else if((typeof percentage) == 'number') {
        return round_num(percentage*100,2)+'%'
    }
    else {
        return percentage
    }
}


function table_json(data,divided_key='',divid_key='') {
    'read json data return a table which\'s title is the json data\'s key;\
    and if divided_key divid_key definded,add a rate column'
    var json_data = JSON.parse(data)

    if(divided_key == '' && divid_key == '') {
        var $table = $('<table></table>')
        var $throw = $('<tr><th>序号</th></tr>')
        for(var key in json_data[0]) {
            $throw.append('<th>'+round_num(translate_dic[key],2)+'</th>')
        }
        $table.append($throw)
        var line_count = 0
        for(var num in json_data) {
            line_count += 1
            var $row = $('<tr><td>'+line_count+'</td></tr>')
            for(var key in json_data[num]) {
                $row.append($('<td>'+round_num((json_data[num])[key],2)+'</td>'))
            }
            $table.append($row)
            $('tr:even').addClass('even')
        }
        return $table
    }
    else if(divided_key && divid_key){
        var sum_divided_key = 0
        var sum_divid_key = 0
        var $table = $('<table></table>')
        var $throw = $('<tr><th>序号</th></tr>')
        console.log(translate_dic)
        for(var key in json_data[0]) {
            $throw.append('<th>'+translate_dic[key]+'</th>')
        }
        $throw.append('<th>'+'比例('+translate_dic[divided_key]+'/'+
            translate_dic[divid_key]+')</th>')
        $table.append($throw)
        var line_count = 0
        for(var num in json_data) {
            line_count += 1
            var $row = $('<tr><td>'+line_count+'</td></tr>')
            for(var key in json_data[num]) {
                if(key == 'sub_contract_boq_code') {
                    $row.append($('<td><a href="" id={0}>'.replace('{0}',(json_data[num])[key])
                        +(json_data[num])[key]+'</a></td>'))
                }
                else {
                    $row.append($('<td>'+round_num((json_data[num])[key],2)+'</td>'))
                }    
            }
            var percentage = json_data[num][divided_key]/json_data[num][divid_key]
            sum_divided_key += json_data[num][divided_key]
            sum_divid_key += json_data[num][divid_key]
            $row.append($('<td>'+round_percentage(percentage)+'</td>'))
            $table.append($row)
            $('tr:even').addClass('even')
        } 
        return [$table,sum_divided_key,sum_divid_key]
    }
}


$(function() {
    $income_boq.on('click',function(e) {
        e.preventDefault();
        $tab1.show()
        $('a').removeClass('current')
        $footer1.text('loading income table...')
        var rows = [];
        $content.html('收入清单完成情况 加载中....')
        $.getJSON('/get_income_json')
        .done(function(data) {
            var sum_income = 0
            var row_count = 0           
            var $table = $('<table><tr>\
            <th>序号</th>\
            <th>收入清单编号</th>\
            <th>收入清单名称</th>\
            <th>收入清单单位</th>\
            <th>收入清单单价</th>\
            <th>收入清单总量</th>\
            <th>收入清单完成量</th>\
            <th>收入清单完成价</th>\
            </tr></table>')
            $.each(JSON.parse(data),function(key,value) {
                row_count += 1
                var $row = $('<tr></tr>')
                $row.append($('<td></td>').text(row_count))
                $row.append($('<td>'+'<a href="" id={0}>'.
                     replace('{0}',value.income_boq_code)+value.income_boq_code+'</a>'+'</td>'))
                $row.append($('<td></td>').text(value.income_boq_name))
                $row.append($('<td></td>').text(value.income_boq_unit))
                $row.append($('<td></td>').text(value.income_boq_price))
                $row.append($('<td></td>').text(value.income_boq_quantity))
                $row.append($('<td></td>').text(round_num(value.actural_quantity,2)))
                $row.append($('<td></td>').text(round_num(value.income,2)))
                rows.push({jsonword:value,$element:$row})
                $table.append($row)
                sum_income += value.income
            })
            var $sumrow = $('<tr class="sum"></tr>')
            $sumrow.append($('<td></td>'))
            $sumrow.append($('<td></td>'))
            $sumrow.append($('<td></td>').text('合计'))
            $sumrow.append($('<td></td>'))
            $sumrow.append($('<td></td>'))
            $sumrow.append($('<td></td>'))
            $sumrow.append($('<td></td>'))
            $sumrow.append($('<td></td>').text(round_num(sum_income,2)))
            $table.append($sumrow)
            $content.html($table)
            $footer1.text('收入清单完成情况加载完毕')
            $table.on('click',function(e) {
                e.preventDefault();     
                var income_boq_code = e.target.id;
                if(!income_boq_code) {
                }
                else {
                $tab1.hide();
                $content.html('加载{0}明细'.replace('{0}',income_boq_code))
                $footer1.text('loading....')

                $.getJSON('get_income_boq_detail_json/{0}'.
                  replace('{0}',income_boq_code))
                .done(function(data) {
                    var table_obj = table_json(data,divided_key='finished_income_quantity',
                        divid_key='detail_wbs_income_quantity')
                    var $table = table_obj[0]
                    var sum_finished_income_quantity = round_num(table_obj[1],2)
                    var sum_detail_wbs_income_quantity = round_num(table_obj[2],2)
                    var $sumrow = $('<tr class="sum">'+'<td></td>'+'<td></td>'+
                        '<td>合计</td>'+'<td></td>'+'<td></td>'+'</tr>')
                    $sumrow.append('<td>'+sum_detail_wbs_income_quantity+'</td>')
                    $sumrow.append('<td>'+sum_finished_income_quantity+'</td>')
                    $sumrow.append('<td>'+round_percentage(sum_finished_income_quantity/
                        sum_detail_wbs_income_quantity)+'</td>')
                    $table.append($sumrow)
                    $content.html($table)
                    $footer1.text('{0} detail loaded'.replace('{0}',income_boq_code))
                })
                }
            })
        })
    })
})

$(function() {
    $sub_contractor_title.on('click',function(e) {
        e.preventDefault;
        $('a').removeClass('current')
        $footer1.text('')
        $content.html('显示分包合同及分包信息 点击子标签以选择具体内容')
    })
})

$(function() {
    $sub_contractor.on('click',function(e) {
        e.preventDefault();
        var sub_contractor_content = e.target.getAttribute("id")
        var sub_contractor_href = e.target.getAttribute("href")
        $('a').removeClass('current')
        $('#{0}'.replace('{0}',sub_contractor_content)).addClass('current')
        $footer1.text('{0}loading....'.replace('{0}',sub_contractor_content))
        $content.html('{0}信息 加载中....'.replace('{0}',sub_contractor_href))
        //list the columns title needed
        var sub_contractor_title = {
            'sub_contractor_condition':
            ['sub_contractor_name','loc','legal_representative','agent','phone'],
            'sub_contract_message':
            ['sub_contractor_name','sub_contract_work','contract_code','price',
            'contract_sign_date'],
            'sub_contractor_licence':
            ['sub_contractor_name','business_licence_code',
            'qualification_certificat_code','qualification_certificat_level',
            'safety_licence','safety_licence_end_date'],
            'sub_contractor_bank_account':
            ['sub_contractor_name','bank_name','bank_count']}
        $.getJSON('/get_sub_contractor_account_json')
        .done(function(data) {
            var array1 = sub_contractor_title[sub_contractor_content];
            var $table = $('<table></table>');
            var $throw = $('<tr></tr>');
            for(var i in array1) {
                $throw.append($('<th>'+translate_dic[array1[i]]+'</th>'));
            }
            $table.append($throw);           
            $.each(JSON.parse(data),function(key,value) {
                $row = $('<tr></tr>');
                for(var j in array1) {
                    $row.append($('<td>'+round_num(value[array1[j]],2)+'</td>'));
                }
                $table.append($row);
            })
            $content.html($table);
            $footer1.text('{0} loaded'.replace('{0}',sub_contractor_content))
        })
    })
})

$(function() {
    $cal_and_payed.on('click',function(e) {
        e.preventDefault();
        $('a').removeClass('current')
        $footer1.text('loading cal_and_payed_data....')
        $content.html('显示分包结算付款情况 加载中....')
        var title_list = ['sub_contractor_name','total_cal','pure_cal',
            'cash_payed','bill_payed','total_payed','rate_of_payed','rate_of_bill']
        $.getJSON('/get_cal_and_payed_json')
        .done(function(data) {
            var $table = $('<table></table>')
            var $throw = $('<tr></tr>')
            for(var item in title_list) {
                $throw.append($('<th>'+translate_dic[title_list[item]]+'</th>'))
            }
            $table.append($throw)
            var sum_total_cal = 0
            var sum_pure_cal = 0
            var sum_cash_payed = 0
            var sum_bill_payed = 0
            $.each(JSON.parse(data),function(key,value) {
                var $row = $('<tr></tr>')
                for(var item in title_list) {
                    if(title_list[item] == 'rate_of_payed'||
                       title_list[item] == 'rate_of_bill') {
                        $row.append($('<td>'+round_percentage(value[title_list[item]])+'</td>'))
                    }
                    else {
                        $row.append($('<td>'+round_num(value[title_list[item]],2)+'</td>'))
                    }
                }
                $table.append($row)
                sum_total_cal += value.total_cal
                sum_pure_cal += value.pure_cal 
                sum_cash_payed += value.cash_payed 
                sum_bill_payed += value.bill_payed
            })
            var $sumrow = $('<tr class="sum"><td>合计</td></tr>')
            $sumrow.append($('<td>'+round_num(sum_total_cal,2)+'</td>'))
            $sumrow.append($('<td>'+round_num(sum_pure_cal,2)+'</td>'))
            $sumrow.append($('<td>'+round_num(sum_cash_payed,2)+'</td>'))
            $sumrow.append($('<td>'+round_num(sum_bill_payed,2)+'</td>'))
            $sumrow.append($('<td>'+round_num((sum_cash_payed+sum_bill_payed),2)+'</td>'))
            $sumrow.append($('<td>'+round_num(((sum_cash_payed+sum_bill_payed)/
                sum_pure_cal)*100,2)+'%</td>'))
            $sumrow.append($('<td>'+round_percentage(sum_bill_payed/
                (sum_cash_payed+sum_bill_payed))+'</td>'))
            $table.append($sumrow)
            $content.html($table)
            $footer1.text('cal_and_payed_data loaded')
        })
    })
})

$(function() {
    $material_quantity_title.on('click',function(e) {
        e.preventDefault;
        $('a').removeClass('current')
        $footer1.text('')
        $content.html('显示材料收入量 点击具体材料以获取具体收入量')
    })
})

$(function() {
    $material_quantity.on('click',function(e) {
        e.preventDefault();
        var material_content = e.target.getAttribute("id");
        var material_href = e.target.getAttribute('href')
        $('a').removeClass('current')
        $('#{0}'.replace('{0}',material_content)).addClass('current')
        $footer1.text('{0} message loading...'.replace('{0}',material_content))
        $content.html('{0}信息加载中...'.replace('{0}',material_href))
        $.getJSON('get_material_quantity_json/{0}'.replace('{0}',material_content))
        .done(function(data) {
            var table_obj = table_json(data,
                divided_key='{0}_quantity'.replace('{0}',material_content),
                divid_key='{0}_totalquantity'.replace('{0}',material_content))
            var $table = table_obj[0]
            var sum_quantity = table_obj[1]
            var sum_totalquantity = table_obj[2]
            var $sumrow = $('<tr class="sum"><td></td><td></td><td>合计</td></tr>')
            $sumrow.append($('<td>'+round_num(sum_quantity,2)+'</td>'))
            $sumrow.append($('<td>'+round_num(sum_totalquantity,2)+'</td>'))
            $sumrow.append($('<td>'+round_percentage(sum_quantity/sum_totalquantity)+'</td>'))
            $table.append($sumrow)
            $content.html($table)
            $footer1.text('{0} message loaded'.replace('{0}',material_content))
        })  
    })
})

$(function() {
    $sub_contractor_income_title.on('click',function() {
        $content.html('显示分包产值信息　点击分包名称以获取具体内容')
        $footer1.text('')
        $('a').removeClass('current');
    })
})

$(function() {
    $sub_contractor_income.on('click',function(e) {
        e.preventDefault(); 
        var contractor_short_name = e.target.id;
        $('a').removeClass('current');
        $('#{0}'.replace('{0}',contractor_short_name)).addClass('current');
        $content.html('正在获取{0}产值信息....'.replace('{0}',contractor_short_name))
        $.getJSON('get_sub_contractor_income_json/{0}'
          .replace('{0}',contractor_short_name))
        .done(function(data) {
            var table_obj = table_json(data,divided_key=
                'actural_sub_income',divid_key='total_sub_income')
            var $table = table_obj[0]
            var sum_actural_sub_income = table_obj[1]
            var sum_total_sub_income = table_obj[2]
            var $sumrow = $('<tr class="sum"><td></td>\
                <td></td><td>合计</td><td></td><td></td>\
                <td></td><td></td><td>'+round_num(sum_total_sub_income,2)+
                '</td><td>'+round_num(sum_actural_sub_income,2)+'</td>'+'<td>'+
                round_percentage(sum_actural_sub_income/
                    sum_total_sub_income)+'</td></tr>')
            $table.append($sumrow)
            $content.html($table) 
            $footer1.text('{0}产值加载完成 点击清单号以获取明细'
            　　　.replace('{0}',contractor_short_name))
            $table.on('click',function(e) {
                e.preventDefault();
                var contract_boq_code = e.target.id;
                if(!contract_boq_code) {
                }
                else {
                    $content.html('获取{0}分包{1}清单明细....'.
                        replace('{0}',contractor_short_name).
                        replace('{1}',contract_boq_code))
                    $.getJSON('/get_sub_contractor_income_detail_json/{0}/{1}'.
                        replace('{0}',contractor_short_name).
                        replace('{1}',contract_boq_code))
                    .done(function(data) {
                        var table_obj = table_json(data,divided_key=
                            'actural_sub_quantity',divid_key='total_sub_quantity')
                        var $table = table_obj[0]
                        var sum_actural_quantity = table_obj[1]
                        var sum_total_quantity = table_obj[2]
                        $content.html($table)
                        $footer1.text('{0}分包{1}加载完成'.
                            replace('{0}',contractor_short_name).
                            replace('{1}',contract_boq_code))
                    })
                }
            })
        })
    })
})
