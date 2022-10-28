
transcript_table_default_sorting_columns = ['#transcript_table_numflags_col', '#transcript_table_length_col']
transcript_table_ascending = ['true', 'true']

table = document.getElementById("transcriptTable");
if (table != null) {
    filterTable_one_column("ensembl", 4, table);
    table_sorter(transcript_table_default_sorting_columns, '#transcriptTable')
}



// functionality for the consequence table switch between ensembl & refseq
function filter_transcript_table(source) {
    const table = document.getElementById('transcriptTable')
    filterTable_one_column(source, 4, table)
    const sort_columns = transcript_table_default_sorting_columns
    for (var i = 0; i < sort_columns.length; i++) {
        $(sort_columns[i]).attr('asc', transcript_table_ascending[i])
    }
    table_sorter(sort_columns, '#' + table.id)
}
