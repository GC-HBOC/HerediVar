

//////////////////////////////////////////////////////////////
////////////////// activating functionality //////////////////
//////////////////////////////////////////////////////////////

$(document).ready(function()
{
    // form validation
    // listens on the class validationreq
    $(".validationreq").focus(function(){
        $(this).parent().removeClass("was-validated");
    });
    $(".validationreq").blur(function(){
        if ($(this).attr('type') !== 'checkbox'){ // do not show validation colors for checkboxes as they should be fine no matter what you tick!
            $(this).parent().addClass("was-validated");
            $(".form-control:valid").parent().removeClass("was-validated");
        }
    });

    // add default row to all empty tables
    $(".table").map(function() {
        var nrows = $(this).find("tbody").find("tr").length
        if (nrows === 0) {
            add_default_caption($(this).get(0))
        }
    });

    // activate bootstrap tooltips
    $("body").tooltip({ selector: '[data-bs-toggle=tooltip]' });
    $('.large-tt').tooltip({
        template: '<div class="tooltip" role="tooltip"><div class="tooltip-arrow"></div><div class="tooltip-inner large"></div></div>'
    });

    // activate bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
      return new bootstrap.Popover(popoverTriggerEl)
    })
    
    // activate table column sorting on click
    $('.sortable').click(function(e) {
        const table_id = '#' + $(this).parents('table').attr('id')
        table_sorter([$(this).parents('th').index()], table_id)
    });

    // functionality for column filters in tables
    $(".column-filter").on("keyup", function() {
        var table = $(this).parents('table').get(0)
        //var index = $(this).parents('th').index()
        filterTable_multiple_columns($(this).val(), table, true)
    });

    // activate links on EVERY object
    $("*[data-href]").click(function(event) {
        switch (event.which) {
            case 1: // left mouse button
                window.location = $(this).data("href"); // open link in same tab
                break;
            case 3: // right mouse button
                // nothing rn
                break;
        }
    });

    // activate middle mouse button links
    // mousedown is preferred here because middle mouse button also triggers
    // fast scrolling on mousedown
    $("*[data-href]").mousedown(function(event) {
        switch (event.which) {
            case 2: // middle mouse button
                window.open($(this).data("href")); // open in new tab
                break;
        }
    });

    //$('.wide-tooltip').find('.tooltip-inner').addClass('.wide-inner-tooltip')

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
    });
});





////////////////////////////////////////////////////////////////
////////////////// filter table functionality //////////////////
////////////////////////////////////////////////////////////////

// filter table by only one column specified by the 'col' argument
// this is mainly used for splitting tables visually
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
    
        tds = tr[i].getElementsByTagName("td");
        if (col <= tds.length && col >= 0) {
            cell = tds[col];
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


// looks at all columns & extracts the values of the search inputs (if there are any)
// also highlights the inputs which currently have a value
// then first hides a row and if it satisfies all filters it shows it again
function filterTable_multiple_columns(filter, table, filter_visible = false) {
    filter = filter.toUpperCase();
    var tr = table.getElementsByTagName("tr");

    th = table.getElementsByTagName("th");
    all_filters = []
    for (i = 0; i < th.length; i++) {
        current_th = th[i]
        current_search_inputs = current_th.getElementsByTagName("input")
        if (current_search_inputs.length > 0) {
            current_search_input = current_search_inputs[0]
            current_filter = current_search_input.value.toUpperCase()
            if (current_filter != '') {
                new_data = [i, current_filter]
                all_filters.push(new_data)
                current_search_input.classList.add('search-input-selected')
            } else {
                current_search_input.classList.remove('search-input-selected')
            }
        }
    }

    remove_default_caption(table);
    displayed = 0;
    for (i = 1; i < tr.length; i++) { // loop over rows
        tr[i].style.display = "none"; // hide row
        if (!filter_visible) {
            tr[i].setAttribute('is-visible', 'false')
        }
    
        var tds = tr[i].getElementsByTagName("td");
        var num_matching = 0;
        for (var j=0; j < all_filters.length; j++) {
            var current_filter = all_filters[j][1]
            var current_col = all_filters[j][0]
            if (current_col <= tds.length && current_col >= 0) {
                var cell = tds[current_col];
                if (cell) {
                    if (cell.innerText.toUpperCase().indexOf(current_filter) > -1) {
                        num_matching += 1;
                    }
                }
            }
        }

        if (num_matching == all_filters.length) { // show row
            if (!filter_visible) {
                tr[i].setAttribute('is-visible', 'true')
            }
            if (tr[i].getAttribute('is-visible') == 'true' || !tr[i].hasAttribute('is-visible')) {
                tr[i].style.display = "";
                displayed += 1
            }
        }

    }

    if (displayed == 0) {
        add_default_caption(table)
    }
}

// adding a row if the filters removed all rows ie. the table is empty
function add_default_caption(table) {
    const cap = document.createElement("caption");
    cap.setAttribute('class', 'defaultrow');
    cap.textContent ='Nothing to show';
    table.appendChild(cap);
}

// removing the empty-table-row
function remove_default_caption(table) {
    var caps = table.getElementsByClassName('defaultrow');
    while(caps[0]) {
        caps[0].parentNode.removeChild(caps[0]);
    }
}



//////////////////////////////////////////////////////////////
////////////////// sort table functionality //////////////////
//////////////////////////////////////////////////////////////

// used for sorting of table columns
// colids can either be actual ids or the index of the column in the table
function table_sorter(colids, table_id){
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

// removes the direction arrow indicating how the table is sorted
// listens on the css class 'ascending'
function remove_sort_direction_arrows(table_id) {
    if (table_id[0] !== '#') {
        table_id = '#' + table_id
    }
    $(table_id).find('.sortable[ascending]').removeAttr('ascending')
}

// this updates the object attribute 'asc'
// adds the 'asc' attribute if the object does not yet have one
// flips the attribute if it is already there
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

// used for table sorting in ascending or descending order
// depends on the object attribute 'asc'
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
        return valA - valB // sort numerically
    } else {
        return valA.toString().localeCompare(valB) // sort alphabetically
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




///////////////////////////////////////////////////////////////
////////////////// further utility funcitons //////////////////
///////////////////////////////////////////////////////////////


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

//var class1ColorHEX = "#3cd23c"
//var class1ColorRGB = "rgba(60,210,60,1)"
//
//var class2ColorHEX = "95e900"
//var class2ColorRGB = "rgba(149,233,0,1)"
//
//var class3ColorHEX = "#1db5cf"
//var class3ColorRGB = "rgba(29, 181, 207, 1)"
//
//var class4ColorHEX = "#ff8e3d"
//var class4ColorRGB = "rgba(255,142,61,1)"
//
//var class5ColorHEX = "#f04935"
//var class5ColorRGB = "rgba(240,73,53,1)"
//
//var noClassHEX = "#a4a4a4"
//var noClassRGB = "rgb(164, 164, 164)"


function get_consensus_classification_color(classification) {
    switch (classification) {
        case '5':
            base_color = "rgba(240,73,53,1)" // hex: #f04935
            break;
        case '4':
            base_color = "rgba(255,142,61,1)" // hex: #ff8e3d
            break;
        case '3':
            base_color = "rgba(29, 181, 207, 1)" // hex: #1db5cf
            break;
        case '2':
            base_color = "rgba(149,233,0,1)" // hex: #95e900
            break;
        case '1':
            base_color = "rgba(60,210,60,1)" // hex: #3cd23c
            break;
        default:
            base_color = "rgb(164, 164, 164)" // hex: #a4a4a4
    }
    return base_color
}



