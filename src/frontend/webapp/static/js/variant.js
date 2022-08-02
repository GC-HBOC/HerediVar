

// presort the tables on page load
table = document.getElementById("variantConsequenceTable");
if (table != null) {
    filterTable_one_column("ensembl", 10, table);
    sorter(['#variant_consequence_numflags_col', '#variant_consequence_length_col'], '#variantConsequenceTable') // sort first by num of flags and if there is a tie sort by length
}
sorter(['#userClassificationsTableDateCol'], '#userClassificationsTable')
sorter(['#literatureTableYearCol'], '#literatureTable')
sorter(['#clinvarSubmissionsTableLastEvaluatedCol'], '#clinvarSubmissionsTable')
sorter(['#heredicareCenterClassificationsTableDateCol'], '#heredicareCenterClassificationsTable')
sorter(['#userSchemeClassificationsTableDateCol'], '#userSchemeClassificationsTable')



// functionality for the consequence table switch between ensembl & refseq
function filter_consequence_table(source) {
    const table = document.getElementById('variantConsequenceTable')
    filterTable_one_column(source, 10, table)
    const sort_columns = ['#variant_consequence_numflags_col', '#variant_consequence_length_col']
    for (var i = 0; i < sort_columns.length; i++) {
        $(sort_columns[i]).attr('asc', 'true')
    }
    sorter(sort_columns, '#' + table.id)
}



$(document).ready(function()
{
    ////////// functionality for the reannotate button
    var annotation_status = $('#annotation_status').data()['annotationStatus'];
    if (annotation_status === 'pending'){
        $('#reannotate_button').attr('disabled', true)
        $('#reannotate_form').attr('title', "Wait for the current annotation to finish before submitting another one")
    }

    $('#reannotate-submit').click(function(){
        $('#reannotate_button').attr('disabled', true);
        /* when the submit button in the modal is clicked, submit the form */
       $('#reannotate_form').submit();
    });

    //$('.classification-gradient').css({'background': 'linear-gradient(90deg, ' + class5ColorRGB + ' 0%, rgba(170,240,170,1) 20%, rgba(190,250,190,1) 40%, rgba(255,255,255,1) 100%)'});
    //$('.classification-gradient').css({'background': 'linear-gradient(90deg, rgba(149,149,149,0.5) 0%, rgba(195,195,195,0.5) 20%, rgba(232,232,232,0.5) 40%, rgba(255,255,255,1) 100%)'});
    
});




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
        $(this).dropdown('toggle');
    })
})(bootstrap);
