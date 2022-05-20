<?php

require_once("utils/functions.php");
require_once("utils/paths.php");


$xml = new SimpleXMLElement('<SeqIdList/>');
//$seqid_list = $xml->addChild('SeqIdList');

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
$xml_string=$xml->asXML();

print($xml_string);


?>