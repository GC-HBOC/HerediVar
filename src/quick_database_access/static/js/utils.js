/////////////// filter and sort tables according to specific columns

function filterTable_one_column(filter, col, table) {
    var table, tr, td, cell, i;
    filter = filter.toUpperCase();
    tr = table.getElementsByTagName("tr");
    for (i = 1; i < tr.length; i++) { // loop over rows
        tr[i].style.display = "none"; // hide row
    
        td = tr[i].getElementsByTagName("td");
        if (col <= td.length && col >= 0) {
            cell = tr[i].getElementsByTagName("td")[col];
            if (cell) {
                if (cell.innerText.toUpperCase().indexOf(filter) > -1) {
                    tr[i].style.display = "";
                }
            }
        }
    }
}

// not used atm!
function filterTable_all_columns(filter) {
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
}


function sorter(colids){ // !! only insert columns from the same table
    var indices = []
    for (var i = 0; i < colids.length; i++) {
        var domid = colids[i]
        indices.push($(domid).index())
    }
    var table = $(domid).parents('table').eq(0)
    var rows = table.find('tr:gt(0)').toArray().sort(comparer(indices), )
    rows = rows.reverse()
    for (var i = 0; i < rows.length; i++){
        table.append(rows[i])
    }
}

function comparer(indices) {
    return function(a, b) {
        for (var i = 0; i < indices.length; i++) {
            var row_index = indices[i]
            var valA = getCellValue(a, row_index)
            var valB = getCellValue(b, row_index)
            var result = sort_helper(valA, valB)
            if (result !== 0) {
                break;
            }
        }

        return result

    }
}

function sort_helper(valA, valB){
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

function getCellValue(row, index){
    return $(row).children('td').eq(index).text()
}



$(document).ready(function()
{
    ////////// activate bootstrap tooltips
    $("body").tooltip({ selector: '[data-bs-toggle=tooltip]' });

    ////////// functionality for the reannotate button
    $('#reannotate_button').click(function()
    {
        $(this).attr('disabled', true);
        return true;
    });
});



function get_amino_acids(three_to_one = true){
    if (three_to_one){
        return {
            "ala": "A",
            "arg": "R",
            "asn": "N",
            "asp": "D",
            "asx": "B",
            "cys": "C",
            "glu": "E",
            "gln": "Q",
            "glx": "Z",
            "gly": "G",
            "his": "H",
            "ile": "I",
            "leu": "L",
            "lys": "K",
            "met": "M",
            "phe": "F",
            "pro": "P",
            "ser": "S",
            "thr": "T",
            "trp": "W",
            "tyr": "Y",
            "val": "V"
        }
    } else {
        return {
            "A": "ala",
            "R": "arg",
            "N": "asn",
            "D": "asp",
            "B": "asx",
            "C": "cys",
            "E": "glu",
            "Q": "gln",
            "Z": "glx",
            "G": "gly",
            "H": "his",
            "I": "ile",
            "L": "leu",
            "K": "lys",
            "M": "met",
            "F": "phe",
            "P": "pro",
            "S": "ser",
            "T": "thr",
            "W": "trp",
            "Y": "tyr",
            "V": "val"
        }
    }

}
