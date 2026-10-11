<?php
// Shared helpers for the touch launcher.
// Reads the same data as gamelist.php / loadcheck.php / load.php (WiPi 6.1-92), never writes to them.

define('WEB_ROOT', dirname(__DIR__, 2));
define('LAUNCHER_ROOT', dirname(__DIR__));
define('DATA_DIR', LAUNCHER_ROOT . '/data');
define('ROMS_CSV', WEB_ROOT . '/csv/romsinfo.csv');
define('DIMMS_CSV', WEB_ROOT . '/csv/dimms.csv');
define('ROMS_DIR', '/boot/roms');
define('PIFORCE_DIR', '/sbin/piforce');
define('LAST_GAME_LOG', '/var/www/logs/log.txt');

// romsinfo.csv absolute column indexes (see WiPi manual, Advanced section)
define('COL_SYSTEM', 0);
define('COL_ROM', 1);
define('COL_IMAGE', 2);
define('COL_VIDEO', 3);
define('COL_NAME', 4);
define('COL_MANUFACTURER', 6);
define('COL_YEAR', 7);
define('COL_GENRE', 8);
define('COL_ORIENTATION', 10);
define('COL_CONTROLS', 11);
define('COL_ENABLED', 12);
define('COL_FAVOURITE', 13);
define('COL_MAPPING', 14);
define('COL_FFB', 15);

function config()
{
    static $config = null;
    if ($config === null) {
        $config = require LAUNCHER_ROOT . '/config.php';
    }
    return $config;
}

function is_simulation()
{
    return !empty(config()['simulate']);
}

function read_mode($name)
{
    $value = @file_get_contents(PIFORCE_DIR . '/' . $name . '.txt');
    return $value === false ? '' : trim($value);
}

function json_out($data, $code = 200)
{
    http_response_code($code);
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

function require_post()
{
    if ($_SERVER['REQUEST_METHOD'] !== 'POST' || ($_SERVER['HTTP_X_LAUNCHER'] ?? '') !== '1') {
        json_out(['error' => 'method not allowed'], 405);
    }
}

// Same compatibility rules as loadcheck.php
function supported_systems($dimmtype)
{
    switch ($dimmtype) {
        case 'Sega Naomi':    return ['Sega Naomi', 'Sammy Atomiswave'];
        case 'Sega Naomi2':   return ['Sega Naomi', 'Sega Naomi2', 'Sammy Atomiswave'];
        case 'Sega Chihiro':  return ['Sega Chihiro'];
        case 'Sega Triforce': return ['Sega Triforce'];
    }
    return [];
}

function load_dimms()
{
    $dimms = [];
    if (($f = @fopen(DIMMS_CSV, 'r')) === false) {
        return $dimms;
    }
    fgetcsv($f);
    while (($row = fgetcsv($f)) !== false) {
        if (count($row) < 3 || $row[1] === '') {
            continue;
        }
        $dimms[] = ['name' => $row[0], 'ip' => $row[1], 'type' => $row[2]];
    }
    fclose($f);
    return $dimms;
}

function load_games()
{
    $present = array_flip(array_diff(@scandir(ROMS_DIR) ?: [], ['.', '..']));

    // System Filter option: only keep systems the configured netdimms can boot (as gamelist.php)
    $allowed = null;
    if (read_mode('filtermode') === 'filteron') {
        $allowed = [];
        foreach (load_dimms() as $dimm) {
            $allowed = array_merge($allowed, supported_systems($dimm['type']));
        }
    }

    $games = [];
    if (($f = @fopen(ROMS_CSV, 'r')) === false) {
        return $games;
    }
    fgetcsv($f);
    while (($row = fgetcsv($f)) !== false) {
        if (count($row) <= COL_FFB || $row[COL_ENABLED] !== 'Yes' || !isset($present[$row[COL_ROM]])) {
            continue;
        }
        if ($allowed !== null && !in_array($row[COL_SYSTEM], $allowed, true)) {
            continue;
        }
        $games[$row[COL_ROM]] = [
            'rom' => $row[COL_ROM],
            'system' => $row[COL_SYSTEM],
            'name' => $row[COL_NAME],
            'image' => $row[COL_IMAGE],
            'manufacturer' => $row[COL_MANUFACTURER],
            'year' => $row[COL_YEAR],
            'genre' => $row[COL_GENRE],
            'orientation' => $row[COL_ORIENTATION],
            'controls' => $row[COL_CONTROLS],
            'fave' => $row[COL_FAVOURITE] === 'Yes',
            'mapping' => $row[COL_MAPPING],
            'ffb' => $row[COL_FFB],
        ];
    }
    fclose($f);
    return $games;
}

function find_game($rom)
{
    $games = load_games();
    return $games[$rom] ?? null;
}

function last_game_rom()
{
    $log = @file_get_contents(LAST_GAME_LOG);
    if (!$log) {
        return null;
    }
    return explode(' ', trim($log))[0];
}

function read_json_file($path, $default)
{
    $raw = @file_get_contents($path);
    $data = $raw === false ? null : json_decode($raw, true);
    return $data === null ? $default : $data;
}

function write_json_file($path, $data)
{
    $tmp = $path . '.tmp';
    if (@file_put_contents($tmp, json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)) === false) {
        return false;
    }
    return @rename($tmp, $path);
}

function read_history()
{
    return read_json_file(DATA_DIR . '/history.json', []);
}

function add_history($rom)
{
    $history = array_values(array_diff(read_history(), [$rom]));
    array_unshift($history, $rom);
    write_json_file(DATA_DIR . '/history.json', array_slice($history, 0, config()['history_size']));
}

function ping($ip)
{
    exec('fping -c1 -t500 ' . escapeshellarg($ip) . ' 2>/dev/null', $output, $status);
    return $status === 0;
}

function tail_lines($path, $count)
{
    $lines = @file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    if ($lines === false) {
        exec('sudo tail -n ' . (int)$count . ' ' . escapeshellarg($path) . ' 2>/dev/null', $lines);
    }
    return array_slice($lines, -$count);
}
