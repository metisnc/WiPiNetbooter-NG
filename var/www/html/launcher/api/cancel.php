<?php
// POST: stop the running transfer (wipiloader.py and netdimm_send). The netdimm then
// stays on its "now loading" screen until another game is sent.
require __DIR__ . '/launch_lib.php';

require_post();
$launch = read_launch();
if (!$launch) {
    json_out(['state' => 'idle']);
}

if ($launch['sim'] === null) {
    exec('sudo pkill -f ' . escapeshellarg(LOADER_PATTERN) . ' 2>/dev/null');
}
$launch['ended'] = 'cancelled';
write_launch($launch);

json_out(launch_status());
