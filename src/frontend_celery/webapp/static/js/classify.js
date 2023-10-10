///////////// field variables /////////////
const flask_data = document.getElementById('flask_data')



const logged_in_user_id = flask_data.dataset.loggedInUserId

const classification_schemas = JSON.parse(flask_data.dataset.classificationSchemas)

const previous_classifications = JSON.parse(flask_data.dataset.previousClassifications)
const variant_genes = flask_data.dataset.variantGenes;
const classification_type = flask_data.dataset.classificationType;
const request_form = JSON.parse(flask_data.dataset.requestForm)

const selected_pmids = JSON.parse(flask_data.dataset.selectedPmids) // this may be non empty if there were errors in the submission
const selected_text_passages = JSON.parse(flask_data.dataset.selectedTextPassages) // this may be non empty if there were errors in the submission



var previous_obj = null;
var colors; // this maps a criterium strength to a color which are defined in css
var scheme = document.getElementById('scheme').value // contains the currently selected scheme
var scheme_type = document.getElementById('scheme').getAttribute('scheme_type')

///////////// prepare data ////////////
//const schemes_with_info = json_string_to_object(schemes_with_info_string)
//const request_form = json_string_to_object(request_form_string)
var do_request_form_preselect = false
if (Object.keys(request_form).length > 0) {
    do_request_form_preselect = true
}



///////////// criterium buttons /////////////

function button_select_action(obj){
    obj.checked = ! obj.checked;

    save_criteria()

    const id = obj.id;
    const previous_evidence = obj.value;
    update_info_panel(id, previous_evidence)

    previous_obj = obj
}

function save_criteria() {
    if (previous_obj != null) {
        previous_obj.value = document.getElementById('criteria_evidence').value
    }
}

function update_info_panel(criterium_id, previous_evidence) {
    revert_criteria_container()
    //var criteria_container = document.getElementById('criteria_container')
    var criteria_title = document.getElementById('criteria_title')
    criteria_title.textContent = criterium_id.toUpperCase();
    document.getElementById('button_container').hidden = false;

    $('#select_criterium_check').popover('hide')
    document.getElementById('select_criterium_check').hidden = false;

    var criteria_description_dom = document.getElementById('criteria_description')
    update_criteria_description(criteria_description_dom, criterium_id)
    var criteria_evidence_dom = document.getElementById('criteria_evidence')
    update_criteria_evidence_dom(criteria_evidence_dom, previous_evidence)
    var select_criterium_button = document.getElementById('select_criterium_check')
    update_select_criterium_button(select_criterium_button, criterium_id)


    
    if (classification_type === 'consensus') {
        add_user_acmg_classification_details(criterium_id)
    }

    const current_criteria = classification_schemas[scheme]['criteria']
    if (criterium_id in current_criteria) {
        add_strength_selection(criterium_id, current_criteria[criterium_id]['possible_strengths'])
    }

    show_relevant_information(criterium_id)

}

function show_relevant_information(criterium_id) {
    var relevant_information = classification_schemas[scheme]['criteria'][criterium_id]['relevant_information']
    if (relevant_information != '') {
        relevant_information = relevant_information.split(';')
        for (var i = 0; i < relevant_information.length; i++) {
            document.getElementById(relevant_information[i] + '_info').classList.remove('visually-hidden')
        }
    }
}

function update_criteria_description(div, criterium_id) {
    var text = classification_schemas[scheme]['criteria'][criterium_id]['description']
    div.textContent = text
}

function update_criteria_evidence_dom(criteria_evidence_dom, previous_evidence) {
    criteria_evidence_dom.value = previous_evidence
}

function update_select_criterium_button(select_criterium_button, id) {
    select_criterium_button.value = id // save the criterium in button such that it knows which one to select on press
    select_criterium_button.checked = document.getElementById(id).checked
}

function criterium_strength_to_description(criterium_strength) {
    criterium_strength = criterium_strength.toLowerCase()
    if (criterium_strength == 'pvs') {
        return 'very strong'
    }
    if (criterium_strength == 'ps') {
        return 'strong'
    }
    if (criterium_strength == 'pm') {
        return 'medium'
    }
    if (criterium_strength == 'pp') {
        return 'supporting'
    }
    if (criterium_strength == 'bp') {
        return 'supporting'
    }
    if (criterium_strength == 'bm') {
        return "medium"
    }
    if (criterium_strength == 'bs') {
        return 'strong'
    }
    if (criterium_strength == 'ba') {
        return 'stand-alone'
    }
}


// this submits the classification(s)
function submit_classification() {
    // this is important to save the last edited criteria. Otherwise the user 
    // needs to first select some other criterium to save the progress
    save_criteria() 
}


///////////// preselect stuff ////////////


function preselect_literature() {
    // THIS FUNCTION IS UGLY --> maybe REWORK
    if (classification_type === 'consensus') { // remove all rows in add from user literature selection
        document.getElementById('user_text_passages_for_copy').innerHTML = ""
        update_default_caption(document.getElementById('userSelectedLiterature'))
    }
    for (var user_id in previous_classifications) {
        if (user_id != -1) { // skip imaginary consensus classification user id
            var all_user_classifications = previous_classifications[user_id]
            var selected_classification = all_user_classifications[scheme] ?? {}
            var previous_selected_literature = selected_classification['literature'] ?? []
            var submitter = selected_classification['submitter'] ?? {}
            var provided_by = submitter['full_name']
            var affiliation = submitter['affiliation']
            for (var i = 0; i < previous_selected_literature.length; i++) {
                var current_literature = previous_selected_literature[i]
                var pmid = current_literature['pmid']
                var text_passage = current_literature['text_passage']
                if (classification_type === 'consensus') { // add to modal table for copying
                    create_line_consensus_modal(document.getElementById('user_text_passages_for_copy'), pmid = pmid, evidence_text = text_passage, provided_by=provided_by, affiliation=affiliation)
                } else { // add directly to the literature select
                    create_literature_select(document.getElementById('selectedLiteratureList'), pmid = pmid, placeholder = "Text citation", evidence_text = text_passage)
                }
            }
        }
    }
    // add literature directly for consensus classification
    if (classification_type === 'consensus') {
        var all_user_classifications = previous_classifications[-1] ?? {}
        var selected_classification = all_user_classifications[scheme] ?? {}
        var previous_selected_literature = selected_classification['literature'] ?? []
        var submitter = selected_classification['submitter'] ?? {}
        var provided_by = submitter['full_name']
        var affiliation = submitter['affiliation']
        for (var i = 0; i < previous_selected_literature.length; i++) {
            var current_literature = previous_selected_literature[i]
            var pmid = current_literature['pmid']
            var text_passage = current_literature['text_passage']
            create_literature_select(document.getElementById('selectedLiteratureList'), pmid = pmid, placeholder = "Text citation", evidence_text = text_passage)
        }
    }

}


// call functions once on page load
function preselect_final_classification() {
    var comment_text_area = document.getElementById('comment')
    var final_class_select = document.getElementById('final_class')
    var warning_display = document.getElementById('warning_alert_previous_classification')
    if (classification_type === 'consensus') {
        var current_previous_classifications = previous_classifications[-1] ?? {}
    } else {
        var current_previous_classifications = previous_classifications[logged_in_user_id] ?? {}
    }
    if (scheme in current_previous_classifications){
        final_class_select.value = current_previous_classifications[scheme]['selected_class']
        comment_text_area.value = current_previous_classifications[scheme]['comment']
        comment_text_area.innerText = current_previous_classifications[scheme]['comment']
        warning_display.hidden = false
    } else {
        final_class_select.value = request_form['final_class'] || '3'
        comment_text_area.value = request_form['comment'] || ''
        comment_text_area.innerText = request_form['comment'] || ''
        warning_display.hidden = true
    }
}


function preselect_scheme() {
    var scheme_select = document.getElementById('scheme')
    const lower_case_variant_genes = variant_genes.toLowerCase().split(';') // convert all genes to lower case
    if (lower_case_variant_genes.includes('tp53')) {
        scheme_select.value = 3 //'acmg_TP53'
    } else if (lower_case_variant_genes.includes('cdh1')) {
        scheme_select.value = 4 //'acmg_CDH1'
    } else if (lower_case_variant_genes.includes('brca1') || lower_case_variant_genes.includes('brca2')) {
        scheme_select.value = 6 //'task-force-brca'
    } else {
        scheme_select.value = 2 //'acmg_standard'
    }
}

//Object.keys(request_form).length
function preselect_criteria_from_request_form() {
    for (var key in request_form) {
        if (key in classification_schemas[scheme]['criteria']) { // filter for criteria
            set_criterium(key, true)
            var current_evidence = request_form[key]
            document.getElementById(key).value = current_evidence

            var current_strength = request_form[key + '_strength']
            set_criterium_strength(key, current_strength)

            update_criterium_button_background(key)

        }
    }
    update_classification_preview()
}

function preselect_selected_literature() {
    selected_pmids.forEach(function (pmid, index) {
        var text_passage = selected_text_passages[index]
        create_literature_select(document.getElementById('selectedLiteratureList'), pmid = pmid, placeholder = "Text citation", evidence_text = text_passage)
    })
}



$(document).ready(function() {
    set_scheme_select_options()

    if (do_request_form_preselect) {
        document.getElementById('final_class').value = request_form['final_class']
        document.getElementById('comment').value = request_form['comment']
        // select scheme from request
        document.getElementById('scheme').value = request_form['scheme']
        update_scheme_field_variable()
    } else {
        preselect_scheme()
        update_scheme_field_variable()
        preselect_final_classification()
    }

    scheme_select_action(do_revert=!do_request_form_preselect)

    if (do_request_form_preselect) {
        preselect_criteria_from_request_form()
        preselect_selected_literature()
    }

    // fix for option href handling in edge, chrome (https://stackoverflow.com/questions/9972280/onclick-on-option-tag-not-working-on-ie-and-chrome)
    $("#classification_type").change(function (){
        const new_loc = $(this).find(":selected").attr("option-href");
        window.location = new_loc;
    });

    // set event listeners
    $('#scheme').change(function () {
        scheme_select_action();
    });
    $('#select_criterium_check').change(function () {
        select_criterium(this);
    });
    $('#blank_row_button').click(function () {
        create_literature_select(document.getElementById('selectedLiteratureList'));
    });
    $('#submit-acmg-form').click(function () {
        submit_classification();
    });
    $('#select_all_shown_papers_button').click(function() {
        select_all_non_hidden_papers(this.checked, 'literatureTable');
    });
    $('#add_selected_literature_button').click(function() {
        add_all_to_selected_literature('literatureTable', add_from_text_mining);
    });
    $('#select_all_shown_papers_button_user').click(function() {
        select_all_non_hidden_papers(this.checked, 'userSelectedLiterature');
    });
    $('#add_selected_literature_button_user').click(function() {
        add_all_to_selected_literature('userSelectedLiterature', add_from_user_selected);
    });

    add_default_for_important_information()
});


// this function adds a div such that missing or empty data fields
// dont just show the caption...
function add_default_for_important_information() {
    $('.important_information').each(function() {
        const actual_information_doms =$(this).find(":not(h5)")
        if (actual_information_doms.length == 0) {
            const default_empty = document.createElement('div')
            default_empty.innerText = "No information available"
            $(this).append(default_empty)
        }
    })
}

// update global scheme field variable
function update_scheme_field_variable() {
    scheme = $('#scheme').val()
    scheme_type = $("#scheme :selected").attr('scheme_type')
}

// call the function once to preselect on page load
// we need to wait until the document is ready to call the function because there is some jquery
// which will not be loaded if this function is called without the document ready!
function scheme_select_action(do_revert=true) {
    if (do_revert) {
        revert_all()
    }
    
    update_scheme_field_variable()


    if (scheme == 1) {
        $('#classification_schema_wrapper').collapse('hide');
        //classification_schema_wrapper_div.classList.remove('show')
    } else {
        $('#classification_schema_wrapper').collapse('show');
        create_criteria_buttons()
        colors = load_colors()
        set_default_strengths()
        set_activatable_property()
        
        if (do_revert) {
            preselect_criteria_from_database(scheme)
        }
        if (classification_type === 'consensus') {
            set_user_selection_counts(scheme)
        }
        
        update_classification_preview()
        update_reference_link(scheme)
        
    }
    preselect_final_classification()

    if (do_revert) {
        remove_all_selected_literature()
        preselect_literature()
    }

}

function set_user_selection_counts(scheme) {
    //console.log(scheme)
    for (var user_id in previous_classifications) {
        if (user_id != -1) { // exclude imaginary consensus classification user id
            var current_classifications = previous_classifications[user_id]
            var scheme_with_info = current_classifications[scheme] ?? {} // get an empty dict if the user does not have a user classification for this scheme
            var scheme_with_info = scheme_with_info['scheme'] ?? {} 
            var selected_criteria = scheme_with_info['criteria'] ?? [] // propagate the above
            for (var i in selected_criteria) {
                var criterium = selected_criteria[i]
                var criterium_id = criterium['name']
                var count_label = document.getElementById('users_selected_' + criterium_id)
                count_label.innerText = parseInt(count_label.innerText) + 1
                count_label.hidden = false;
            }
        }
    }
}

function set_default_strengths() {
    var all_strength_selects = document.querySelectorAll('[id$="_strength"]');
    for (var i = 0; i < all_strength_selects.length; i++) {
        var current_strength_select = all_strength_selects[i];
        var current_criterium_id = current_strength_select.id.replace('_strength', '');
        current_strength_select.setAttribute('default_strength', classification_schemas[scheme]['criteria'][current_criterium_id]['default_strength'])
        if (!Object.keys(request_form).includes(current_criterium_id) || request_form['scheme'] !== document.getElementById('scheme').value) {
            current_strength_select.value = current_strength_select.getAttribute('default_strength')
        }   
    }
}

function preselect_criteria_from_database(scheme) {
    //const user_id = Object.keys(previous_classifications)[0]
    if (classification_type === 'consensus') {
        var current_scheme_with_info = previous_classifications[-1] ?? {} // use imaginary consensus classification user id
        current_scheme_with_info = current_scheme_with_info[scheme]
    } else {
        var current_scheme_with_info = previous_classifications[logged_in_user_id][scheme]
    }
    if (typeof current_scheme_with_info !== "undefined") { // only preselect if there is data for it
        selected_criteria = current_scheme_with_info['scheme']['criteria']
        //console.log(selected_criteria)
        for(var i = 0; i < selected_criteria.length; i++) {
            var current_data = selected_criteria[i];
            var current_criterium = current_data['name'].toUpperCase();
            var current_evidence = current_data['evidence'];
            var current_strength = current_data['type'];

            var selected_button = document.getElementById(current_criterium);
            selected_button.value = current_evidence;
            set_criterium_strength(current_criterium, current_strength)
            set_criterium(current_criterium, true)
        }
    }
}

function set_activatable_property() {
    const criteria = classification_schemas[scheme]['criteria']
    for (const criterium_id in criteria) {
        const is_selectable = criteria[criterium_id]['is_selectable']
        var selectable = false
        if (is_selectable === 1) {
            selectable = true
        }
        var current_criterium_button = document.getElementById(criterium_id)
        current_criterium_button.setAttribute('activateable', selectable)
        
        enable_disable_buttons([criterium_id], !selectable)
    }
}

function update_reference_link(scheme) {
    document.getElementById('scheme_reference').setAttribute('href', classification_schemas[scheme]['reference'])
}


function set_scheme_select_options() {
    var scheme_select = document.getElementById('scheme')
    for (var key in classification_schemas) {
        create_select_option(scheme_select, key, classification_schemas[key]['description'], classification_schemas[key]['scheme_type'])
    }
}





///////////// revert state /////////////

function revert_criteria_container() {
    document.getElementById('criteria_title').textContent = "Please select a criterion";
    document.getElementById('select_criterium_check').checked = false;
    document.getElementById('select_criterium_check').hidden = true;
    document.getElementById('button_container').hidden = true;
    document.getElementById('criteria_description').textContent = "";
    document.getElementById('criteria_evidence').value = "";
    document.getElementById('additional_content').innerHTML = "";
    hide_all_information()
}

function hide_all_information() {
    $('.important_information').each(function() {
        this.classList.add('visually-hidden')
    })
}

function revert_strength_selects() {
    var all_buttons = document.querySelectorAll('.btn-check')
    for (var i = 0; i < all_buttons.length; i++) {
        var current_button_id = all_buttons[i].id;
        var current_strength_select = document.getElementById(current_button_id + '_strength')
        current_strength_select.value = current_strength_select.getAttribute('default_strength') // this extracts the default strength of the criterium
    }
}

function revert_previous_obj() {
    previous_obj = null;
}

function revert_count_labels() {
    var all_count_labels = document.querySelectorAll('.count_label')
    for (var i in all_count_labels) {
        var current_count_label = all_count_labels[i]
        current_count_label.innerText = '0'
        current_count_label.hidden = true
    }
}

function remove_buttons() {
    document.getElementById('pathogenic_criteria_container').innerHTML = null
    document.getElementById('benign_criteria_container').innerHTML = null
    document.getElementById('uncertain_criteria_container').innerHTML = null

    document.querySelector("#pathogenic_criteria_container").closest(".card").hidden = false
    document.querySelector("#benign_criteria_container").closest(".card").hidden = false
    document.querySelector("#uncertain_criteria_container").closest(".card").hidden = false
}

function revert_all() {
    //revert_strength_selects()
    revert_criteria_container()
    remove_buttons()
    revert_previous_obj()
    revert_count_labels()
}

function remove_all_selected_literature() {
    const selected_literature_container = document.getElementById('selectedLiteratureList')
    const selected_literature = selected_literature_container.getElementsByTagName('tr')
    const num_selected_literature = selected_literature.length
    // The problem here is: each time an element is removed it is also removed from the selected_literature array which alters the selected_literature.length
    // --> Not all elements are removed
    // The solution: the total number of selected literatures is saved in a const and the for loop iterates using that as reference
    // Since we know that removing the dom from the html page it also removes it from the array
    // we can just select the first element of that array and be okay.
    for (var i  = 0; i < num_selected_literature; i++) {
        var current_selected_literature = selected_literature[0]
        delete_selected_literature_row(current_selected_literature)
    }
}


//////////// create dom object functions ////////////

// create literature select 
function create_literature_select(parent, pmid="", placeholder="Text citation", text_passage="") {
    /*
        <tr>
            <td><input class="form-control" type="text" name="pmid"></td>
            <td><textarea class="form-control" style="height:0; width:100%" type="text" name="text_passage"></textarea></td>
            <td style="text-align:center;"><button class="btn btn-danger" type="button">-</button></td>
        </tr>
    */
    var tr = document.createElement('tr')
    parent.appendChild(tr)

    // the first column
    var pmid_td = document.createElement('td')
    tr.appendChild(pmid_td)
    var pmid_input = document.createElement('input')
    pmid_input.classList.add("form-control")
    pmid_input.setAttribute("type", "text")
    pmid_input.setAttribute("name", "pmid")
    pmid_input.setAttribute('value', pmid)
    pmid_input.setAttribute('placeholder', "pmid")
    pmid_td.appendChild(pmid_input)

    // the second column
    var text_passage_td = document.createElement('td')
    tr.appendChild(text_passage_td)
    var text_passage_textarea = document.createElement('textarea')
    text_passage_textarea.setAttribute('type', "text")
    text_passage_textarea.setAttribute('name', "text_passage")
    text_passage_textarea.classList.add("form-control")
    text_passage_textarea.classList.add("height_zero")
    text_passage_textarea.value = text_passage
    text_passage_textarea.setAttribute('placeholder', placeholder)
    text_passage_td.appendChild(text_passage_textarea)

    // the remove column
    var remove_td = document.createElement('td')
    tr.appendChild(remove_td)
    var delete_button = document.createElement('button')
    delete_button.classList.add("btn")
    delete_button.classList.add("btn-link")
    delete_button.classList.add("text_align_center")
    delete_button.setAttribute("type", "button")
    delete_button.addEventListener("click", function() {delete_selected_literature_row(this.closest('tr'))} );
    remove_td.appendChild(delete_button)
    var image = create_trashcan()
    delete_button.appendChild(image)
    
    remove_default_caption(document.getElementById('selectedLiterature'))
}


function create_line_consensus_modal(parent, pmid, evidence_text, provided_by, affiliation) {
    var  new_row = document.createElement('tr')
    parent.appendChild(new_row)

    //<td style="vertical-align: middle; text-align:center;"><input class="form-check-input selected_literature" type="checkbox"></input></td>
    var select_td = document.createElement('td')
    new_row.appendChild(select_td)
    var new_checkbox = document.createElement('input')
    new_checkbox.classList.add('form-check-input')
    new_checkbox.classList.add('selected_user_literature')
    new_checkbox.classList.add('vertical_align_middle')
    new_checkbox.classList.add('text_align_center')
    new_checkbox.setAttribute('type', 'checkbox')
    select_td.appendChild(new_checkbox)

    var provided_by_td = document.createElement('td')
    provided_by_td.innerText = provided_by
    new_row.appendChild(provided_by_td)

    var affiliation_td = document.createElement('td')
    affiliation_td.innerText = affiliation
    new_row.appendChild(affiliation_td)

    var pmid_td = document.createElement('td')
    pmid_td.innerText = pmid
    new_row.appendChild(pmid_td)

    var evidence_text_td = document.createElement('td')
    evidence_text_td.innerText = evidence_text
    new_row.appendChild(evidence_text_td)

    remove_default_caption(document.getElementById('userSelectedLiterature'))
}   


function delete_selected_literature_row(tr) {
    if (tr.closest('tbody').children.length == 1) {
        add_default_caption(tr.closest('table'))
    }
    tr.remove()
}



function add_all_to_selected_literature(tname, inner_func) {
    const tbody = document.getElementById(tname).getElementsByTagName('tbody')[0]
    var rows = tbody.getElementsByTagName('tr')
    for (var i = 0; i < rows.length; i++) {
        var current_row = rows[i]
        var current_tds = current_row.getElementsByTagName('td')
        var current_selected_check = current_tds[0].getElementsByTagName('input')[0]
        if (current_selected_check.checked) { // if was selected add a new row
            inner_func(current_tds)
            current_selected_check.checked = false
        }
    }
    $('.modal').modal('hide');
    $('.selected_literature').prop('checked', false);
}

function add_from_text_mining(current_tds) {
    var pmid = current_tds[5].getAttribute('data-pmid')
    var paper_title = current_tds[3].getAttribute('data-title')
    create_literature_select(document.getElementById('selectedLiteratureList'), pmid=pmid, placeholder="Paper title: " + paper_title)
    
}

function add_from_user_selected(current_tds) {
    var pmid = current_tds[3].innerText
    var text_passage = current_tds[4].innerText
    create_literature_select(document.getElementById('selectedLiteratureList'), pmid=pmid, placeholder="Text citation", text_passage=text_passage)
}

/*
function add_all_to_selected_literature_from_user_selected() {
    const tbody = document.getElementById('userSelectedLiterature').getElementsByTagName('tbody')[0]
    var rows = tbody.getElementsByTagName('tr')
    for (var i = 0; i < rows.length; i++) {
        var current_row = rows[i]
        var current_tds = current_row.getElementsByTagName('td')
        var current_selected_check = current_tds[0].getElementsByTagName('input')[0]
        if (current_selected_check.checked) { // if was selected add a new row
            var pmid = current_tds[3].innerText
            var text_passage = current_tds[4].innerText
            create_literature_select(document.getElementById('selectedLiteratureList'), pmid=pmid, placeholder="Text citation", text_passage=text_passage)
            current_selected_check.checked = false
        }
    }
    $('.modal').modal('hide');
    $('.selected_literature').prop('checked', false);
}
*/


function select_all_non_hidden_papers(check_or_not, table_id) {
    const tbody = document.getElementById(table_id).getElementsByTagName('tbody')[0]
    var rows = tbody.getElementsByTagName('tr')
    for (var i = 0; i < rows.length; i++) {
        var current_row = rows[i]
        if (current_row.getAttribute('style')) { // check that current row has the style attribute at all
            if (current_row.getAttribute('style').includes('display: none')) {
                continue
            }
        }
        var current_tds = current_row.getElementsByTagName('td')
        var current_selected_check = current_tds[0].getElementsByTagName('input')[0]
        current_selected_check.checked = check_or_not
    }
}



// creates the criteria buttons depending on mask
function create_criteria_buttons() {
    var pathogenic_criteria_container = document.getElementById('pathogenic_criteria_container')
    var benign_criteria_container = document.getElementById('benign_criteria_container')
    var uncertain_criteria_container = document.getElementById('uncertain_criteria_container')

    
    var last_criterium_type = '-'
    var container = document.createElement('div')
    const current_criteria = classification_schemas[scheme]['criteria']
    criteria_ids = Object.keys(current_criteria)
    
    criteria_ids = criteria_ids.sort(compare_criteria())

    for (const i in criteria_ids) {
        var criterium_id = criteria_ids[i]
        var current_criterium = current_criteria[criterium_id]
        var default_strength = current_criterium['default_strength']

        var criterium_type = criterium_id[0] // a task force criterium -> the type is determined by the first digit
        if (scheme_type === 'acmg' || scheme_type === 'acmg-enigma-brca1'|| scheme_type === 'acmg-enigma-brca2') {
            criterium_type = criterium_id.replace(/\d+/g, '') // an acmg criterium. The type is determined by the first two or three letters
        }

        if (last_criterium_type != criterium_type) {
            if (['B', '1', '2'].includes(last_criterium_type[0])) {
                benign_criteria_container.appendChild(container)
            } else if (['P', '4', '5'].includes(last_criterium_type[0])) {
                pathogenic_criteria_container.appendChild(container)
            } else if (container.hasChildNodes()) {
                uncertain_criteria_container.appendChild(container)
            }
            container = document.createElement('div')
            container.classList.add('ssr')
        }
        new_criterium_button = create_criterium_button(criterium_id, default_strength)
        container.appendChild(new_criterium_button)
        last_criterium_type = criterium_type
    }

    // add the last column of buttons
    if (['B', '1', '2'].includes(last_criterium_type[0])) {
        benign_criteria_container.appendChild(container)
    } else if (['P', '4', '5'].includes(last_criterium_type[0])) {
        pathogenic_criteria_container.appendChild(container)
    } else {
        uncertain_criteria_container.appendChild(container)
    }

    if (! pathogenic_criteria_container.hasChildNodes()) {
        document.querySelector("#pathogenic_criteria_container").closest(".card").hidden = true
    }
    if (! benign_criteria_container.hasChildNodes()) {
        document.querySelector("#benign_criteria_container").closest(".card").hidden = true
    }
    if (! uncertain_criteria_container.hasChildNodes()) {
        document.querySelector("#uncertain_criteria_container").closest(".card").hidden = true
    }

}


// sort helper
function compare_criteria() {
    return function(a, b) {
        if (scheme_type === 'acmg' || scheme_type === 'acmg-enigma-brca1' || scheme_type === 'acmg-enigma-brca2') {
            const criterium_order = {'PVS': 1, 'PS': 2, 'PM': 3, 'PP': 4, 'BP': 5, 'BS': 6, 'BA': 7}
            const a_letters = a.slice(0, -1)
            const a_crit_num = parseInt(a.slice(-1))
            const b_letters = b.slice(0, -1)
            const b_crit_num = parseInt(b.slice(-1))

            if (a_letters === b_letters) {
                return a_crit_num - b_crit_num
            }

            a_num = criterium_order[a_letters]
            b_num = criterium_order[b_letters]

            return a_num - b_num
        } 
        
        if (scheme_type === 'task-force') {

            const a_first_num = a[0]
            const b_first_num = b[0]

            if (a_first_num !== b_first_num) {
                return b_first_num - a_first_num
            }

            const a_second_num = a.slice(2)
            const b_second_num = b.slice(2)

            return a_second_num - b_second_num
            
        }
    }
}

// sort helper
function compare_strength() {
    return function(a, b) {
        const strength_order = {'PVS': 1, 'PS': 2, 'PM': 3, 'PP': 4, 'BP': 5, 'BM':6, 'BS': 7, 'BA': 8}
        a_num = strength_order[a]
        b_num = strength_order[b]
        
        return a_num - b_num
    }
}





function create_select_option(parent, value, display_text, scheme_type) {
    var new_option = document.createElement('option')
    new_option.setAttribute('value', value)
    new_option.setAttribute('scheme_type', scheme_type)
    new_option.innerText = display_text
    parent.appendChild(new_option)
}


function create_criterium_button(criterium_id, strength) {
    // this is what it should look like in html:
    `
    <div class="form-group">
        <div id="users_selected_pvs1" class="count_label" hidden>0</div>
        <input type="checkbox" class="btn-check" id="pvs1" name="pvs1" value="" strength-adjustable="true" autocomplete="off" onchange="button_select_action(this)">
        <label id="pvs1_label" class="btn btn-pvs light-hover acmg-button" for="pvs1">PVS1</label>
        <input type="checkbox" id="pvs1_strength" name="pvs1_strength" value="pvs" autocomplete="off" hidden>
    </div>
    `

    var container = document.createElement('div')
    container.classList.add("form-group")

    var count_label = document.createElement('div')
    count_label.id = "users_selected_" + criterium_id
    count_label.classList.add("count_label")
    count_label.hidden = true
    count_label.innerText = '0'
    container.appendChild(count_label)

    var the_button = document.createElement('input')
    the_button.setAttribute('type', 'checkbox')
    the_button.classList.add('btn-check')
    the_button.id = criterium_id
    the_button.name = criterium_id
    the_button.setAttribute('strength-adjustable', 'true')
    the_button.setAttribute('autocomplete', 'off')
    the_button.setAttribute('activateable', 'true')
    the_button.onchange = function() { button_select_action(this) }
    the_button.value = ''
    container.appendChild(the_button)

    var label = document.createElement('label')
    label.setAttribute('for', criterium_id)
    label.id = criterium_id + '_label'
    //label.classList.add('btn')
    label.classList.add('btn-'+strength)
    label.classList.add('light-hover')
    label.classList.add('acmg-button')
    label.classList.add('acmg-button-large')
    label.textContent = criterium_id
    container.appendChild(label)

    if (! criterium_id.toLowerCase().indexOf(strength.toLowerCase()) <= 0) {
        label.textContent += '_' + strength;
    }

    var strength_select = document.createElement('input')
    strength_select.setAttribute('type', 'checkbox')
    strength_select.id = criterium_id + '_strength'
    strength_select.name = criterium_id + '_strength'
    strength_select.value = strength
    strength_select.setAttribute('autocomplete', 'off')
    strength_select.hidden = true
    container.appendChild(strength_select)

    return container
}


// strength select radio buttons
function add_strength_selection(criterium_id, possible_strengths) {
    if (possible_strengths.length <= 1) {
        return
    }

    possible_strengths = possible_strengths.sort(compare_strength())

    var additional_content = document.getElementById('additional_content');
    const new_subcaption = create_subcaption('Strength:')
    additional_content.appendChild(new_subcaption)
    var container = document.createElement('div')
    for (var i in possible_strengths) {
        container.appendChild(create_strength_ratio(criterium_id, possible_strengths[i]))
    }
    additional_content.appendChild(container)

    // preselect
    const preselected_strength = document.getElementById(criterium_id + '_strength').value
    document.getElementById(preselected_strength + '_radio').checked = true
}


function create_strength_ratio(criterium_id, criterium_strength) {
    var container = document.createElement('div')
    container.classList.add('form-check')
    container.classList.add('form-check-inline')

    var radio = document.createElement('input')
    radio.classList.add('form-check-input')
    radio.type = 'radio'
    radio.name = 'strength_select'
    radio.id = criterium_strength + '_radio'
    radio.value = criterium_strength
    radio.onchange = function() {update_criterium_strength(this, criterium_id)}
    container.appendChild(radio)

    var label = document.createElement('label')
    label.classList.add('form-check-label')
    label.setAttribute('for', radio.id)
    label.innerText = criterium_strength_to_description(criterium_strength)
    container.appendChild(label)
    return container
}

function create_table_data(text) {
    var new_td = document.createElement('td')
    new_td.appendChild(document.createTextNode(text))
    return new_td
}

// consensus classification specific
function create_user_acmg_details_table() {
    var table_container = document.createElement('div')
    table_container.classList.add('table-responsive')
    table_container.classList.add('tableFixHead')

    var table = document.createElement('table')
    table.classList.add('table')
    table.classList.add('table-hover')
    table_container.appendChild(table)

    var header = document.createElement('thead')
    var header_row = document.createElement('tr')
    header_row.appendChild(create_sortable_header('User', 'width_small'))
    header_row.appendChild(create_sortable_header('Affiliation', 'width_small'))
    header_row.appendChild(create_sortable_header('Strength', 'width_small'))
    var evidence_header = create_sortable_header('Evidence')
    header_row.appendChild(evidence_header)
    header_row.appendChild(create_sortable_header('Date', 'width_small'))
    header_row.appendChild(create_non_sortable_header('Copy', 'width_minimal'))
    header.appendChild(header_row)
    table.appendChild(header)

    var body = document.createElement('tbody')
    body.id = "user_acmg_details"
    table.appendChild(body)
    return table_container
}

function create_non_sortable_header(text, width_class="") {
    var new_th = document.createElement('th')
    if (width_class !== "") {
        new_th.classList.add(width_class)
    }
    new_th.innerText = text
    return new_th
}

function create_sortable_header(text, width_class = "") {
    var new_th = document.createElement('th')
    if (width_class !== "") {
        new_th.classList.add(width_class)
    }
    
    var title = document.createElement('div')
    title.classList.add('sortable')
    title.innerText = text
    new_th.appendChild(title)

    var searchbar = document.createElement('input')
    searchbar.type = 'text'
    searchbar.classList.add('form-control')
    searchbar.classList.add('form-control-sm')
    searchbar.classList.add('column-filter')
    searchbar.classList.add('sst')
    searchbar.setAttribute('placeholder', 'search...')
    searchbar.setAttribute('autocomplete', 'off')
    new_th.appendChild(searchbar)
    return new_th
}

function create_subcaption(text) {
    var new_subcaption = document.createElement('h5')
    new_subcaption.appendChild(document.createTextNode(text))
    new_subcaption.classList.add('bst')
    return new_subcaption
}

// this returns one row of the user scheme table shown when making a consensus classification
function create_row_user_acmg_details(user, affiliation, strength, evidence, date) {
    var new_row = document.createElement('tr')
    new_row.appendChild(create_table_data(user))
    new_row.appendChild(create_table_data(affiliation))
    new_row.appendChild(create_table_data(criterium_strength_to_description(strength)))
    new_row.appendChild(create_table_data(evidence))
    new_row.appendChild(create_table_data(date))
    //new_row.appendChild(create_table_data('copy...')) // TODO
    var copy_evidence_td = document.createElement('td')
    copy_evidence_td.classList.add('text_align_center')
    var copy_evidence_text = document.createElement('div')
    // add the bootstrap icon
    copy_evidence_text.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-clipboard-plus" viewBox="0 0 16 16">
            <path fill-rule="evenodd" d="M8 7a.5.5 0 0 1 .5.5V9H10a.5.5 0 0 1 0 1H8.5v1.5a.5.5 0 0 1-1 0V10H6a.5.5 0 0 1 0-1h1.5V7.5A.5.5 0 0 1 8 7z"/>
            <path d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1h1v-1z"/>
            <path d="M9.5 1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-1a.5.5 0 0 1 .5-.5h3zm-3-1A1.5 1.5 0 0 0 5 1.5v1A1.5 1.5 0 0 0 6.5 4h3A1.5 1.5 0 0 0 11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3z"/>
        </svg>
    `
    copy_evidence_text.value = evidence
    copy_evidence_text.setAttribute('strength', strength)
    copy_evidence_text.onclick = function() {copy_evidence(this)}
    copy_evidence_text.classList.add('clickable')
    copy_evidence_td.appendChild(copy_evidence_text)
    new_row.appendChild(copy_evidence_td)
    return new_row
}

// functionality of the copy evidence 'buttons'
function copy_evidence(obj) {
    var evidence_input = document.getElementById('criteria_evidence')
    evidence_input.value = obj.value
    const strength_to_select = obj.getAttribute('strength')

    var radio_to_select = document.getElementById(strength_to_select + '_radio')
    if (radio_to_select != null) {
        radio_to_select.click()
    }
}

function add_user_acmg_classification_details(criterium_id) {
    var additional_content = document.getElementById('additional_content')
    const new_subcaption = create_subcaption("User selections:")
    additional_content.appendChild(new_subcaption)

    // add the table
    const tab = create_user_acmg_details_table()
    additional_content.appendChild(tab)
    for (var user_id in previous_classifications) {
        if (user_id != -1) { // ignore imaginary consensus classification user id
            var current_classification = previous_classifications[user_id][scheme]
            if (typeof current_classification !== 'undefined') {
                var user = current_classification['submitter']['full_name']
                var affiliation = current_classification['submitter']['affiliation']
                var current_date = current_classification['date']
                var selected_criteria = current_classification['scheme']['criteria']
                for (var i in selected_criteria) {
                    var criterium = selected_criteria[i]
                    var current_criterium_id = criterium['name']
                    var current_strength = criterium['type']
                    var current_evidence = criterium['evidence']
                    if (current_criterium_id === criterium_id) {
                        var new_row = create_row_user_acmg_details(user, affiliation, current_strength, current_evidence, current_date)
                        document.getElementById('user_acmg_details').appendChild(new_row)
                    }
                }
            }
        }


    }
    add_functionality_to_table()
}

// this stuff is usually called on page load but needs to be refreshed here because the table
// is generated from javascript and does not exist on page load!
function add_functionality_to_table() {
    // add default row to all empty tables
    $(".table").map(function() {
        var nrows = $(this).find("tbody").find("tr").length
        if (nrows === 0) {
            add_default_caption($(this).get(0))
        }
    });
    ////////// functionality for column filters in tables
    $(".column-filter").on("keyup", function() {
        var table = $(this).parents('table').get(0)
        filterTable_multiple_columns($(this).val(), table, true)
    });

    $('.sortable').click(function(e) {
        const table_id = '#' + $(this).parents('table').attr('id')
        table_sorter([$(this).parents('th').index()], table_id)
    });
}






///////////// helper functions /////////////

function select_criterium(obj) {
    const criterium_id = obj.value // this is the criterium which we want to select
    var criterium_to_select_dom = document.getElementById(criterium_id)
    if (document.getElementById('criteria_evidence').value.trim() == '' && !criterium_to_select_dom.checked) { 
        $('#' + obj.id).popover('show')
        obj.checked = false;
    } else { // only select criterium if there is evidence
        $('#' + obj.id).popover('hide')
        set_criterium(criterium_id, obj.checked)
        //criterium_to_select_dom.checked = !criterium_to_select_dom.checked
        update_classification_preview()
    }
}

function get_checked_criteria_strengths() {
    var result = []
    var all_buttons = document.querySelectorAll('.btn-check')
    for (var i = 0; i < all_buttons.length; i++) {
        var current_button = all_buttons[i];
        if (current_button.checked) {
            var new_value = document.getElementById(current_button.id + '_strength').value
            result.push(new_value)
        }
    }
    return result
}

function get_currently_checked_criteria() {
    var result = []
    var all_buttons = document.querySelectorAll('.btn-check')
    for (var i = 0; i < all_buttons.length; i++) {
        var current_button = all_buttons[i];
        if (current_button.checked) {
            result.push(current_button.id)
        }
    }
    return result
}

function load_colors() {
    const red = $('.btn-pvs').css('color')
    const orange = $('.btn-ps').css('color')
    const yellow = $('.btn-pm').css('color')
    const green = $('.btn-pp').css('color')
    const blue = $('.btn-bp').css('color')
    const purple = $('.btn-bs').css('color')
    const darkblue = $('.btn-ba').css('color')
    return {'pvs': red, 'ps': orange, 'pm': yellow, 'pp': green, 'bp': blue, 'bs': purple, 'ba': darkblue}
}

function enable_disable_buttons(criterium_ids, is_disable) {
    for (var i = 0; i < criterium_ids.length; i++) {
        var current_criterium_id = criterium_ids[i];
        var current_criterium_button = document.getElementById(current_criterium_id)
        // this is just a sanity check to make sure that the disabled buttons are not checked!
        if (current_criterium_button.checked) {
            set_criterium(current_criterium_id, false)
        }
        if (current_criterium_button.getAttribute('activateable') === 'true') {
            current_criterium_button.disabled = is_disable
        } else {
            current_criterium_button.disabled = true
        }
    }
}

function update_classification_preview() {
    if (scheme_type == 'task-force') {
        var selected_criteria = get_currently_checked_criteria(); // this is an array of critera ids
    } else {
        var selected_criteria = get_checked_criteria_strengths(); // this is an array of criteria strengths
        
    }
    selected_criteria = selected_criteria.join('+')
    fetch('/calculate_class/'+scheme_type+'/'+selected_criteria).then(function (response) {
        return response.json();
    }).then(function (text) {
        const final_class = text.final_class
        document.getElementById('classification_preview').textContent = final_class
        if (classification_type === "consensus") {
            var pc = previous_classifications[-1] ?? {} // use imaginary consensus classification user id
        } else {
            var pc = previous_classifications[logged_in_user_id] ?? {}
        }
        if (!(scheme in pc) && !do_request_form_preselect) {
            document.getElementById('final_class').value = final_class
        }
        
    });
}

function update_criterium_button_background(criterium_id) {
    //var criterium_button = document.getElementById(criterium_id);
    var criterium_strength_select = document.getElementById(criterium_id + '_strength');
    var criterium_label = document.getElementById(criterium_id + '_label');

    //var outer_color = colors[criterium_strength_select.value];
    //var inner_color = colors[criterium_id.replace(/\d+/g,'')]

    var new_class = "btn-" + criterium_strength_select.value

    const current_classes = criterium_label.classList
    for (var i = 0; i < current_classes.length; i++) {
        var current_class = current_classes[i]
        if (current_class.indexOf("btn-") >= 0) {
            criterium_label.classList.remove(current_class)
        }
    }
    criterium_label.classList.add(new_class)

    //if (!criterium_button.checked) {
    //    criterium_label.style['background-color'] = null
    //} else {
    //    criterium_label.style['background-color'] = outer_color //"radial-gradient(circle, " + inner_color + " 50%, " + outer_color + " 100%)"
    //}
}

function update_criterium_button_label(criterium_id) {
    var criterium_strength_select = document.getElementById(criterium_id + '_strength');
    var criterium_button_label = document.getElementById(criterium_id + '_label');

    if (criterium_strength_select.getAttribute('default_strength') != criterium_strength_select.value) {
        criterium_button_label.innerText = criterium_id + '_' + criterium_strength_select.value
    } else {
        criterium_button_label.innerText = criterium_id
    }
}

// select and unselect the criterium itself + its associated strength input check which holds information about its user-assigned strenght
function toggle_criterium(criterium_id) {
    var obj = document.getElementById(criterium_id)
    obj.checked = !obj.checked
    update_criterium_button_background(criterium_id)
    document.getElementById(criterium_id + '_strength').checked = obj.checked
    const current_disable_group = classification_schemas[scheme]['criteria'][criterium_id]['mutually_exclusive_criteria']
    enable_disable_buttons(current_disable_group, obj.checked)
}

function set_criterium(criterium_id, is_checked) {
    var obj = document.getElementById(criterium_id)
    obj.checked = is_checked
    update_criterium_button_background(criterium_id)
    update_criterium_button_label(criterium_id)
    document.getElementById(criterium_id + '_strength').checked = obj.checked
    const current_disable_group = classification_schemas[scheme]['criteria'][criterium_id]['mutually_exclusive_criteria']
    enable_disable_buttons(current_disable_group, obj.checked)
}

function set_criterium_strength(criterium_id, strength) {
    document.getElementById(criterium_id + '_strength').value = strength;
}

function update_criterium_strength(obj, criterium_id) {
    var strength_obj = document.getElementById(criterium_id + '_strength')
    strength_obj.value = obj.value
    update_classification_preview()
    update_criterium_button_background(criterium_id)
    update_criterium_button_label(criterium_id)
}


//
//function update_schemes_with_info() {
//
//    var currently_checked_criteria = get_currently_checked_criteria()
//    var new_selection = []
//    for (var i in currently_checked_criteria) {
//        var criterium_id = currently_checked_criteria[i]
//        var current_evidence = document.getElementById(criterium_id).value
//        var current_strength = document.getElementById(criterium_id + '_strength').value
//        new_selection.push([-1,-1,criterium_id, current_strength, current_evidence])
//    }
//    schemes_with_info['selected'][scheme] = {'selected_criteria': new_selection}
//}
//











function preselect_from_data(){
    // TODO!!
}


