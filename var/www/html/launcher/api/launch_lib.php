<?php
// Launch state shared by launch.php / status.php / cancel.php.
// Real launches run exactly what load.php runs (wipiloader.py), progress comes from
// /var/log/progress_<ip> written by dm_netboot (0..100 then "COMPLETE").

require_once __DIR__ . '/lib.php';

define('LAUNCH_STATE', DATA_DIR . '/launch.json');
define('LOADER_PATTERN', '[w]ipiloader\.py|[n]etdimm_send');

function read_launch()
{
    return read_json_file(LAUNCH_STATE, null);
}

function write_launch($launch)
{
    return write_json_file(LAUNCH_STATE, $launch);
}

function loader_running()
{
    exec('pgrep -f ' . escapeshellarg(LOADER_PATTERN), $output, $status);
    return $status === 0;
}

// Netdimms able to boot this game. In simulation, fake ones depending on the scenario.
function candidate_dimms($game, $scenario)
{
    if ($scenario !== null) {
        if ($scenario === 'nodimm') {
            return [];
        }
        if ($scenario === 'multi') {
            return [
                ['name' => 'Borne 1 (simulée)', 'ip' => '10.0.0.98'],
                ['name' => 'Borne 2 (simulée)', 'ip' => '10.0.0.99'],
            ];
        }
        return [['name' => 'Borne simulée', 'ip' => '10.0.0.99']];
    }

    $online = [];
    foreach (load_dimms() as $dimm) {
        if (in_array($game['system'], supported_systems($dimm['type']), true) && ping($dimm['ip'])) {
            $online[] = ['name' => $dimm['name'], 'ip' => $dimm['ip']];
        }
    }
    return $online;
}

function start_loader($game, $ip)
{
    $args = [$game['rom'], $ip, read_mode('relaymode'), read_mode('zeromode'), $game['mapping'], $game['ffb']];
    $command = 'sudo python3 /sbin/piforce/wipiloader.py ' . implode(' ', array_map('escapeshellarg', $args));
    exec($command . ' > /dev/null 2>&1 &');
}

function public_launch($launch)
{
    return [
        'rom' => $launch['rom'],
        'name' => $launch['name'],
        'image' => $launch['image'],
        'system' => $launch['system'] ?? '',
        'dimm' => $launch['dimm_name'],
    ];
}

function simulated_status($launch, $elapsed)
{
    $connect = 1.5;
    $duration = $launch['sim'] === 'slow' ? 20.0 : 6.0;
    if ($elapsed < $connect) {
        return ['state' => 'connecting'];
    }
    $progress = (int)min(100, ($elapsed - $connect) / $duration * 100);
    if ($launch['sim'] === 'error' && $progress >= 45) {
        return ['state' => 'error', 'progress' => 45, 'log' => [
            'sending...',
            'Simulation: connection to 10.0.0.99 lost',
            'TimeoutError: timed out',
        ]];
    }
    return $progress >= 100 ? ['state' => 'done', 'progress' => 100] : ['state' => 'running', 'progress' => $progress];
}

function launch_status()
{
    $launch = read_launch();
    if (!$launch) {
        return ['state' => 'idle'];
    }
    $public = public_launch($launch);
    if (!empty($launch['ended'])) {
        return $public + ['state' => $launch['ended']];
    }

    $elapsed = microtime(true) - $launch['started'];
    if ($launch['sim'] !== null) {
        return $public + simulated_status($launch, $elapsed);
    }

    // The progress file is only rewritten when the upload starts: ignore a stale one.
    $file = '/var/log/progress_' . $launch['dimm'];
    clearstatcache(true, $file);
    $mtime = @filemtime($file);
    $last = null;
    if ($mtime !== false && $mtime >= floor($launch['started'])) {
        $lines = tail_lines($file, 1);
        $last = $lines ? trim(end($lines)) : null;
    }

    if ($last === 'COMPLETE') {
        return $public + ['state' => 'done', 'progress' => 100];
    }
    if (loader_running()) {
        return $public + (is_numeric($last)
            ? ['state' => 'running', 'progress' => (int)$last]
            : ['state' => 'connecting']);
    }
    if ($elapsed < 4) {
        return $public + ['state' => 'connecting'];
    }
    $log = tail_lines('/var/log/netdimm_send.log', 4);
    if (!$log) {
        $log = tail_lines('/var/log/wipiloader.log', 4);
    }
    return $public + ['state' => 'error', 'progress' => is_numeric($last) ? (int)$last : 0, 'log' => $log];
}

function launch_in_progress()
{
    $status = launch_status();
    return in_array($status['state'], ['connecting', 'running'], true);
}
