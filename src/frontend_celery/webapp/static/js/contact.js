const core_gene_transcripts = JSON.parse(flask_data.dataset.coreGeneTranscripts)
console.log(core_gene_transcripts)

function create_option(value, text) {
    var option = document.createElement('option')
    option.classList.add("color_black")
    option.value = value
    option.innerText = text
    return option
}

function clear_options(select) {
    var i, L = select.options.length - 1;
    for(i = L; i >= 0; i--) {
        select.remove(i);
    }
}

function create_default_option() {
    var option = document.createElement('option')
    option.classList.add()
    option.value = ""
    option.selected = "selected"
    option.disabled = true
    option.hidden = true
    option.innerText = "Choose a gene before choosing the transcript"
    return option
}


function switch_gene() {
    const gene_select = document.getElementById('gene')
    const selected_gene = gene_select.value
    if (selected_gene == "") {
        return
    }
    const transcripts_oi = core_gene_transcripts[selected_gene]
    const transcript_select = document.getElementById('transcript')

    
    clear_options(transcript_select)
    transcript_select.appendChild(create_default_option())

    for (var i = 0; i < transcripts_oi.length; i++) {
        var current_transcript = transcripts_oi[i]
        var current_transcript_name = current_transcript['name']
        var new_option = create_option(current_transcript_name, current_transcript_name)
        transcript_select.appendChild(new_option)
    }
}



$(document).ready(function() {
    $('#gene').change(function () {
        switch_gene();
    });

    switch_gene()
});