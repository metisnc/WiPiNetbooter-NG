<?php
// POST {rom, dimm?, sim?}: checks online netdimms (like loadcheck.php) then starts the loader.
// Answers: started | choose (several netdimms) | nodimm | busy | error.
require __DIR__ . '/launch_lib.php';

require_post();
$input = json_decode(file_get_contents('php://input'), true) ?: [];

$game = find_game((string)($input['rom'] ?? ''));
if (!$game) {
    json_out(['state' => 'error', 'message' => 'Jeu introuvable'], 404);
}

$scenario = null;
if (is_simulation()) {
    $scenario = in_array($input['sim'] ?? '', ['ok', 'error', 'slow', 'multi', 'nodimm'], true) ? $input['sim'] : 'ok';
}

if (launch_in_progress()) {
    json_out(['state' => 'busy'] + public_launch(read_launch()));
}

$dimms = candidate_dimms($game, $scenario);
$wanted = (string)($input['dimm'] ?? '');
if ($wanted !== '') {
    $dimms = array_values(array_filter($dimms, function ($dimm) use ($wanted) {
        return $dimm['ip'] === $wanted;
    }));
}

if (!$dimms) {
    // Configured but silent netdimms: distinguishes "nothing set up" from "the board does not answer"
    json_out(['state' => 'nodimm', 'system' => $game['system'],
        'offline' => $scenario === null ? compatible_dimms($game) : []]);
}
if (count($dimms) > 1) {
    json_out(['state' => 'choose', 'dimms' => $dimms]);
}

$dimm = $dimms[0];
$launch = [
    'rom' => $game['rom'],
    'name' => $game['name'],
    'image' => $game['image'],
    'system' => $game['system'],
    'dimm' => $dimm['ip'],
    'dimm_name' => $dimm['name'],
    'started' => microtime(true),
    'sim' => $scenario,
];
if (!write_launch($launch)) {
    json_out(['state' => 'error', 'message' => 'Dossier launcher/data non accessible en écriture'], 500);
}
if ($scenario === null) {
    start_loader($game, $dimm['ip']);
}
add_history($game['rom']);

json_out(['state' => 'started'] + public_launch($launch));
