
var previous_obj = null;

function button_select_action(obj){
    obj.checked = ! obj.checked;

    save_criteria()

    const id = obj.id;
    const previous_evidence = obj.value;
    update_info_panel(id, previous_evidence)

    previous_obj = obj
}

function update_info_panel(id, previous_evidence) {
    //var criteria_container = document.getElementById('criteria_container')
    var criteria_title = document.getElementById('criteria_title')
    criteria_title.textContent = id.toUpperCase();
    document.getElementById('button_container').hidden = false;

    $('#select_criterium_button').popover('hide')

    var criteria_description_dom = document.getElementById('criteria_description')
    update_criteria_description(criteria_description_dom, id)
    var criteria_evidence_dom = document.getElementById('criteria_evidence')
    update_criteria_evidence_dom(criteria_evidence_dom, previous_evidence)
    var select_criterium_button = document.getElementById('select_criterium_button')
    update_select_criterium_button(select_criterium_button, id)
}

function save_criteria() {
    if (previous_obj != null) {
        previous_obj.value = document.getElementById('criteria_evidence').value
    }
}

function update_select_criterium_button(select_criterium_button, id) {
    select_criterium_button.value = id // save the criterium in button such that it knows which one to select on press
}

function update_criteria_evidence_dom(criteria_evidence_dom, previous_evidence) {
    criteria_evidence_dom.value = previous_evidence
}

$('#select_criterium_button').on('click', function(e){
    const criterium_to_select = $(this)[0].value;
    var criterium_to_select_dom = document.getElementById(criterium_to_select)
    if (document.getElementById('criteria_evidence').value.trim() == '' && !criterium_to_select_dom.checked) { 
        $(this).popover('show')
    } else { // only select criterium if there is evidence
        $(this).popover('hide')
        criterium_to_select_dom.checked = !criterium_to_select_dom.checked
        update_classification_preview()
    }
})

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

$('#submit-acmg-form').on('click', function(e){
    save_criteria() // this is important to save the last edited criteria. Otherwise the user needs to first select some other criterium to save the progress
})

function revert_criteria_container() {
    document.getElementById('criteria_title').textContent = "Please select a criterion";
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
    }
}

function revert_previous_obj() {
    previous_obj = null;
}

function preselect_from_previous_selection() {
    revert_criteria_container()
    revert_buttons()
    revert_previous_obj()
    const mask = document.getElementById('mask').value
    const current_mask_with_info = masks_with_info[mask]
    
    if (typeof current_mask_with_info !== "undefined") { // only preselect if there is data for it
        selected_criteria = current_mask_with_info['selected_criteria']
        for(var i = 0; i < selected_criteria.length; i++) {
            var current_data = selected_criteria[i];
            var current_criterium = current_data[2];
            var current_evidence = current_data[3];
            var selected_button = document.getElementById(current_criterium.toLowerCase());
            selected_button.value = current_evidence;
            selected_button.checked = true;
        }
    }
    update_classification_preview()
}
// call the function once to preselect on page load
preselect_from_previous_selection()



function preselect_from_data(){
    // TODO!!
}


// selected criteria is an array of criteria ids
function update_classification_preview() {
    var selected_criteria = get_currently_checked_criteria();
    selected_criteria = selected_criteria.join('+')
    fetch('/calculate_acmg_class?selected_classes='+selected_criteria).then(function (response) {
        return response.json();
    }).then(function (text) {
        const final_class = text.final_class
        document.getElementById('classification_preview').textContent = final_class
    });
}




function update_criteria_description(div, id) {
    //var criteria = ['pvs1', 'ps1', 'ps2', 'ps3', 'ps4', 'pm1', 'pm2', 'pm3', 'pm4', 'pm5', 'pm6', 'pp1', 'pp2', 'pp3', 'pp4', 'pp5', 'ba1', 'bs1', 'bs2', 'bs3', 'bs4', 'bp1', 'bp2', 'bp3', 'bp4', 'bp5', 'bp6', 'bp7']
    var text = ""
    if (id == "pvs1") {
        text = `Null variant (nonsense, frameshift, canonical +/-1 or 2 splice sites, initiation \
        codon, single or multi-exon deletion) in a gene where loss of function (LOF) \
        is a known mechanism of disease \r\n\
            Caveats: \r\n\
            - Beware of genes where LOF is not a known disease mechanism (e.g. GFAP, MYH7) \r\n\
            - Use caution interpreting LOF variants at the extreme 3' end of a gene \r\n\
            - Use caution with splice variants that are predicted to lead to exon skipping but leave the remainder of the protein intact \r\n\
            - Use caution in the presence of multiple transcripts`
    }
    
    if (id == "ps1") {
        text = `Same amino acid change as a previously established pathogenic variant \
        regardless of nucleotide change. \r\n\r\n\
            Example:	Val->Leu caused by either G>C or G>T in the same codon \r\n\
            Caveat:	Beware of changes that impact splicing rather than at the amino acid/protein level`
    } if (id == "ps2") {
        text = `De novo (both maternity and paternity confirmed) in a patient with the \
        disease and no family history. \r\n \r\n\
        Note: Confirmation of paternity only is insufficient. Egg donation, surrogate \
        motherhood, errors in embryo transfer, etc. can contribute to non-maternity.`
    } if (id == "ps3") {
        text = `Well-established in vitro or in vivo functional studies supportive of a \
        damaging effect on the gene or gene product. \r\n\r\n\
        Note: Functional studies that have been validated and shown to be \
        reproducible and robust in a clinical diagnostic laboratory setting are \
        considered the most well-established.`
    } if (id == "ps4") {
        text = "The prevalence of the variant in affected individuals is significantly \
        increased compared to the prevalence in controls. \r\n\r\n\
            Note 1: Relative risk (RR) or odds ratio (OR), as obtained from case-control \
        studies, is >5.0 and the confidence interval around the estimate of RR or OR \
        does not include 1.0. See manuscript for detailed guidance. \r\n\r\n\
            Note 2: In instances of very rare variants where case-control studies may \
        not reach statistical significance, the prior observation of the variant in \
        multiple unrelated patients with the same phenotype, and its absence in \
        controls, may be used as moderate level of evidence."
    }
    
    if (id == "pm1") {
        text = "Located in a mutational hot spot and/or critical and well-established \
        functional domain (e.g. active site of an enzyme) without benign variation."
    } if (id == "pm2") {
        text = "Absent from controls (or at extremely low frequency if recessive)\
        in Exome Sequencing Project, 1000 Genomes or ExAC. \r\n\r\n\
        Caveat: Population data for indels may be poorly called by next generation \
        sequencing."
    } if (id == "pm3") {
        text = "For recessive disorders, detected in trans with a pathogenic variant. \r\n\r\n \
        Note: This requires testing of parents (or offspring) to determine phase."
    } if (id == "pm4") {
        text = "Protein length changes due to in-frame deletions/insertions in a non-repeat \
        region or stop-loss variants."
    } if (id == "pm5") {
        text = "Novel missense change at an amino acid residue where a different \
        missense change determined to be pathogenic has been seen before. \r\n\r\n \
        Example: Arg156His is pathogenic; now you observe Arg156Cys. \r\n\
        Caveat: Beware of changes that impact splicing rather than at the amino \
        acid/protein level."
    } if (id == "pm6") {
        text = "Assumed de novo, but without confirmation of paternity and maternity."
    }
    
    if (id == "pp1") {
        text = "Co-segregation with disease in multiple affected family members in a gene \
        definitively known to cause the disease. \r\n\r\n\
        Note: May be used as stronger evidence with increasing segregation data."
    } if (id == "pp2") {
        text = "Missense variant in a gene that has a low rate of benign missense variation \
        and where missense variants are a common mechanism of disease."
    } if (id == "pp3") {
        text = "Multiple lines of computational evidence support a deleterious effect on \
        the gene or gene product (conservation, evolutionary, splicing impact, etc). \r\n\r\n\
        Caveat: As many in silico algorithms use the same or very similar input for \
        their predictions, each algorithm should not be counted as an independent \
        criterion. PP3 can be used only once in any evaluation of a variant."
    } if (id == "pp4") {
        text = "Patient's phenotype or family history is highly specific for a disease with a \
        single genetic etiology."
    } if (id == "pp5") {
        text = "Reputable source recently reports variant as pathogenic but the evidence is \
        not available to the laboratory to perform an independent evaluation."
    } 

    if (id == "ba1") {
        text = "Allele frequency is above 5% in Exome Sequencing Project, 1000 Genomes, \
        or ExAC."
    } 
    
    if (id == "bs1") {
        text = "Allele frequency is greater than expected for disorder."
    } if (id == "bs2") {
        text = "Observed in a healthy adult individual for a recessive (homozygous), \
        dominant (heterozygous), or X-linked (hemizygous) disorder with full \
        penetrance expected at an early age."
    } if (id == "bs3") {
        text = "Well-established in vitro or in vivo functional studies shows no damaging \
        effect on protein function or splicing."
    } if (id == "bs4") {
        text = "Lack of segregation in affected members of a family. \r\n\r\n\
        Caveat: The presence of phenocopies for common phenotypes (i.e. cancer, \
            epilepsy) can mimic lack of segregation among affected individuals. Also, \
            families may have more than one pathogenic variant contributing to an \
            autosomal dominant disorder, further confounding an apparent lack of \
            segregation."
    }
    
    if (id == "bp1") {
        text = "Missense variant in a gene for which primarily truncating variants are \
        known to cause disease"
    } if (id == "bp2") {
        text = "Observed in trans with a pathogenic variant for a fully penetrant dominant \
        gene/disorder; or observed in cis with a pathogenic variant in any \
        inheritance pattern."
    } if (id == "bp3") {
        text = "In-frame deletions/insertions in a repetitive region without a known \
        function"
    } if (id == "bp4") {
        text = "Multiple lines of computational evidence suggest no impact on gene or \
        gene product (conservation, evolutionary, splicing impact, etc) \r\n\r\n\
        Caveat: As many in silico algorithms use the same or very similar input for \
        their predictions, each algorithm cannot be counted as an independent \
        criterion. BP4 can be used only once in any evaluation of a variant."
    } if (id == "bp5") {
        text = "Variant found in a case with an alternate molecular basis for disease."
    } if (id == "bp6") {
        text = "Reputable source recently reports variant as benign but the evidence is not \
        available to the laboratory to perform an independent evaluation."
    } if (id == "bp7") {
        text = "A synonymous (silent) variant for which splicing prediction algorithms \
        predict no impact to the splice consensus sequence nor the creation of a \
        new splice site AND the nucleotide is not highly conserved."
    }
    div.textContent = text
}





var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
  return new bootstrap.Popover(popoverTriggerEl)
})
