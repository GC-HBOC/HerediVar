$('.sortable').click(click_sorter);

function click_sorter(){
    var table = $(this).parents('table').eq(0)
    var index = $(this).parents('th').eq(0).index()
    var rows = table.find('tr:gt(0)').toArray().sort(click_comparer(index), )
    this.asc = !this.asc
    if (!this.asc){
        rows = rows.reverse()
    }
    for (var i = 0; i < rows.length; i++){
        table.append(rows[i])
    }
}

function click_comparer(index) {
    return function(a, b) {
        var valA = getCellValue(a, index), valB = getCellValue(b, index)

        // sort none at the end
        var exceptions = [ "none" ];
        if (exceptions.includes(valA.toString().toLowerCase())) {
            return -1
        }
        if (exceptions.includes(valB.toString().toLowerCase())) {
            return 1
        }

        //normal case
        if ($.isNumeric(valA) && $.isNumeric(valB)) { 
            return valA - valB
        } else {
            return valA.toString().localeCompare(valB)
        }
    }
}

