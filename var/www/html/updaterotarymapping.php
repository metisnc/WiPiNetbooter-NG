<?php

$command = escapeshellcmd("sudo python /sbin/piforce/rotaryfile.py");
shell_exec($command);

$newslots = array($_POST['slot0'], $_POST['slot1'], $_POST['slot2'], $_POST['slot3'], $_POST['slot4'], $_POST['slot5'], $_POST['slot6'], $_POST['slot7'], $_POST['slot8'], $_POST['slot9'], $_POST['slot10'], $_POST['slot11'], $_POST['slot12'], $_POST['slot13'], $_POST['slot14'], $_POST['slot15']);

for ($x = 0; $x <= 15; $x++) {
    if ($newslots[$x] == "notset" || $newslots[$x] == ""){
        $lastslot = $x;
        break;
    }
}

$newslots = array_slice($newslots, 0, $lastslot);
$rotaryfile = '/etc/openjvs/rotary';
file_put_contents($rotaryfile, implode("\n", $newslots));
header ("Location: editrotarymappings.php?updated=true");

?>