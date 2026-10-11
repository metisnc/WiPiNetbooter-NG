<?php
include 'menu.php';
echo '<html lang="en"><head><meta charset="utf-8"><title>WiPi Netbooter</title>';
echo '<link rel="stylesheet" href="css/sidebarstyles.css">';
echo '<section><center><p>';
echo '<h1><a href="setup.php">NFC Game Write</a></h1>';
echo '<html><body>';

echo '<br>To write a game to NFC card choose from the drop down<br><br>';

$path = '/boot/roms/';
$files = array_values(array_diff(scandir($path), array('.', '..')));
$f = fopen("csv/romsinfo.csv", "r");
echo '<form method="POST" action="cardactions.php?command=nfcgame"><select style="width:50%" name="nfcgame">';
echo '<option value="menu">On-Screen Menu</option>';
while (($row = fgetcsv($f)) !== false) {
        foreach ($row as $cell) {
             if (in_array($row[1], $files)){
                echo '<option value="'.$row[1].'">'.$row[4].'</option>';
                break;
             }
        }
}
fclose($f);
echo '</select><br><br>';
echo '<input type="submit" name="submit" class="dropbtn" value="Write to NFC" /></form></td>';

?>