import igv from "/static/packages/igv/igv.esm.js"

const flask_data = document.getElementById("flask_data")
const delete_classification_url = flask_data.dataset.deleteClassificationUrl
const annotation_status_url = flask_data.dataset.annotationStatusUrl
const variant_id = flask_data.dataset.variantId
const run_annotation_service_url = flask_data.dataset.runAnnotationServiceUrl


$(document).ready(function(){

    // add delete column to list variant view
    var classification_table = $('#userClassificationsTable')
    classification_table.find('thead').find('tr').append('<th class="text_align_center bold width_minimal">Del</th>')
    
    classification_table.find('tbody').find('tr').each(function(){
        var trow = $(this)
        var variant_id = trow[0].getAttribute("variant_id")
        var user_classification_id = trow[0].getAttribute("user_classification_id")
        var can_delete = trow[0].getAttribute("can_delete")
        if (can_delete === "True") {
            create_delete_button(trow, delete_classification_url, variant_id, user_classification_id)
        } else {
            create_xlg(trow, "You are not allowed to delete this classification")
        }
    });
    activate_data_href_links()

    // functionality for the hide variant button
    $('#change_hidden_state').click(function() {
        $.ajax({
            type: 'POST',
            url: this.getAttribute('url'),
            success: function(data, status, request) {
                if (data === 'True') {
                    const hidden_pill = create_hidden_pill()
                    document.getElementById('hidden_status_pill_holder').appendChild(hidden_pill)
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
        $('#add-to-list-form').attr('action', $(this).attr('action'))
    });

    $('#igv-tab').one('show.bs.tab', function() { // gets called only the first time you switch to the igv tab
        const variant_page_title_obj = document.getElementById('variant_page_title')
        const chrom = variant_page_title_obj.getAttribute('chrom')
        const pos = parseInt(variant_page_title_obj.getAttribute('pos'))
        setup_igv(chrom, pos-100, pos+100, variant_id)
    })

    update_annotation_status(annotation_status_url);
})


///////////////////////////////////////////////////////////////////////
////////////////// reannotation button functionality //////////////////
///////////////////////////////////////////////////////////////////////

// function triggered on reannotaiton submit button pressed
function confirm_reannotation_action() {
    // send ajax POST request to start background job
    $.ajax({
        type: 'POST',
        url: run_annotation_service_url,
        data: {"variant_id": variant_id},
        success: function(data, status, request) {
            show_annotation_status('bg-secondary', "Annotation requested successfully", "Annotation requested")
            update_annotation_status(annotation_status_url);
        },
        error: function(xhr) {
            console.log(xhr)
            show_annotation_status("bg-danger", "The variant could not be annotated. Either the service is unreachable or some other unexpected exception occured. You can try to reload this page or issue another annotation to fix this. If that does not help try again later. Status code is: " + xhr.status, "Internal error")
            $('#reannotate_button').attr('disabled', false)
        }
    });
}


// polling & status display update
function update_annotation_status(status_url, show_reload_modal=false) {
    // send GET request to status URL (defined by flask)
    $.ajax({
        type: 'GET',
        url: status_url,
        data: {"variant_id": variant_id},
        success: function(data, status, request) {
            console.log(data)
            if (data === undefined) {
                show_annotation_status("bg-secondary", "This variant is not annotated, yet. Submit one using the gear button.", "No annotation")
            } else {
                if (data['status'] == 'pending') {
                    show_annotation_status("bg-secondary", "Annotation is queued. This annotation job is waiting for other jobs to finish first.", "Annotation queued")
                } else if (data['status'] == 'progress') {
                    show_annotation_status("bg-primary", "Annotation is being processed in the background. Please wait for it to finish.", "Annotation processing")
                } else if (data['status'] == "success") {
                    if (show_reload_modal) {
                        $('#reload-modal').modal('toggle');
                    }
                    show_annotation_status("bg-success", "Last annotation finished at " + data["finished_at"] + ". Reload the page to see updated annotations.", "Annotation done")
                } else if (data['status'] == "error") {
                    show_annotation_status("bg-danger", "Variant annotation finished at " + data["finished_at"] + " with fatal error: " + data['error_message'], "Annotation error")
                    $('#reannotate_button').attr('disabled', false);
                } else if (data['status'] == 'retry') {
                    show_annotation_status("bg-warning", "Task yielded an error: " + data['error_message'] + ". Will try again soon.", "Retrying annotation")
                } else if (data['status'] == 'aborted') {
                    show_annotation_status("bg-primary", "This task was manually aborted at " + data['finished_at'] + ". It is recommended to restart the annotation.", "Annotation aborted")
                } else if (data['status'] == 'no annotation') {
                    show_annotation_status("bg-secondary", "This variant does not have an annotation, yet. You can issue one through the gear button.", "No annotation")
                } else {
                    show_annotation_status("bg-warning", "An unexpected status found: " + data['status'], "Unexpected status")
                    $('#reannotate_button').attr('disabled', false);
                }

                // polling happens here:
                // rerun in 5 seconds if state resembles an unfinished task
                if (data['status'] == 'pending' || data['status'] == 'progress' || data['status'] == 'retry') {
                    setTimeout(function() {
                        update_annotation_status(status_url, show_reload_modal=true);
                    }, 5000);
                }
            }
        },
        error: function(xhr) {
            show_annotation_status("bg-danger", "Unable to fetch the status of the annotation. Server returned http status " + xhr.status, "Internal error")
            $('#reannotate_button').attr('disabled', false)
        }
    })

}


// utility for showing the current annotation status
function show_annotation_status(color_class, tooltip_text, inner_text) {
    $('#annotation_status_pill').tooltip('hide')
    document.getElementById('annotation_status_pill_holder').innerHTML = ""
    var status_pill = document.createElement('span')
    status_pill.classList.add('badge')
    status_pill.classList.add('rounded-pill')
    status_pill.classList.add(color_class)
    status_pill.setAttribute('data-bs-toggle', "tooltip")
    status_pill.setAttribute('title', tooltip_text)
    status_pill.innerText = inner_text
    annotation_status_pill_holder.appendChild(status_pill)
}


/////////////////////////////////////////////////
////////////////// IGV UTILITY //////////////////
/////////////////////////////////////////////////

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
                    "url": "/download/vcf/classified?variant_type=sv",
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
                    "url": "/download/vcf/classified?variant_type=small",
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



///////////////////////////////////////////////////////////////
////////////////// further utility functions //////////////////
///////////////////////////////////////////////////////////////

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


function create_delete_button(parent, base_url, variant_id, user_classification_id) {
    var td = document.createElement("td")
    td.classList.add('text_align_center')
    parent[0].appendChild(td)

    var button = document.createElement("button")
    button.setAttribute("type", "button")
    button.classList.add('btn')
    button.classList.add("btn-link")
    button.classList.add("nopad")
    button.addEventListener("click", function() {
        show_delete_modal(base_url, variant_id, user_classification_id)
    })
    td.appendChild(button)

    const image = create_trashcan()
    button.appendChild(image)
}

function show_delete_modal(base_url, variant_id, user_classification_id) {
    const delete_user_classification_button = document.getElementById("delete_user_classification-submit")
    delete_user_classification_button.onclick = function() {
        delete_user_classification_action(base_url, variant_id, user_classification_id)
        $('#delete_user_classification-modal').modal('hide');
    }
    $('#delete_user_classification-modal').modal('toggle');
}


function delete_user_classification_action(base_url, variant_id, user_classification_id) {
    $.ajax({
        type: "get",
        url: base_url,
        data: {"variant_id": variant_id, "user_classification_id": user_classification_id},
        success: function(data, status, request) {
            console.log(data)

            if (data == "success") {
                $('[user_classification_id="' + user_classification_id + '"]').remove()
            }
            
            console.log($("#userClassificationsTable tr").length)
            
            if ($("#userClassificationsTable tr").length <= 1) {
                $("#heredivar_user_classifications_section").remove()
            }
        },
        error: function() {
            
        }
    });
}