<?php

require_once("utils/functions.php");
require_once("utils/paths.php");


$xml = new SimpleXMLElement('<VIdList/>');
//$vid_list = $xml->addChild('VIdList');

if (file_exists($file_path)){
    $file = file($file_path);
    foreach($file as $line)
    {
        $line = trim($line);
        if ($line=="" | startsWith($line, '#')) continue;
        
        $parts = explode("\t", $line);
        $vid = $parts[0];

        $vid_entry = $xml->addChild('VId');
        $vid_entry->addAttribute('id', $vid);
    }
}

Header('Content-type: text/xml');
$xml_string=$xml->asXML();

print($xml_string);


?>