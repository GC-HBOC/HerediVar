import igv from "/static/packages/igv/igv.esm.js"
//import igv from "https://cdn.jsdelivr.net/npm/igv@2.15.0/dist/igv.esm.min.js"

//////////////////////////////////////////////////////////////
////////////////// activating functionality //////////////////
//////////////////////////////////////////////////////////////

$(document).ready(function()
{
    //// presort the tables on page load

    table_sorter(['#userClassificationsTableDateCol'], '#userClassificationsTable')
    table_sorter(['#clinvarSubmissionsTableLastEvaluatedCol'], '#clinvarSubmissionsTable')
    table_sorter(['#heredicareCenterClassificationsTableDateCol'], '#heredicareCenterClassificationsTable')
    table_sorter(['#userSchemeClassificationsTableDateCol'], '#userSchemeClassificationsTable')
    table_sorter(['#assayTableDateCol', '#assayTableAssayTypeCol'], '#assayTable')
    //table_sorter(['#literatureTableYearCol'], '#literatureTable')

    	
    activate_datatables("literatureTable");

    // functionality for the hide variant button
    $('#change_hidden_state').click(function() {
        $.ajax({
            type: 'POST',
            url: this.getAttribute('url'),
            success: function(data, status, request) {
                if (data === 'True') {
                    const hidden_pill = create_hidden_pill()
                    document.getElementById('annotation_status_pills').appendChild(hidden_pill)
                    document.getElementById('change_hidden_state').innerText = "Unhide variant"
                } else {
                    document.getElementById('hidden_pill').remove()
                    document.getElementById('change_hidden_state').innerText = "Hide variant"
                }
                
            },
            error: function() {
                console.log('error')
            }
        });
    })


    // functionality for the reannotate button
    $('#reannotate-submit').click(function(){
        $('#reannotate_button').attr('disabled', true);
        $('#reannotate-modal').modal('toggle');
        confirm_reannotation_action();
    });

    // functionality for the reload page modal
    $('#reload-submit').click(function() {
        location.reload()
    })

    // functionality to add a variant to a user-list
    $('.variant-list-button').click(function() {
        const form_to_submit = $('#add-to-list-form')
        form_to_submit.attr('action', $(this).attr('action'))
    });

    // set the title of the page
    //var variant_page_title_obj = document.getElementById('variant_page_title')
    //var title = variant_page_title_obj.innerText
    //const chrom = variant_page_title_obj.getAttribute('chrom')
    //const pos = parseInt(variant_page_title_obj.getAttribute('pos'))
    //const ref = variant_page_title_obj.getAttribute('ref')
    //const alt = variant_page_title_obj.getAttribute('alt')
    //title = get_variant_type(ref, alt) + title
    //variant_page_title_obj.innerText = title

    // functionality for the annotation status
    // this is blocking I think so it should be called last!
    var annotation_status = $('#annotation_status').data()['annotationStatus'];
    var celery_task_id = $('#annotation_status').data()['celeryTaskId'];
    if ((annotation_status === 'pending' || annotation_status == 'retry') && celery_task_id !== null){
        $('#reannotate_button').attr('disabled', true)
        //$('#reannotate-list-item').attr('title', "Wait for the current annotation to finish before submitting another one")
        const status_url = "/task/annotation_status/" + celery_task_id;
        //console.log(status_url)
        update_annotation_status(status_url);
    }


    $('#igv-tab').one('show.bs.tab', function() { // gets called only the first time you switch to the igv tab
        const variant_page_title_obj = document.getElementById('variant_page_title')
        const chrom = variant_page_title_obj.getAttribute('chrom')
        const pos = parseInt(variant_page_title_obj.getAttribute('pos'))
        setup_igv(chrom, pos-100, pos+100, $('#variant_id_container').data()['variantId'])
    })
    


});




///////////////////////////////////////////////////////////////////////
////////////////// reannotation button functionality //////////////////
///////////////////////////////////////////////////////////////////////

// function triggered on reannotaiton submit button pressed
function confirm_reannotation_action() {
    // send ajax POST request to start background job
    const variant_id = $('#variant_id_container').data()['variantId'];
    $.ajax({
        type: 'POST',
        url: '/task/run_annotation_service?variant_id=' + variant_id,
        success: function(data, status, request) {
            show_annotation_status('bg-secondary', "Annotation requested successfully", "Annotation requested")

            const status_url = request.getResponseHeader('annotation_status_url');
            update_annotation_status(status_url);
        },
        error: function() {
            show_annotation_status("bg-danger", "The variant could not be annotated. Either the service is unreachable or some other unexpected exception occured. You can try to reload this page or issue another annotation to fix this. If that does not help try again later.", "Internal error")
            $('#reannotate_button').attr('disabled', false)
        }
    });
}


// polling & status display update
function update_annotation_status(status_url) {
    // send GET request to status URL (defined by flask)
    $.getJSON(status_url, function(data) {
        console.log(data)
        if (data['state'] == 'PENDING') {
            show_annotation_status("bg-secondary", "Annotation is queued. This annotation job is waiting for other jobs to finish first.", "Annotation queued")
        } else if (data['state'] == 'PROGRESS') {
            show_annotation_status("bg-primary", "Annotation is being processed in the background. Please wait for it to finish.", "Annotation processing")
        } else if (data['state'] == "SUCCESS") {
            $('#reload-modal').modal('toggle');
            show_annotation_status("bg-success", "The annotation is finished. Reload the page to see the updated annotations.", "Annotation finished")
        } else if (data['state'] == "FAILURE") {
            show_annotation_status("bg-danger", "Something unexpected happened during variant annotation: " + data['state'] + ' ' + data['status'], "Annotation error")
            $('#reannotate_button').attr('disabled', false);
        } else if (data['state'] == 'RETRY') {
            show_annotation_status("bg-warning", "Task yielded an error: " + data['status'] + ". Will try again soon.", "Retrying annotation")
        } else {
            show_annotation_status("bg-warning", "An unexpected status found: " + data['state'], "Unexpected status")
            $('#reannotate_button').attr('disabled', false);
        }

        // polling happens here:
        // rerun in 5 seconds if state resembles an unfinished task
        if (data['state'] == 'PENDING' || data['state'] == 'PROGRESS' || data['state'] == 'RETRY') {
            
            setTimeout(function() {
                update_annotation_status(status_url);
            }, 5000);
        }
    });
}


// utility for showing the current annotation status
function show_annotation_status(color_class, tooltip_text, inner_text) {
    $('#current_status').tooltip('hide')
    var annotation_status_obj = document.getElementById('annotation_status_pills')
    annotation_status_obj.innerHTML = ""
    // <span class="badge rounded-pill bg-secondary" data-bs-toggle="tooltip" title="annotation requested at {{ current_annotation_status[3] }}">annotation requested, <br> refresh page to see if it is ready</span>
    var status_pill = document.createElement('span')
    status_pill.classList.add('badge')
    status_pill.classList.add('rounded-pill')
    status_pill.classList.add(color_class)
    status_pill.setAttribute('data-bs-toggle', "tooltip")
    status_pill.setAttribute('title', tooltip_text)
    status_pill.innerText = inner_text
    annotation_status_obj.appendChild(status_pill)
    status_pill.id = "current_status"
}




///////////////////////////////////////////////////////////////
////////////////// further utility functions //////////////////
///////////////////////////////////////////////////////////////




/*
// Infer the variant type by looking at the number of reference and alternative bases
// use this in the header of the page
function get_variant_type(ref, alt) {
    const ref_len = ref.length
    const alt_len = alt.length
    var variant_type = "Variant display" // default phrase just in case
    if (ref_len === 1 && alt_len === 1) {
        variant_type = "SNV"
    }
    if (ref_len > alt_len) {
        variant_type = "Deletion (" + String(ref_len-alt_len) + " bp)"
    }
    if (ref_len < alt_len) {
        variant_type = "Insertion (" + String(alt_len-ref_len) + " bp)"
    }
    return variant_type
}
*/


function setup_igv(chrom, start, end, variant_id) {
    var igvDiv = document.getElementById("igv-container");
    const loc = chrom.toString() + ":" + start.toString() + '-' + end.toString()
    var options = {
        locus: loc,
        reference: {
            "id": "GRCh38",
            "name": "Human (GRCh38/hg38)",
            //"fastaURL": "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg38/hg38.fa",
            //"indexURL": "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg38/hg38.fa.fai",
            "fastaURL": "/download/hg38.fa",
            "indexURL": "/download/hg38.fa.fai",
            "tracks": [
                {
                    "name": "Ensembl genes",
                    "type": "annotation",
                    "format": "gff3",
                    "displayMode": "expanded",
                    "order": 100,
                    "indexed": false,
                    "autoHeight": true,
                    //"url": "/download/refgene_ngsd.gff3",
                    "url": "/download/refgene_ngsd.gff3.gz",
                    "indexURL": "/download/refgene_ngsd.gff3.gz.tbi",
                    "color": (feature) => {
                        if (feature.getAttributeValue("is_mane_plus_clinical") == 1) {
                            return "#00CC00"
                        }
                        if (feature.getAttributeValue("is_mane_select") == 1) {
                            return "red"
                        }
                        if (feature.getAttributeValue("is_ensembl_canonical") == 1) {
                            return "orange"
                        }
                        if (feature.getAttributeValue("is_gencode_basic") == 1) {
                            return "darkblue"
                        }
                        return "gray"
                    }
                },
                {
                    "name": "Variant",
                    "type": "variant",
                    "format": "vcf",
                    "url": "/download/vcf/one_variant?variant_id=" + variant_id.toString(),
                    "indexed": false,
                    "color": "red",
                    "autoHeight": true,
                    //"infoURL": "https://www.ncbi.nlm.nih.gov/gene/?term=$$"
                },
                {
                    "name": "Classified structural variants",
                    "type": "variant",
                    "format": "vcf",
                    "url": "/download/vcf/classified_sv",
                    "indexed": false,
                    "autoHeight": true,
                    "color": (variant) => {
                        if ('classification' in variant.info) {
                            const classification = variant.info['classification']
                            return get_consensus_classification_color(classification)
                        } else {
                            return get_consensus_classification_color('-')
                        }
                    }
                },
                {
                    "name": "Classified variants",
                    "type": "variant",
                    "format": "vcf",
                    "url": "/download/vcf/classified",
                    "indexed": false,
                    "autoHeight": true,
                    "color": (variant) => {
                        if ('classification' in variant.info) {
                            const classification = variant.info['classification']
                            return get_consensus_classification_color(classification)
                        } else {
                            return get_consensus_classification_color('-')
                        }
                    }
                }
            ]
        }
    };



    igv.createBrowser(igvDiv, options).then(function (browser) {
        browser.on('trackclick', function(track, popoverData) { // override the default popovers
            var markup = '<div class="overflow_x_auto">'
            markup += '<table class="styled-table" >';

            // Don't show a pop-over when there's no data.
            if (!popoverData || !popoverData.length) {
                return false;
            }

            var vid = -1

            popoverData.forEach(function (nameValue) {

                if (nameValue.name == 'ID') {
                    vid = nameValue.value
                }

                if (nameValue.name) {
                    markup +=get_row_markup(["<strong>" + nameValue.name + "</strong>", nameValue.value])
                }
                else if (nameValue.toString() == "<hr/>") { // not a name/value pair
                    markup += "<tr><td colspan='2'><hr/></td></tr>" 
                    if (vid != -1) {
                        const variant_page_url = document.getElementById('flask_data').dataset.variantPageUrl
                        const variant_url = variant_page_url.replace('-1', vid)
                        markup += get_row_markup(['<a href="' + variant_url + '">HerediVar</a>', ''])
                        markup += "<tr><td colspan='2'><hr/></td></tr>" 
                    }
                    
                }
            });

            markup += "</table>";
            markup += "</div>"

            // By returning a string from the trackclick handler we're asking IGV to use our custom HTML in its pop-over.
            return markup;
        });
    });

    function get_row_markup(values) {
        var markup = '<tr>';
        for (var i = 0; i < values.length; i++) {
            markup += "<td>" + values[i] + "</td>";
        }
        return markup;
    }
}

function create_hidden_pill() {
    //<span class="badge rounded-pill bg-danger" id="hidden_pill" data-bs-toggle="tooltip" title="This variant is hidden. To unhide use the gear button.">HIDDEN</span>
    var hidden_pill = document.createElement('span')
    hidden_pill.classList.add('badge')
    hidden_pill.classList.add('rounded-pill')
    hidden_pill.classList.add('bg-danger')
    hidden_pill.id = "hidden_pill"
    hidden_pill.setAttribute('data-bs-toggle', 'tooltip')
    hidden_pill.setAttribute('title', "This variant is hidden. To unhide use the gear button.")
    hidden_pill.innerText = "HIDDEN"
    return hidden_pill
}


// multi level dropdown functionality
// move to utils.js?
/*
(function($bs) {
    const CLASS_NAME = 'has-child-dropdown-show';
    $bs.Dropdown.prototype.toggle = function(_orginal) {
        return function() {
            document.querySelectorAll('.' + CLASS_NAME).forEach(function(e) {
                e.classList.remove(CLASS_NAME);
            });
            let dd = this._element.closest('.dropdown').parentNode.closest('.dropdown');
            for (; dd && dd !== document; dd = dd.parentNode.closest('.dropdown')) {
                dd.classList.add(CLASS_NAME);
            }
            return _orginal.call(this);
        }
    }($bs.Dropdown.prototype.toggle);

    document.querySelectorAll('.dropdown').forEach(function(dd) {
        dd.addEventListener('hide.bs.dropdown', function(e) {
            if (this.classList.contains(CLASS_NAME)) {
                this.classList.remove(CLASS_NAME);
                e.preventDefault();
            }
            e.stopPropagation(); // do not need pop in multi level mode
        });
    });

    // for hover
    document.querySelectorAll('.dropdown-hover, .dropdown-hover-all .dropdown').forEach(function(dd) {
        dd.addEventListener('mouseenter', function(e) {
            let toggle = e.target.querySelector(':scope>[data-bs-toggle="dropdown"]');
            if (!toggle.classList.contains('show')) {
                $bs.Dropdown.getOrCreateInstance(toggle).toggle();
                dd.classList.add(CLASS_NAME);
                $bs.Dropdown.clearMenus();
            }
        });
        dd.addEventListener('mouseleave', function(e) {
            let toggle = e.target.querySelector(':scope>[data-bs-toggle="dropdown"]');
            if (toggle.classList.contains('show')) {
                $bs.Dropdown.getOrCreateInstance(toggle).toggle();
            }
        });
    });

    $('.dropdown').on('hidden.bs.dropdown', function() {
        $(this).tooltip("hide");
        //$(this).dropdown('toggle');
    })
})(bootstrap);
*/