<?php
// GET: games visible in the launcher, plus favourites / recent history.
require __DIR__ . '/lib.php';

$games = load_games();

$history = array_values(array_filter(read_history(), function ($rom) use ($games) {
    return isset($games[$rom]);
}));
$last = last_game_rom();
if ($last !== null && isset($games[$last]) && !in_array($last, $history, true)) {
    $history[] = $last;
}

// Game running on the cabinet: the last one sent (by the launcher or the original UI, both write
// log.txt) since the Pi booted. The kiosk only goes to sleep once a game is running.
$playing = null;
$uptime = (float)@file_get_contents('/proc/uptime');
$sentAt = @filemtime(LAST_GAME_LOG);
if ($last !== null && isset($games[$last]) && $uptime > 0 && $sentAt !== false && $sentAt >= time() - $uptime) {
    $playing = $last;
}

$list = [];
foreach ($games as $game) {
    unset($game['mapping'], $game['ffb']);
    if ($game['video'] !== '' && !is_file(WEB_ROOT . '/videos/' . $game['video'])) {
        $game['video'] = '';
    }
    $list[] = $game;
}

json_out([
    'games' => $list,
    'history' => $history,
    'simulate' => is_simulation(),
    'sound' => read_mode('soundmode') === 'soundon',
    'playing' => $playing,
]);
