<?php

require_once("utils/functions.php");


$file_path = "heredicare_variants_11.05.22_ANNOTATED.tsv";

$xml = new SimpleXMLElement('<xml/>');


if (file_exists($file_path)){
    $file = file($file_path);
    foreach($file as $line)
    {
        $line = trim($line);
        if ($line=="" | startsWith($line, '#')) continue;
        
        $parts = explode("\t", $line);
        $seqid = $parts[0];

        $seqid_entry = $xml->addChild('SeqId');
        $seqid_entry->addAttribute('id', $seqid);
    }
}

Header('Content-type: text/xml');
print($xml->asXML());


?>