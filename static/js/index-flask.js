var $income_boq = $('#income_boq')
var $content = $('#content')

$(function() {
    $income_boq.on('click',function(e) {
        e.preventDefault();
        var rows = [];
        $.getJSON('/get_income_boq_json')
        .done(function(data) {
            var $table = $('<table><tr>\
            <th>收入清单编号</th>\
            <th>收入清单名称</th>\
            <th>收入清单单价</th>\
            <th>收入清单完成</th>\
            </tr></table>')
            $.each(JSON.parse(data),function(key,value) {
                var $row = $('<tr></tr>')
                $row.append($('<td></td>').text(value.income_boq_code))
                $row.append($('<td></td>').text(value.income_boq_name))
                $row.append($('<td></td>').text(value.income_boq_price))
                $row.append($('<td></td>').text(value.income_boq_quantity))
                rows.push({jsonword:value,$element:$row})
                $table.append($row)
            $content.html($table)
            })
        })
    })
})
