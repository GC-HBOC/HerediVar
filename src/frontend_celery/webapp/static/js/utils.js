

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




function autocomplete(inp, id_container, arr) {
    /*the autocomplete function takes two arguments,
    the text field element and an array of possible autocompleted values:*/
    // the arr array should contain arrays of length 2 the first index containing an identifier
    // which is saved to the id container if it is selected and the other containing the display name
    var currentFocus;
    /*execute a function when someone writes in the text field:*/
    inp.addEventListener("input", function(e) {
        var a, b, i, val = this.value;
        /*remove id and add it again if we have a match*/
        id_container.value = '';
        for (var i = 0; i < arr.length; i++) {
            if (arr[i][1] == val) {
                id_container.value = arr[i][0];
            }
        }
        /*close any already open lists of autocompleted values*/
        closeAllLists();
        if (!val) { return false;}
        currentFocus = -1;
        /*create a DIV element that will contain the items (values):*/
        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");

        this.parentNode.appendChild(a);
        var total_displayed = 0;
        const max_displayed = 100;
        for (i = 0; i < arr.length; i++) {
            var element_id = arr[i][0]
            var element_name = arr[i][1]
            const match_index = element_name.toUpperCase().indexOf(val.toUpperCase())
            if (match_index !== -1 && total_displayed < max_displayed) {
                /*create a DIV element for each matching element:*/
                b = document.createElement("DIV");
                total_displayed += 1;
                /*make the matching letters bold:*/
                b.innerHTML = element_name.substr(0, match_index);
                b.innerHTML += "<strong>" + element_name.substr(match_index, val.length) + "</strong>";
                b.innerHTML += element_name.substr(match_index + val.length);
                b.setAttribute("data-element-name", element_name)
                b.setAttribute("data-element-id", element_id)
                /*execute a function when someone clicks on the item value (DIV element):*/
                b.addEventListener("click", function(e) {
                    /*insert the value for the autocomplete text field:*/
                    inp.value = this.getAttribute("data-element-name");
                    id_container.value = this.getAttribute("data-element-id");
                    closeAllLists();
                });
                a.appendChild(b);
            }
        }

        if (total_displayed >= max_displayed) {
            const cap = document.createElement("caption");
            cap.setAttribute('class', 'defaultrow');
            cap.textContent ='... more options available, but not shown';
            a.appendChild(cap);
        }
    });
    /*execute a function presses a key on the keyboard:*/
    inp.addEventListener("keydown", function(e) {
        var x = document.getElementById(this.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        if (e.keyCode == 40) {
            /*If the arrow DOWN key is pressed,
            increase the currentFocus variable:*/
            currentFocus++;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode == 38) { //up
            /*If the arrow UP key is pressed,
            decrease the currentFocus variable:*/
            currentFocus--;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode == 13) {
            /*If the ENTER key is pressed, prevent the form from being submitted,*/
            e.preventDefault();
            if (currentFocus > -1) {
              /*and simulate a click on the "active" item:*/
              if (x) x[currentFocus].click();
            }
        }
    });
    function addActive(x) {
        /*a function to classify an item as "active":*/
        if (!x) return false;
        /*start by removing the "active" class on all items:*/
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        /*add class "autocomplete-active":*/
        x[currentFocus].classList.add("autocomplete-active");
    }
    function removeActive(x) {
        /*a function to remove the "active" class from all autocomplete items:*/
        for (var i = 0; i < x.length; i++) {
            x[i].classList.remove("autocomplete-active");
        }
    }
    function closeAllLists(elmnt) {
        /*close all autocomplete lists in the document,
        except the one passed as an argument:*/
        var x = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != inp) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }
    /*execute a function when someone clicks in the document:*/
    document.addEventListener("click", function (e) {
        closeAllLists(e.target);
    });
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

///////////////////////////////////////////////////////////////
//////////////////////// create stuff /////////////////////////
///////////////////////////////////////////////////////////////

function create_trashcan() {


    var image = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    image.setAttribute("id", "delete-from-list-button")
    image.setAttribute("width", 17)
    image.setAttribute("height", 17)
    image.setAttribute("fill", "red")
    image.classList.add("bi")
    image.classList.add("bi-trash3")
    image.setAttribute("viewBox", "0 0 16 16")


    var path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", "M6.5 1h3a.5.5 0 0 1 .5.5v1H6v-1a.5.5 0 0 1 .5-.5ZM11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3A1.5 1.5 0 0 0 5 1.5v1H2.506a.58.58 0 0 0-.01 0H1.5a.5.5 0 0 0 0 1h.538l.853 10.66A2 2 0 0 0 4.885 16h6.23a2 2 0 0 0 1.994-1.84l.853-10.66h.538a.5.5 0 0 0 0-1h-.995a.59.59 0 0 0-.01 0H11Zm1.958 1-.846 10.58a1 1 0 0 1-.997.92h-6.23a1 1 0 0 1-.997-.92L3.042 3.5h9.916Zm-7.487 1a.5.5 0 0 1 .528.47l.5 8.5a.5.5 0 0 1-.998.06L5 5.03a.5.5 0 0 1 .47-.53Zm5.058 0a.5.5 0 0 1 .47.53l-.5 8.5a.5.5 0 1 1-.998-.06l.5-8.5a.5.5 0 0 1 .528-.47ZM8 4.5a.5.5 0 0 1 .5.5v8.5a.5.5 0 0 1-1 0V5a.5.5 0 0 1 .5-.5Z")
    image.appendChild(path)

    return image
}