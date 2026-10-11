<?php
// GET: state of the last launch (idle | connecting | running | done | error | cancelled).
require __DIR__ . '/launch_lib.php';

json_out(launch_status());
