/////////////// filter and sort tables according to specific columns

function filterTable_one_column(filter, col, table, filter_visible = false) {
    var table, tr, td, cell, i;
    filter = filter.toUpperCase();
    tr = table.getElementsByTagName("tr");
    remove_default_caption(table);
    displayed = 0;
    for (i = 1; i < tr.length; i++) { // loop over rows
        tr[i].style.display = "none"; // hide row
        if (!filter_visible) {
            tr[i].setAttribute('is-visible', 'false')
        }
    
        td = tr[i].getElementsByTagName("td");
        if (col <= td.length && col >= 0) {
            cell = tr[i].getElementsByTagName("td")[col];
            if (cell) {
                if (cell.innerText.toUpperCase().indexOf(filter) > -1) {
                    if (!filter_visible) {
                        tr[i].setAttribute('is-visible', 'true')
                    }

                    if (tr[i].getAttribute('is-visible') == 'true' || !tr[i].hasAttribute('is-visible')) {
                        tr[i].style.display = "";
                        displayed += 1;
                    }
                }
            }
        }
    }

    if (displayed == 0) {
        add_default_caption(table)
    }
}

function add_default_caption(table) {
    const cap = document.createElement("caption");
    cap.setAttribute('class', 'defaultrow');
    cap.textContent ='Nothing to show';
    table.appendChild(cap);
}

function remove_default_caption(table) {
    var caps = table.getElementsByClassName('defaultrow');

    while(caps[0]) {
        caps[0].parentNode.removeChild(caps[0]);
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


function remove_sort_direction_arrows(table_id) {
    if (table_id[0] !== '#') {
        table_id = '#' + table_id
    }
    $(table_id).find('.sortable[ascending]').removeAttr('ascending')
}


$('.sortable').click(function(e) {
    const table_id = '#' + $(this).parents('table').attr('id')
    sorter([$(this).parents('th').index()], table_id)
});

// used for sorting of table columns
// colids can either be actual ids or the index of the column in the table
function sorter(colids, table_id){
    var table = $(table_id)

    if (table.length == 0) { // this checks if the table is present in the current html
        return
    }

    remove_sort_direction_arrows(table_id)

    var indices = []
    for (var i = 0; i < colids.length; i++) {
        var domid = colids[i]
        if (domid[0] == '#') { // the 'domid' is the jquery id selector starting with a # beware that the domid is the id of the th
            indices.push($(domid).index())
        } else { // the 'domid' is its column index
            indices.push(domid) 
        }
    }
    
    

    var directions = []
    for (var i = 0; i < indices.length; i++) {
        var current_index = indices[i]
        var current_th = table.find('th').get(current_index)
        var current_sortable = current_th.querySelector('.sortable')

        /*
        console.log(table.find('th'))
        console.log(current_index)
        console.log(current_th)
        */

        update_asc(current_th)
        var current_asc = current_th.getAttribute('asc')

        if (current_sortable != null) {
            current_sortable.setAttribute('ascending', current_asc) // used by css to add the arrows which indicate the direction of sorting
        }

        directions.push(convert_string_to_bool(current_asc))
    }

    var rows = table.eq(0).find('tr:gt(0)').toArray().sort(comparer(indices, directions), )


    for (var i = 0; i < rows.length; i++){
        table.eq(0).append(rows[i])
    }

}



function update_asc(obj) {
    if (obj.hasAttribute('asc')) {
        var current_asc = obj.getAttribute('asc')
        if (current_asc == 'true') {
            obj.setAttribute('asc', 'false')
        } else if (current_asc == 'false'){
            obj.setAttribute('asc', 'true')
        }
    } else {
        obj.setAttribute('asc', 'false')
    }
}

function comparer(indices, directions) {
    return function(a, b) {
        for (var i = 0; i < indices.length; i++) {
            var row_index = indices[i]
            var asc = directions[i]
            var valA = getCellValue(a, row_index)
            var valB = getCellValue(b, row_index)
            var result = sort_helper(valA, valB)
            if (!asc) {
                result = result * -1
            }
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



function convert_string_to_bool(s) {
    if (s === 'true') {
        return true
    } else if (s === 'false') {
        return false
    }
    return null
}


$(document).ready(function()
{
    // add default row to all empty tables
    $(".table").map(function() {
        var nrows = $(this).find("tbody").find("tr").length
        if (nrows === 0) {
            add_default_caption($(this).get(0))
        }
    });

    ////////// activate bootstrap tooltips
    $("body").tooltip({ selector: '[data-bs-toggle=tooltip]' });
    $('.large-tt').tooltip({
        template: '<div class="tooltip" role="tooltip"><div class="tooltip-arrow"></div><div class="tooltip-inner large"></div></div>'
    });
    


    ////////// functionality for column filters in tables
    $(".column-filter").on("keyup", function() {
        var table = $(this).parents('table').get(0)
        var index = $(this).parents('th').index()
        filterTable_one_column($(this).val(), index, table, true)
    });


    $("*[data-href]").mousedown(function(event) {
        switch (event.which) {
            case 1: // left mouse button
                window.location = $(this).data("href"); // open link in same tab
                break;
            case 2: // middle mouse button
                //alert('Middle mouse button pressed');
                window.open($(this).data("href")); // open in new tab
                break;
            case 3: // right mouse button
                // nothing rn
                break;
        }
    });


    //$('.wide-tooltip').find('.tooltip-inner').addClass('.wide-inner-tooltip')
    //console.log($('.wide-tooltip').find('.tooltip-inner'))
});


var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
  return new bootstrap.Popover(popoverTriggerEl)
})


// use this to escape special chars when using tojson jinja filter
function escape_special_chars(input_string) {
    return input_string.replace(/\n/g, "\\n")
               .replace(/\'/g, "\\'")
               .replace(/\r/g, "\\r")
               .replace(/\t/g, "\\t")
               .replace(/\f/g, "\\f");
};


function json_string_to_object(json_string) {
    return JSON.parse(escape_special_chars(json_string))
}


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

function get_consensus_classification_color(classification) {
    switch (classification) {
        case '5':
            base_color = class5ColorRGB
            break;
        case '4':
            base_color = class4ColorRGB
            break;
        case '3':
            base_color = class3ColorRGB
            break;
        case '2':
            base_color = class2ColorRGB
            break;
        case '1':
            base_color = class1ColorRGB
            break;
        default:
            base_color = noClassRGB
    }
    return base_color
}



$(document).ready(function(){
    // coloring of consensus classification
    document.getElementsByName('class-label').forEach(function(obj) {
        var consensus_classification = obj.getAttribute('classification').trim();
        var base_color = get_consensus_classification_color(consensus_classification)

        obj.setAttribute('style', 'color:'+base_color)

        //$('#class-label').css({'color': base_color});
    
        if (["1", "2", "3", "4", "5"].includes(consensus_classification)) {
            tooltip_text = "This variant has been classified by the VUS task-force with the class " + consensus_classification
        } else {
            tooltip_text = "This variant has not been classified by the VUS task-force yet."
        }
    
        obj.querySelector("#theC").setAttribute('title', tooltip_text);
    });


    
    document.getElementsByName('consensus_class_display').forEach(function(obj) {
        var consensus_classification = obj.getAttribute('classification').trim()
        var base_color = get_consensus_classification_color(consensus_classification)
        obj.setAttribute('style', 'background-color:'+base_color)
    })



});


