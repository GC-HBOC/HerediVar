table = document.getElementById("transcriptTable");
if (table != null) {
    filterTable_one_column("ensembl", 4, table);
    sorter(['#transcripts_numflags_col', '#transcripts_length_col']) // sort first by num of flags and if there is a tie sort by length
}