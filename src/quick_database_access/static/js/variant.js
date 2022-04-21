/////////////// The following filters and sorts the variant consequence table such that the tabs ensembl and refseq are working!

filterTable("ensembl")

function filterTable(filter) {
    var table, tr, td, cell, i, j;
    filter = filter.toUpperCase();
    table = document.getElementById("variantConsequenceTable");
    tr = table.getElementsByTagName("tr");
    for (i = 1; i < tr.length; i++) {
        tr[i].style.display = "none"; // hide row
    
        td = tr[i].getElementsByTagName("td");
        for (var j = 0; j < td.length; j++) {
            cell = tr[i].getElementsByTagName("td")[j];
            if (cell) {
                if (cell.innerText.toUpperCase().indexOf(filter) > -1) {
                    tr[i].style.display = "";
                break;
                }
            }
        }
    }
    sortTable()
}


function sortTable(){
    sorter('#variant_consequence_length_col') // sort by length
    sorter('#variant_consequence_numflags_col') // sort by num of flags
}


function sorter(domid){
    var table = $(domid).parents('table').eq(0)
    var rows = table.find('tr:gt(0)').toArray().sort(comparer($(this).index()), )
    rows = rows.reverse()
    for (var i = 0; i < rows.length; i++){
        table.append(rows[i])
    }
}

function comparer(index) {
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

function getCellValue(row, index){
    return $(row).children('td').eq(index).text()
}
