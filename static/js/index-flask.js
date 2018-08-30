var $income_boq = $('#income')
var $sub_contractor_title = $('#sub_contractor')
var $sub_contractor = $('#tab-2')
var $cal_and_payed = $('#cal_and_payed')
var $material_quantity_title = $('#material_quantity')
var $material_quantity = $('#tab-4')
var $content = $('#content')
var $footer1 = $('#footer1')
var $tab1 = $('#tab-1');

$(function() {
    $('#tab').tabs();
    $tab1.hide();
})

function round_num(num,point) {
    'if num is number act like python\'s round,else return num'
    if((typeof num)=='number') {
        var point_pow = Math.pow(10,point)
        return (Math.round(num*point_pow))/point_pow
    }
    else {
        return num
    }
}

$(function() {
    $income_boq.on('click',function(e) {
        e.preventDefault();
        $tab1.show()
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
                var translate_dic
                $.getJSON('/get_translate_dic')
                .done(function(data) {
                    translate_dic = JSON.parse(data);    
                })

                $.getJSON('get_income_boq_detail_json/{0}'.
                  replace('{0}',income_boq_code))
                .done(function(data) {
                    var $table = $('<table></table>')
                    var $throw = $('<tr></tr>')
                    console.log(JSON.parse(data))
                    for(var key in (JSON.parse(data))[0]) {
                        $throw.append('<th>'+translate_dic[key]+'</th>') 
                    }
                    $throw.append('<th>完成比例</th>')
                    $table.append($throw)
                    $.each(JSON.parse(data),function(key,value) {
                        var $row = $('<tr></tr>')
                        for(var key1 in value) {
                            $row.append('<td>'+round_num(value[key1],2)+'</td>')  
                        }
                        $row.append('<td>'+round_num((value['finished_income_quantity']/
                             value['detail_wbs_income_quantity'])*100,2)+'%</td>')
                        $table.append($row)
                    })
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
        $footer1.text('')
        $content.html('显示分包合同及分包信息 点击子标签以选择具体内容')
    })
})



$(function() {
    $sub_contractor.on('click',function(e) {
        e.preventDefault();
        var sub_contractor_content = e.target.getAttribute("id")
        var sub_contractor_href = e.target.getAttribute("href")
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
        var translate_dic
        $.getJSON('/get_translate_dic')
        .done(function(data) {
            translate_dic = JSON.parse(data);    
        })

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
                    $row.append($('<td>'+value[array1[j]]+'</td>'));
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
        $footer1.text('loading cal_and_payed_data....')
        $content.html('显示分包结算付款情况 加载中....')
        var title_list = ['sub_contractor_name','total_cal','pure_cal',
            'cash_payed','bill_payed','total_payed','rate_of_payed','rate_of_bill']
        var translate_dic
        $.getJSON('/get_translate_dic')
        .done(function(data) {
            translate_dic = JSON.parse(data);    
        })

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
                        $row.append($('<td>'+round_num(value[title_list[item]]*100,2)+'%</td>'))
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
            $sumrow.append($('<td>'+round_num((sum_bill_payed/
                (sum_cash_payed+sum_bill_payed))*100,2)+'%</td>'))
            $table.append($sumrow)
            $content.html($table)
            $footer1.text('cal_and_payed_data loaded')
        })
    })
})

$(function() {
    $material_quantity_title.on('click',function(e) {
        e.preventDefault;
        $footer1.text('')
        $content.html('显示材料收入量 点击具体材料以获取具体收入量')
    })
})

$(function() {
    $material_quantity.on('click',function(e) {
        e.preventDefault();
        var material_content = e.target.getAttribute("id");
        var material_href = e.target.getAttribute('href')
        var translate_dic
        var title_dic = ['sub_contractor_short_name',
            '{0}_kind'.replace('{0}',material_content),
            '{0}_quantity'.replace('{0}',material_content),
            '{0}_totalquantity'.replace('{0}',material_content)]
        $.getJSON('/get_translate_dic')
        .done(function(data) {
            translate_dic = JSON.parse(data);    
        })    

        $footer1.text('{0} message loading...'.replace('{0}',material_content))
        $content.html('{0}信息加载中...'.replace('{0}',material_href))
        $.getJSON('get_material_quantity_json/{0}'.replace('{0}',material_content))
        .done(function(data) {
            var $table = $('<table></table>')
            var $throw = $('<tr></tr>')
            for(var key in (JSON.parse(data))[0]) {
                $throw.append('<th>'+round_num(translate_dic[key],2)+'</th>')
            }
            $throw.append($('<th>完成比例</th>'))
            $table.append($throw)
            var sum_quantity = 0
            var sum_totalquantity =0
            $.each(JSON.parse(data),function(key,value) {
                var $row = $('<tr></tr>')
                for(var title in title_dic) {
                    $row.append($('<td>'+round_num(value[title_dic[title]],2)+'</td>'))
                }
                $row.append($('<td>'+round_num((value['{0}_quantity'.replace('{0}',material_content)]/
                            value['{0}_totalquantity'.replace('{0}',material_content)])*100,2)+'%</td>'))
                $table.append($row)
                sum_quantity += value['{0}_quantity'.replace('{0}',material_content)]
                sum_totalquantity += value['{0}_totalquantity'.replace('{0}',material_content)]
            })
            var $sumrow = $('<tr class="sum"><td></td><td>合计</td></tr>')
            $sumrow.append($('<td>'+round_num(sum_quantity,2)+'</td>'))
            $sumrow.append($('<td>'+round_num(sum_totalquantity,2)+'</td>'))
            $sumrow.append($('<td>'+round_num((sum_quantity/sum_totalquantity)*100,2)+'%</td>'))
            $table.append($sumrow)
            $content.html($table)
            $footer1.text('{0} message loaded'.replace('{0}',material_content))
        })  
    })
})

