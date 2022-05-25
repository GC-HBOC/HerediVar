<?php


require_once("utils/functions.php");
require_once("utils/paths.php");

$seqid_request = $_GET['seqid'];

$variant = new SimpleXMLElement('<Variant/>');

if (file_exists($file_path)) {
    $file = file($file_path);
    foreach($file as $line) { // search for the seqid in that file
        $line = trim($line);
        if ($line=="" | startsWith($line, '#')) continue;
        
        $parts = explode("\t", $line);
        $current_seqid = $parts[0];

        if ($current_seqid == $seqid_request) {
            // capture vcf style in attributes of variant
            $variant->addAttribute('chr', 'chr'.trim($parts[3]));
            $variant->addAttribute('pos', trim($parts[4]));
            $variant->addAttribute('ref', trim($parts[5]));
            $variant->addAttribute('alt', trim($parts[6]));
            $variant->addAttribute('genome_build', 'GRCh37');

            // add some mock data
            $occurances = $variant->addChild('Occurances');
            if ($current_seqid == '11334923'){
                $occurances->addAttribute('cases_count', 65);
                $occurances->addAttribute('family_count', 423547);
            } else {
                $occurances->addAttribute('cases_count', 69);
                $occurances->addAttribute('family_count', 42);
            }

            $classification_center = $variant->addChild('ClassificationCenter');
            $classification_center->addAttribute('class', 5);
            $classification_center->addAttribute('date', '1999-01-01');
            $classification_center->addAttribute('center_name', 'Uniklinik Tübingen');
            $classification_center->addAttribute('comment', 'this is a test');
            
            $classification_center = $variant->addChild('ClassificationCenter');
            $classification_center->addAttribute('class', 5);
            $classification_center->addAttribute('date', '2020-05-01');
            $classification_center->addAttribute('center_name', 'Hamburger Hähnchenfabrik');
            $classification_center->addAttribute('comment', 'this is a test for the second classificatoin center');

            $classification_task_force = $variant->addChild('ClassificationTaskForce');
            $classification_task_force->addAttribute('class', 5);
            $classification_task_force->addAttribute('date', '2022-06-12');
            $classification_task_force->addAttribute('comment', 'Evidence provided äöüß');
        }
    }
}

Header('Content-type: text/xml');
$xml_string=$variant->asXML();

print($xml_string);


?>