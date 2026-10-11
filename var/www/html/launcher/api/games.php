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

$list = [];
foreach ($games as $game) {
    unset($game['mapping'], $game['ffb']);
    $list[] = $game;
}

json_out([
    'games' => $list,
    'history' => $history,
    'simulate' => is_simulation(),
]);
