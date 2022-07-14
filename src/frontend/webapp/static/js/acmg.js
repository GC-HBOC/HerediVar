
var previous_obj = null;
// add criteria_ids to this array if you want to enable strength select for it
const criteria_with_strength_selects = ['pp1', 'ps1', 'bp1']
// this dictionary contains the links for the reference articles of the acmg specifications (masks)
const reference_links = {
    'none': ' https://pubmed.ncbi.nlm.nih.gov/25741868/',
    'TP53': 'https://pubmed.ncbi.nlm.nih.gov/33300245/',
    'CDH1': 'https://pubmed.ncbi.nlm.nih.gov/30311375/',
    'task-force': '#'
}
// this dictionary contains all buttons which should be disabled if one if them is activated
// !! you need to add both directions for this to work properly
// SPECIFIC FOR TP53 spec: PS4 not applicable when BA1 or BS1 are present, PM1 disables pm5
const disable_groups = {
    // very strong pathogenic
    'pvs1': [],
    // strong pathogenic
    'ps1': [],
    'ps2': [],
    'ps3': [],
    'ps4': [],
    // moderate pathogenic
    'pm1': [],
    'pm2': [],
    'pm3': [],
    'pm4': [],
    'pm5': [],
    'pm6': [],
    // supporting pathogenic
    'pp1': ['bs4'],
    'pp2': [],
    'pp3': [],
    'pp4': [],
    'pp5': [],
    // supporting benign
    'bp1': [],
    'bp2': [],
    'bp3': [],
    'bp4': [],
    'bp5': [],
    'bp6': [],
    'bp7': [],
    // strong benign
    'bs1': [],
    'bs2': [],
    'bs3': [],
    'bs4': ['pp1'],
    // stand alone benign
    'BA1': []
}

// this dict contains the default strengths for each mask
const default_strengths = {
    'none': {
        // very strong pathogenic
        'pvs1': 'pvs',
        // strong pathogenic
        'ps1': 'ps', 'ps2': 'ps', 'ps3': 'ps', 'ps4': 'ps',
        // moderate pathogenic
        'pm1': 'pm', 'pm2': 'pm', 'pm3': 'pm', 'pm4': 'pm', 'pm5': 'pm', 'pm6': 'pm',
        // supporting pathogenic
        'pp1': 'pp', 'pp2': 'pp', 'pp3': 'pp', 'pp4': 'pp', 'pp5': 'pp',
        // supporting benign
        'bp1': 'bp', 'bp2': 'bp', 'bp3': 'bp', 'bp4': 'bp', 'bp5': 'bp', 'bp6': 'bp', 'bp7': 'bp',
        // strong benign
        'bs1': 'bs', 'bs2': 'bs', 'bs3': 'bs', 'bs4': 'bs',
        // stand alone benign
        'BA1': 'ba'
    },
    'TP53': {
        // very strong pathogenic
        'pvs1': 'pvs',
        // strong pathogenic
        'ps1': 'ps', 'ps2': 'ps', 'ps3': 'ps', 'ps4': 'ps',
        // moderate pathogenic
        'pm1': 'pm', 'pm2': 'pm', 'pm3': 'pm', 'pm4': 'pm', 'pm5': 'pm', 'pm6': 'pm',
        // supporting pathogenic
        'pp1': 'pp', 'pp2': 'pp', 'pp3': 'pp', 'pp4': 'pp', 'pp5': 'pp',
        // supporting benign
        'bp1': 'bp', 'bp2': 'bp', 'bp3': 'bp', 'bp4': 'bp', 'bp5': 'bp', 'bp6': 'bp', 'bp7': 'bp',
        // strong benign
        'bs1': 'bs', 'bs2': 'bs', 'bs3': 'bs', 'bs4': 'bs',
        // stand alone benign
        'BA1': 'ba'
    },
    'CDH1': {
        // very strong pathogenic
        'pvs1': 'pvs',
        // strong pathogenic
        'ps1': 'ps', 'ps2': 'ps', 'ps3': 'ps', 'ps4': 'ps',
        // moderate pathogenic
        'pm1': 'pm', 'pm2': 'pm', 'pm3': 'pm', 'pm4': 'pm', 'pm5': 'pm', 'pm6': 'pm',
        // supporting pathogenic
        'pp1': 'pp', 'pp2': 'pp', 'pp3': 'pp', 'pp4': 'pp', 'pp5': 'pp',
        // supporting benign
        'bp1': 'bp', 'bp2': 'bp', 'bp3': 'bp', 'bp4': 'bp', 'bp5': 'bp', 'bp6': 'bp', 'bp7': 'bp',
        // strong benign
        'bs1': 'bs', 'bs2': 'bs', 'bs3': 'bs', 'bs4': 'bs',
        // stand alone benign
        'BA1': 'ba'
    },
    'task-force': {
        // very strong pathogenic
        'pvs1': 'pvs',
        // strong pathogenic
        'ps1': 'ps', 'ps2': 'ps', 'ps3': 'ps', 'ps4': 'ps',
        // moderate pathogenic
        'pm1': 'pm', 'pm2': 'pm', 'pm3': 'pm', 'pm4': 'pm', 'pm5': 'pm', 'pm6': 'pm',
        // supporting pathogenic
        'pp1': 'pp', 'pp2': 'pp', 'pp3': 'pp', 'pp4': 'pp', 'pp5': 'pp',
        // supporting benign
        'bp1': 'bp', 'bp2': 'bp', 'bp3': 'bp', 'bp4': 'bp', 'bp5': 'bp', 'bp6': 'bp', 'bp7': 'bp',
        // strong benign
        'bs1': 'bs', 'bs2': 'bs', 'bs3': 'bs', 'bs4': 'bs',
        // stand alone benign
        'BA1': 'ba'
    }
}

// this dict contains all criteria which should be disabled for a specific mask
const not_activateable_buttons = {
    'none': [],
    'TP53': ['pm3', 'pm4', 'pp2', 'pp4', 'pp5', 'bp1', 'bp3', 'bp5', 'bp6'], // this is in disable group and if it is in not activateable buttons as well it will stay disabled: , 'bs4'
    'CDH1': [],
    'task-force': []
}

function button_select_action(obj){
    obj.checked = ! obj.checked;

    save_criteria()

    const id = obj.id;
    const previous_evidence = obj.value;
    update_info_panel(id, previous_evidence)

    previous_obj = obj
}

function update_info_panel(id, previous_evidence) {
    revert_criteria_container()
    //var criteria_container = document.getElementById('criteria_container')
    var criteria_title = document.getElementById('criteria_title')
    criteria_title.textContent = id.toUpperCase();
    document.getElementById('button_container').hidden = false;

    $('#select_criterium_check').popover('hide')
    document.getElementById('select_criterium_check').hidden = false;

    var criteria_description_dom = document.getElementById('criteria_description')
    update_criteria_description(criteria_description_dom, id)
    var criteria_evidence_dom = document.getElementById('criteria_evidence')
    update_criteria_evidence_dom(criteria_evidence_dom, previous_evidence)
    var select_criterium_button = document.getElementById('select_criterium_check')
    update_select_criterium_button(select_criterium_button, id)

    if (criteria_with_strength_selects.includes(id)) {
        add_strength_selection(id)
    }
}


function save_criteria() {
    if (previous_obj != null) {
        previous_obj.value = document.getElementById('criteria_evidence').value
    }
}

function update_select_criterium_button(select_criterium_button, id) {
    select_criterium_button.value = id // save the criterium in button such that it knows which one to select on press
    select_criterium_button.checked = document.getElementById(id).checked
}

function update_criteria_evidence_dom(criteria_evidence_dom, previous_evidence) {
    criteria_evidence_dom.value = previous_evidence
}

/*
$('#select_criterium_button').on('click', function(e){
    const criterium_id = $(this)[0].value;
    var criterium_to_select_dom = document.getElementById(criterium_id)
    if (document.getElementById('criteria_evidence').value.trim() == '' && !criterium_to_select_dom.checked) { 
        $(this).popover('show')
    } else { // only select criterium if there is evidence
        $(this).popover('hide')
        toggle_criterium(criterium_id)
        //criterium_to_select_dom.checked = !criterium_to_select_dom.checked
        update_classification_preview()
    }
})
*/

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

function update_criterium_button_background(criterium_id) {
    var criterium_button = document.getElementById(criterium_id);
    var criterium_strength_select = document.getElementById(criterium_id + '_strength');
    var criterium_label = document.getElementById(criterium_id + '_label');

    var outer_color = colors[criterium_strength_select.value];
    //var inner_color = colors[criterium_id.replace(/\d+/g,'')]

    if (!criterium_button.checked) {
        criterium_label.style['background-color'] = null
    } else {
        criterium_label.style['background-color'] = outer_color //"radial-gradient(circle, " + inner_color + " 50%, " + outer_color + " 100%)"
    }
}

const colors = load_colors() // this maps a criterium strength to a color
function load_colors() {
    const red = $('.btn-red').css('color')
    const orange = $('.btn-orange').css('color')
    const yellow = $('.btn-yellow').css('color')
    const green = $('.btn-green').css('color')
    const blue = $('.btn-blue').css('color')
    const purple = $('.btn-purple').css('color')
    const darkblue = $('.btn-darkblue').css('color')
    return {'pvs': red, 'ps': orange, 'pm': yellow, 'pp': green, 'bp': blue, 'bs': purple, 'ba': darkblue}
}

$('#submit-acmg-form').on('click', function(e){
    save_criteria() // this is important to save the last edited criteria. Otherwise the user needs to first select some other criterium to save the progress
})



function revert_criteria_container() {
    document.getElementById('criteria_title').textContent = "Please select a criterion";
    document.getElementById('select_criterium_check').checked = false;
    document.getElementById('select_criterium_check').hidden = true;
    document.getElementById('button_container').hidden = true;
    document.getElementById('criteria_description').textContent = "";
    document.getElementById('criteria_evidence').value = "";
    document.getElementById('additional_content').innerHTML = "";
}

function revert_buttons() {
    var all_buttons = document.querySelectorAll('.btn-check')
    for (var i = 0; i < all_buttons.length; i++) {
        var current_button = all_buttons[i];
        current_button.checked = false;
        current_button.value = ""
        current_button.setAttribute('activateable', 'true')
        current_button.disabled = false
        update_criterium_button_background(current_button.id)
    }
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

function revert_all() {
    //revert_strength_selects()
    revert_criteria_container()
    revert_buttons()
    revert_previous_obj()
}

function mask_select_action() {
    revert_all()
    const mask = document.getElementById('mask').value
    set_default_strengths(default_strengths[mask])
    preselect_from_previous_selection(mask)
    set_activatable_property(not_activateable_buttons[mask])
    enable_disable_buttons(not_activateable_buttons[mask], true)

    update_classification_preview()
    update_reference_link(mask)
    update_last_submitted_date(mask)
}

function update_reference_link(mask) {
    document.getElementById('mask_reference').setAttribute('href', reference_links[mask])
}

function update_last_submitted_date(mask) {
    var date = '-'
    const current_mask_with_info = masks_with_info[mask]
    if (typeof current_mask_with_info !== "undefined") { // only preselect if there is data for it
        date = current_mask_with_info['date']
    }
    document.getElementById('submitted_at_date').textContent = date
}


function set_activatable_property(criterium_ids) {
    for (var i = 0; i < criterium_ids.length; i++) {
        var criterium_id = criterium_ids[i];
        var current_criterium_button = document.getElementById(criterium_id)
        current_criterium_button.setAttribute('activateable', 'false')
    }
}

function set_default_strengths(strengths) {
    var all_strength_selects = document.querySelectorAll('[id$="_strength"]');
    for (var i = 0; i < all_strength_selects.length; i++) {
        var current_strength_select = all_strength_selects[i];
        var current_criterium_id = current_strength_select.id.replace('_strength', '');
        current_strength_select.setAttribute('default_strength', strengths[current_criterium_id])
        current_strength_select.value = current_strength_select.getAttribute('default_strength')
    }
}

function preselect_from_previous_selection(mask) {
    const current_mask_with_info = masks_with_info[mask]
    if (typeof current_mask_with_info !== "undefined") { // only preselect if there is data for it
        selected_criteria = current_mask_with_info['selected_criteria']
        for(var i = 0; i < selected_criteria.length; i++) {
            var current_data = selected_criteria[i];
            var current_criterium = current_data[2].toLowerCase();
            var current_evidence = current_data[4];
            var current_strength = current_data[3];

            var selected_button = document.getElementById(current_criterium);
            selected_button.value = current_evidence;
            set_criterium_strength(current_criterium, current_strength)
            set_criterium(current_criterium, true)
        }
    }
}
// call the function once to preselect on page load
mask_select_action()


function set_criterium_strength(criterium_id, strength) {
    document.getElementById(criterium_id + '_strength').value = strength;
}


function add_strength_selection(criterium_id) {
    var additional_content = document.getElementById('additional_content');
    if (criterium_id[0] === 'p') {
        additional_content.innerHTML = `
        <h5 class="bst">Strength:</h5>
        <div>
            <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" name="strength_select" id="pp_radio" value="pp" onclick="update_criterium_strength(this, '` + criterium_id + `')">
                <label class="form-check-label" for="pp_radio">supporting</label>
            </div>
            <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" name="strength_select" id="pm_radio" value="pm" onclick="update_criterium_strength(this, '` + criterium_id + `')">
                <label class="form-check-label" for="pm_radio">moderate</label>
            </div>
            <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" name="strength_select" id="ps_radio" value="ps" onclick="update_criterium_strength(this, '` + criterium_id + `')">
                <label class="form-check-label" for="ps_radio">strong</label>
            </div>
            <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" name="strength_select" id="pvs_radio" value="pvs" onclick="update_criterium_strength(this, '` + criterium_id + `')">
                <label class="form-check-label" for="pvs_radio">very strong</label>
            </div>
        </div>
        `
    } else {
        if (criterium_id[0] === 'b') {
            additional_content.innerHTML = `
            <h5 class="bst">Strength:</h5>
            <div>
                <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="strength_select" id="bp_radio" value="bp" onclick="update_criterium_strength(this, '` + criterium_id + `')">
                    <label class="form-check-label" for="bp_radio">supporting</label>
                </div>
                <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="strength_select" id="bs_radio" value="bs" onclick="update_criterium_strength(this, '` + criterium_id + `')">
                    <label class="form-check-label" for="bs_radio">strong</label>
                </div>
                <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="strength_select" id="ba_radio" value="ba" onclick="update_criterium_strength(this, '` + criterium_id + `')">
                    <label class="form-check-label" for="ba_radio">stand-alone</label>
                </div>
            </div>
            `
        }
    }


    // preselect
    const preselected_strength = document.getElementById(criterium_id + '_strength').value
    document.getElementById(preselected_strength + '_radio').checked = true

}


function update_criterium_strength(obj, criterium_id) {
    var strength_obj = document.getElementById(criterium_id + '_strength')
    strength_obj.value = obj.value
    update_classification_preview()
    update_criterium_button_background(criterium_id)
}


// select and unselect the criterium itself + its associated strength input check which holds information about its user-assigned strenght
function toggle_criterium(criterium_id) {
    var obj = document.getElementById(criterium_id)
    obj.checked = !obj.checked
    update_criterium_button_background(criterium_id)
    document.getElementById(criterium_id + '_strength').checked = obj.checked
    const current_disable_group = disable_groups[criterium_id]
    enable_disable_buttons(current_disable_group, obj.checked)
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

function set_criterium(criterium_id, is_checked) {
    var obj = document.getElementById(criterium_id)
    obj.checked = is_checked
    update_criterium_button_background(criterium_id)
    document.getElementById(criterium_id + '_strength').checked = obj.checked
    const current_disable_group = disable_groups[criterium_id]
    enable_disable_buttons(current_disable_group, obj.checked)
}


function preselect_from_data(){
    // TODO!!
}




function update_classification_preview() {
    var selected_criteria = get_currently_checked_criteria(); // this is an array of criteria ids
    selected_criteria = selected_criteria.join('+')
    fetch('/calculate_acmg_class?selected_classes='+selected_criteria).then(function (response) {
        return response.json();
    }).then(function (text) {
        const final_class = text.final_class
        document.getElementById('classification_preview').textContent = final_class
    });
}

function get_currently_checked_criteria() {
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





function update_criteria_description(div, id) {
    //var criteria = ['pvs1', 'ps1', 'ps2', 'ps3', 'ps4', 'pm1', 'pm2', 'pm3', 'pm4', 'pm5', 'pm6', 'pp1', 'pp2', 'pp3', 'pp4', 'pp5', 'ba1', 'bs1', 'bs2', 'bs3', 'bs4', 'bp1', 'bp2', 'bp3', 'bp4', 'bp5', 'bp6', 'bp7']
    const mask = document.getElementById('mask').value;
    var text = criteria_descriptions[mask][id]
    div.textContent = text
}


// this dictionary contains all criteria descriptions depending on mask 
const criteria_descriptions = {
    'none': {
        // very strong pathogenic
        "pvs1":
            `Null variant (nonsense, frameshift, canonical +/-1 or 2 splice sites, initiation \
            codon, single or multi-exon deletion) in a gene where loss of function (LOF) \
            is a known mechanism of disease \r\n\
                Caveats: \r\n\
                - Beware of genes where LOF is not a known disease mechanism (e.g. GFAP, MYH7) \r\n\
                - Use caution interpreting LOF variants at the extreme 3' end of a gene \r\n\
                - Use caution with splice variants that are predicted to lead to exon skipping but leave the remainder of the protein intact \r\n\
                - Use caution in the presence of multiple transcripts`,
        
        // strong pathogenic
        "ps1":
            `Same amino acid change as a previously established pathogenic variant \
            regardless of nucleotide change. \r\n\r\n\
                Example:	Val->Leu caused by either G>C or G>T in the same codon \r\n\
                Caveat:	Beware of changes that impact splicing rather than at the amino acid/protein level`,
        "ps2":
            `De novo (both maternity and paternity confirmed) in a patient with the \
            disease and no family history. \r\n \r\n\
            Note: Confirmation of paternity only is insufficient. Egg donation, surrogate \
            motherhood, errors in embryo transfer, etc. can contribute to non-maternity.`,
        "ps3":
            `Well-established in vitro or in vivo functional studies supportive of a \
            damaging effect on the gene or gene product. \r\n\r\n\
            Note: Functional studies that have been validated and shown to be \
            reproducible and robust in a clinical diagnostic laboratory setting are \
            considered the most well-established.`,
        "ps4":
            "The prevalence of the variant in affected individuals is significantly \
            increased compared to the prevalence in controls. \r\n\r\n\
                Note 1: Relative risk (RR) or odds ratio (OR), as obtained from case-control \
            studies, is >5.0 and the confidence interval around the estimate of RR or OR \
            does not include 1.0. See manuscript for detailed guidance. \r\n\r\n\
                Note 2: In instances of very rare variants where case-control studies may \
            not reach statistical significance, the prior observation of the variant in \
            multiple unrelated patients with the same phenotype, and its absence in \
            controls, may be used as moderate level of evidence.",
        
        // moderate pathogenic
        "pm1":
            "Located in a mutational hot spot and/or critical and well-established \
            functional domain (e.g. active site of an enzyme) without benign variation.",
        "pm2":
            "Absent from controls (or at extremely low frequency if recessive)\
            in Exome Sequencing Project, 1000 Genomes or ExAC. \r\n\r\n\
            Caveat: Population data for indels may be poorly called by next generation \
            sequencing.",
        "pm3":
            "For recessive disorders, detected in trans with a pathogenic variant. \r\n\r\n \
            Note: This requires testing of parents (or offspring) to determine phase.",
        "pm4":
            "Protein length changes due to in-frame deletions/insertions in a non-repeat \
            region or stop-loss variants.",
        "pm5":
            "Novel missense change at an amino acid residue where a different \
            missense change determined to be pathogenic has been seen before. \r\n\r\n \
            Example: Arg156His is pathogenic; now you observe Arg156Cys. \r\n\
            Caveat: Beware of changes that impact splicing rather than at the amino \
            acid/protein level.",
        "pm6":
            "Assumed de novo, but without confirmation of paternity and maternity.",
        
        // supporting pathogenic
        'pp1':
            "Co-segregation with disease in multiple affected family members in a gene \
            definitively known to cause the disease. \r\n\r\n\
            Note: May be used as stronger evidence with increasing segregation data.",
        "pp2":
            "Missense variant in a gene that has a low rate of benign missense variation \
            and where missense variants are a common mechanism of disease.",
        "pp3":
            "Multiple lines of computational evidence support a deleterious effect on \
            the gene or gene product (conservation, evolutionary, splicing impact, etc). \r\n\r\n\
            Caveat: As many in silico algorithms use the same or very similar input for \
            their predictions, each algorithm should not be counted as an independent \
            criterion. PP3 can be used only once in any evaluation of a variant.",
        "pp4":
            "Patient's phenotype or family history is highly specific for a disease with a \
            single genetic etiology.",
        "pp5":
            "Reputable source recently reports variant as pathogenic but the evidence is \
            not available to the laboratory to perform an independent evaluation.",
        
        // stand alone benign
        "ba1":
            "Allele frequency is above 5% in Exome Sequencing Project, 1000 Genomes, \
            or ExAC.",
        
        // strong benign
        "bs1":
            "Allele frequency is greater than expected for disorder.",
        "bs2":
            "Observed in a healthy adult individual for a recessive (homozygous), \
            dominant (heterozygous), or X-linked (hemizygous) disorder with full \
            penetrance expected at an early age.",
        "bs3":
            "Well-established in vitro or in vivo functional studies shows no damaging \
            effect on protein function or splicing.",
        "bs4":
            "Lack of segregation in affected members of a family. \r\n\r\n\
            Caveat: The presence of phenocopies for common phenotypes (i.e. cancer, \
                epilepsy) can mimic lack of segregation among affected individuals. Also, \
                families may have more than one pathogenic variant contributing to an \
                autosomal dominant disorder, further confounding an apparent lack of \
                segregation.",
        
        // supporting benign
        "bp1":
            "Missense variant in a gene for which primarily truncating variants are \
            known to cause disease",
        "bp2":
            "Observed in trans with a pathogenic variant for a fully penetrant dominant \
            gene/disorder; or observed in cis with a pathogenic variant in any \
            inheritance pattern.",
        "bp3":
            "In-frame deletions/insertions in a repetitive region without a known \
            function",
        "bp4":
            "Multiple lines of computational evidence suggest no impact on gene or \
            gene product (conservation, evolutionary, splicing impact, etc) \r\n\r\n\
            Caveat: As many in silico algorithms use the same or very similar input for \
            their predictions, each algorithm cannot be counted as an independent \
            criterion. BP4 can be used only once in any evaluation of a variant.",
        "bp5":
            "Variant found in a case with an alternate molecular basis for disease.",
        "bp6":
            "Reputable source recently reports variant as benign but the evidence is not \
            available to the laboratory to perform an independent evaluation.",
        "bp7":
            "A synonymous (silent) variant for which splicing prediction algorithms \
            predict no impact to the splice consensus sequence nor the creation of a \
            new splice site AND the nucleotide is not highly conserved."
    },
    'TP53': {
        // very strong pathogenic
        "pvs1":
            "Null variant (nonsense, frameshift, canonical ±1 or 2 splice sites, initiation codon,\
            single or multiexon deletion) in a gene where LOF is a known mechanism of disease \r\n\r\n\
            Use SVI-approved decision tree to determine the strength of this criterion\
            (refer to Abou Tayoun et al. for more details).",
        
        // strong pathogenic
        "ps1":
            "Same amino acid change as a previously established pathogenic variant \
            regardless of nucleotide change. \r\n\r\n\
            Use original description with the following additions: \r\n\
                PS1: \r\n\
                    - Must confirm there is no difference in splicing using RNA data. \r\n\
                    - Can only be used to compare to variants classified as Pathogenic or Likely Pathogenic by the \
                      TP53 VCEP (see ClinVar for VCEP classifications). \r\n\r\n\
                PS1_Moderate: \r\n\
                    - Must confirm there is no difference in splicing using a metapredictor. \r\n\
                    - Can only be used to compare to variants classified as Pathogenic or Likely Pathogenic by the TP53 VCEP (see ClinVar).",
        "ps2":
            "De novo (both maternity and paternity confirmed) in a patient with the \
            disease and no family history. \r\n\r\n\
            Use SVI-approved scoring system to determine the strength of this criterion \
            (refer to Table 2 from original publication: PMC8374922 (linked above) for more details)",
        "ps3":
            "Well-established in vitro or in vivo functional studies supportive of a \
            damaging effect on the gene or gene product. \r\n\r\n\
            The following additions have been made by the TP53 ACMG specification: \r\n\
                - PS3: transactivation assays in yeast demonstrate a low functioning allele \
                  (≤20% activity) AND there is evidence of dominant negative effect and loss-of-function \
                  OR there is a second assay showing low function (colony formation assays, apoptosis assays, \
                  tetramer assays, knock-in mouse models and growth suppression assays).\r\n\r\n\
                - PS3_Moderate: transactivation assays in yeast demonstrate a partially \
                  functioning allele (>20% and ≤75% activity) AND there is evidence of dominant \
                  negative effect and loss-of-function OR there is a second assay showing low function \
                  (colony formation assays, apoptosis assays, tetramer assays, knock-in mouse models and \
                  growth suppression assays).\r\n\r\n\
                - PS3_Moderate: there is no data available from transactivation assays in yeast BUT \
                  there is evidence of dominant negative effect and loss-of-function AND there is a second \
                  assay showing low function (colony formation assays, apoptosis assays, tetramer assays, \
                  knock-in mouse models and growth suppression assays).\r\n\r\n\
                ==> Refer to Figure 1 from original publication: PMC8374922 (linked above) for more details.",
        "ps4":
            "The prevalence of the variant in affected individuals is significantly \
            increased compared to the prevalence in controls. \r\n\r\n\
            Use SVI-approved scoring system to determine the strength of this criterion \
            (refer to Table 3 from original publication: PMC8374922 (linked above) for more details). \
            This criterion cannot be applied when a variant also meets BA1 or BS1. Refrain from considering \
            probands who have another pathogenic variant(s) in a highly penetrant cancer gene(s) that is a \
            logical cause for presentation. \r\n\r\n\
            Caveat: \r\n\
                Please be mindful of the risk of clonal hematopoieses of indeterminate potential with TP53 variants \
                (Coffee et al., 2017; Weitzel et al., 2017). One should take care to ensure that probands have \
                germline and not mosaic somatic TP53 variants.",
        
        // moderate pathogenic
        "pm1":
            "Located in a mutational hot spot and/or critical and well-established \
            functional domain (e.g. active site of an enzyme) without benign variation. \r\n\r\n\
            Located in a mutational hotspot defined as: \r\n\
                - Variants within the following codons on protein NP_000537.3: 175, 273, 245, 248, 282, 249. \r\n\
                - Variants seen in cancerhotspots.org (v2) with >10 somatic occurrences (recommendation from the ClinGen \
                  Germline/Somatic Variant Curation Subcommittee).",
        "pm2":
            "Absent from controls (or at extremely low frequency if recessive)\
            in Exome Sequencing Project, 1000 Genomes or ExAC. \r\n\r\n\
            Caveat: Population data for indels may be poorly called by next generation \
            sequencing. \r\n\r\n\
            PM2_Supporting: absent from population databases (gnomAD (most up-to-date non-cancer dataset) is the \
            preferred population database at this time http://gnomad.broadinstitute.org).",
        "pm3":
            "Excluded.",
        "pm4":
            "Excluded.",
        "pm5":
            "Novel missense change at an amino acid residue where a different \
            missense change determined to be pathogenic has been seen before. \r\n\r\n \
            Example: Arg156His is pathogenic; now you observe Arg156Cys. \r\n\r\n\
            PM5: novel missense change at an amino acid residue where at least two other different missense changes \
                determined to be pathogenic by the TP53 VCEP have been seen before. \
                PM5_Supporting: novel missense change at an amino acid residue where a different missense \
                change determined to be pathogenic by the TP53 VCEP has been seen before. \r\n\r\n\
            Both criteria require the following additions: \r\n\
                - Grantham should be used to compare the variants, and the variant being evaluated must have \
                  equal to or higher score than the observed pathogenic variants. \r\n\
                - Splicing should be ruled out using a metapredictor. \r\n\
                - This criterion cannot be applied when a variant also meets PM1.",
        "pm6":
            "Assumed de novo, but without confirmation of paternity and maternity. \r\n\r\n\
            Use SVI-approved scoring system to determine the strength of this criterion (refer to Table 2 from original \
            publication: PMC8374922 (linked above) for more details).",
        
        // supporting pathogenic
        'pp1':
            "Co-segregation with disease in multiple affected family members in a gene \
            definitively known to cause the disease. \r\n\r\n\
            PP1: co-segregation with disease is observed in 3–4 meioses in one family. \r\n\
            PP1_Moderate: co-segregation with disease is observed in 5–6 meioses in one family. \r\n\
            PP1_Strong: co-segregation with disease is observed >7 meioses in >1 family.",
        "pp2":
            "Excluded.",
        "pp3":
            "Multiple lines of computational evidence support a deleterious effect on \
            the gene or gene product (conservation, evolutionary, splicing impact, etc). \r\n\r\n\
            Caveat: As many in silico algorithms use the same or very similar input for \
            their predictions, each algorithm should not be counted as an independent \
            criterion. PP3 can be used only once in any evaluation of a variant. \r\n\r\n\
            PP3: Use original description with the following additions: \r\n\
                - For missense variants, use a combination of BayesDel (≥0.16) and optimised Align-GVGD (C55-C25). \r\n\
                - For splicing variants, use a metapredictor. \r\n\r\n\
            PP3_Moderate: for missense variants, use a combination of BayesDel (≥0.16) and optimized Align-GVGD (C65).",
        "pp4":
            "Excluded.",
        "pp5":
            "Excluded.",
        
        // stand alone benign
        "ba1":
            "Allele frequency is above 5% in Exome Sequencing Project, 1000 Genomes, \
            or ExAC.\r\n\r\n\
            Allele frequency is ≥0.1% in a non-founder population with a minimum of five alleles \
            (gnomAD (most up-to-date non-cancer dataset)) is the preferred population database \
            at this time http://gnomad.broadinstitute.org).",
        
        // strong benign
        "bs1":
            "Allele frequency is greater than expected for disorder. \r\n\r\n\
            Allele frequency is ≥0.03% and <0.1% in a non-founder population with a minimum of five alleles \
            (gnomAD (most up-to-date non-cancer dataset) is the preferred population database at this time \
            http://gnomad.broadinstitute.org).",
        "bs2":
            "Observed in a healthy adult individual for a recessive (homozygous), \
            dominant (heterozygous), or X-linked (hemizygous) disorder with full \
            penetrance expected at an early age.\r\n\r\n\
            BS2: observed in a single dataset in ≥8 females, who have reached at least 60 years of age without cancer \
                (i.e. cancer diagnoses after age 60 are ignored). \r\n\r\n\
            BS2_Supporting: observed in a single dataset in 2–7 females, who have reached at least 60 years of age without cancer. \r\n\r\n\
            Caveat: Be mindful of the risk of clonal hematopoiesis of indeterminate potential with TP53 variants (Coffee et al., 2017; Weitzel et al., 2017). \
                Individuals with mosaic somatic TP53 variants should not be included as evidence for BS2.",
        "bs3":
            "Well-established in vitro or in vivo functional studies shows no damaging \
            effect on protein function or splicing. \r\n\r\n\
            - BS3: transactivation assays in yeast demonstrate a functional allele or super-transactivation \
                (>75% activity) AND there is no evidence of dominant negative effect and loss-of-function OR \
                there is a second assay showing retained function (colony formation assays, apoptosis assays, \
                tetramer assays, knock-in mouse models and growth suppression assays). \r\n\r\n\
            - BS3_Supporting: transactivation assays in yeast demonstrate a partially functioning allele \
                (>20% and ≤75% activity) AND there is no evidence of dominant negative effect and loss-of-function \
                OR there is a second assay showing retained function (colony formation assays, apoptosis assays, \
                tetramer assays, knock-in mouse models and growth suppression assays). \r\n\r\n\
            - BS3_Supporting: there is no data available from transactivation assays in yeast BUT there is no \
                evidence of dominant negative effect and loss-of-function AND there is a second assay showing \
                retained function (colony formation assays, apoptosis assays, tetramer assays, knock-in mouse \
                models and growth suppression assays). \r\n\r\n\
            ==> Refer to Figure 1 from original publication: PMC8374922 (linked above) for more details.",
        "bs4":
            "Lack of segregation in affected members of a family. \r\n\r\n\
            The variant segregates to opposite side of the family meeting LFS criteria, or the variant is \
            present in >3 living unaffected individuals (at least two of three should be female) above 55 years of age.",
            
        // supporting benign
        "bp1":
            "Excluded",
        "bp2":
            "Observed in trans with a pathogenic variant for a fully penetrant dominant \
            gene/disorder; or observed in cis with a pathogenic variant in any \
            inheritance pattern. \r\n\r\n\
            Variant is observed in trans with a TP53 pathogenic variant (phase confirmed), \
            or there are three or more observations with a TP53 pathogenic variant when phase is unknown (at least two different \
            TP53 pathogenic variants). The other observed pathogenic variants must have been classified using \
            the TP53-specific guidelines.",
        "bp3":
            "Excluded",
        "bp4":
            "Multiple lines of computational evidence suggest no impact on gene or \
            gene product (conservation, evolutionary, splicing impact, etc) \r\n\r\n\
            Caveat: As many in silico algorithms use the same or very similar input for \
            their predictions, each algorithm cannot be counted as an independent \
            criterion. BP4 can be used only once in any evaluation of a variant. \r\n\r\n\
            Same rule description with the following additions: \r\n\
                - For missense variants, use a combination of BayesDel (<0.16) and optimized Align-GVGD (C15-C0). \r\n\
                - For splicing variants, use a metapredictor.",
        "bp5":
            "Excluded",
        "bp6":
            "Excluded",
        "bp7":
            "A synonymous (silent) variant for which splicing prediction algorithms \
            predict no impact to the splice consensus sequence nor the creation of a \
            new splice site AND the nucleotide is not highly conserved. \r\n\r\n\
            Same description with the following additions: \r\n\
                - Splicing should be ruled out using a metapredictor. \r\n\
                - If a new alternate site is predicted, compare strength to native site in interpretation."
    }
    
}

