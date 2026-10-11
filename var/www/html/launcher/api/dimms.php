<?php
// GET: configured netdimms (csv/dimms.csv) and whether they answer a ping, for the Réglages screen.
require __DIR__ . '/lib.php';

$dimms = [];
foreach (load_dimms() as $dimm) {
    $dimm['online'] = ping($dimm['ip']);
    $dimms[] = $dimm;
}

json_out(['dimms' => $dimms]);
