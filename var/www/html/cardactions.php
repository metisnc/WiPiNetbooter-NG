<?php
mb_internal_encoding("UTF-8");
$mode = $_GET['mode'];
echo '<html lang="en"><head><meta charset="utf-8"><title>WiPi Netbooter</title>';
echo '<meta name="description" content="Responsive Header Nav">';
echo '<meta name="viewport" content="width=device-width; initial-scale=1; maximum-scale=1">';
echo '<link rel="stylesheet" href="css/sidebarstyles.css">';
include 'menu.php';
echo '<section><center><p>';
if ($mode == 'main'){
echo '<h1><a href="setup.php">Card Management</a></h1>';}
else {
echo '<h1><a href="cardmanagement.php?mode=main">Card Management</a></h1>';}

$emumode = file_get_contents('/sbin/piforce/emumode.txt');
$nfcmode = file_get_contents('/sbin/piforce/nfcmode.txt');


if ($_GET["command"] == 'nfcwipe') {
$copyfile = $_GET["filetocopy"];
$path_parts = pathinfo($copyfile);
$phpfile = '/var/www/html/cards/'.$mode.'/'.$path_parts['filename'].'.printdata.php';
ini_set('output_buffering', false);

echo '<b><br>Wiping Existing Card Data<br></b>';
$handle = popen('sudo python3 /sbin/piforce/card_emulator/nfcwipe.py', 'r');
while(!feof($handle)) {
    $buffer = fgets($handle);
    echo "$buffer";
    flush();
}
pclose($handle);

echo '<br><a href="cardmanagement.php?mode='.$mode.'">Return to Card Management</a>';
}

if ($_GET["command"] == 'nfcwrite') {
$copyfile = $_GET["filetocopy"];
$path_parts = pathinfo($copyfile);
$phpfile = '/var/www/html/cards/'.$mode.'/'.$path_parts['filename'].'.printdata.php';
ini_set('output_buffering', false);

echo '<b><br>Wiping Existing Card Data<br></b>';
$handle = popen('sudo python3 /sbin/piforce/card_emulator/nfcwipe.py', 'r');
while(!feof($handle)) {
    $buffer = fgets($handle);
    echo "$buffer";
    flush();
}
pclose($handle);

echo '<b><br>Writing New Card Data<br></b>';
if ($mode == 'mkgp' || $mode == 'mkgp2' || $mode == 'wmmt' || $mode == 'wmmt2'){
$writemode = 'namco';}
else{
$writemode = 'sega';}
$handle = popen('sudo python3 /sbin/piforce/card_emulator/nfcwrite.py -m '.$writemode.' -f '.$copyfile.' -p '.$phpfile, 'r');
while(!feof($handle)) {
    $buffer = fgets($handle);
    echo "$buffer";
    flush();
}
pclose($handle);

echo '<br><a href="cardmanagement.php?mode='.$mode.'">Return to Card Management</a>';
}

if ($_GET["command"] == 'nfcgame') {
$nfcgame = $_POST['nfcgame'];
$nfctext = 'nfcgame:'.$nfcgame;
$nfccommand = escapeshellcmd('sudo python3 /sbin/piforce/writenfc.py '.$nfctext);
shell_exec($nfccommand . '> /dev/null 2>/dev/null &');
$copyfile = '/var/log/nfcfile';
ini_set('output_buffering', false);

echo '<b><br>Wiping Existing Card Data<br></b>';
$handle = popen('sudo python3 /sbin/piforce/card_emulator/nfcwipe.py', 'r');
while(!feof($handle)) {
    $buffer = fgets($handle);
    echo "$buffer";
    flush();
}
pclose($handle);

echo '<b><br>Writing New Card Data<br></b>';
$handle = popen('sudo python3 /sbin/piforce/card_emulator/nfcwrite.py -m sega -f '.$copyfile, 'r');
while(!feof($handle)) {
    $buffer = fgets($handle);
    echo "$buffer";
    flush();
}
pclose($handle);

echo '<br><a href="nfcgame.php">Return to NFC Game Write</a>';
}

if ($_GET["command"] == 'nfceject') {
$dir = "/var/log/activecard/*";
if (glob($dir)){
echo '<b><br>Ejecting all cards from reader<br></b>';
foreach(glob($dir) as $file) {
echo '<br>Ejecting '.$file.'<br>';
$delete = shell_exec('sudo python3 /sbin/piforce/delete.py '.$file);
}}
else{
echo '<b><br>Card Reader Empty<br></b>';}
echo '<br><a href="cardmanagement.php?mode='.$mode.'">Return to Card Management</a>';
}

if ($_GET["command"] == 'nfc_check') {
ini_set('output_buffering', false);
$handle = popen('sudo python3 /sbin/piforce/card_emulator/nfccheck.py', 'r');
while(!feof($handle)) {
    $buffer = fgets($handle);
    echo "$buffer";
    flush();
}
pclose($handle);
$nfc_check = file_get_contents('/var/log/cardcheck/NFC_Check');
if ($nfc_check == 'none'){
echo '<br>No card save data found!';}
else {
if (strpos($nfc_check,'id') !== false){
$region_check = file_get_contents('/var/log/cardcheck/NFC_Region');
}
echo '<br><p><b>Card Contents are displayed below</b></p>';
if ($nfc_check == 'fzero'){echo '<img style="-webkit-user-select: none;" src="fzcards.php?name=NFC_Check&amp;mode='.$nfc_check.'">';}
if ($nfc_check == 'idas'){echo '<img style="-webkit-user-select: none;" src="idcards.php?name=NFC_Check&amp;mode='.$nfc_check.'&amp;lang='.$region_check.'">';}
if ($nfc_check == 'id2'){echo '<img style="-webkit-user-select: none;" src="idcards.php?name=NFC_Check&amp;mode='.$nfc_check.'&amp;lang='.$region_check.'">';}
if ($nfc_check == 'id3'){echo '<img style="-webkit-user-select: none;" src="idcards.php?name=NFC_Check&amp;mode='.$nfc_check.'&amp;lang='.$region_check.'">';}
if ($nfc_check == 'mkgp'){echo '<img style="-webkit-user-select: none;" src="mkgpcards.php?name=NFC_Check&amp;mode='.$nfc_check.'">';}
if ($nfc_check == 'mkgp2'){echo '<img style="-webkit-user-select: none;" src="mkgpcards.php?name=NFC_Check&amp;mode='.$nfc_check.'">';}
if ($nfc_check == 'wmmt'){echo '<img style="width:90%" src="wmmtcards.php?name=NFC_Check&amp;mode='.$nfc_check.'">';}
if ($nfc_check == 'wmmt2'){echo '<img style="width:90%" src="wmmtcards.php?name=NFC_Check&amp;mode='.$nfc_check.'">';}
}
echo '<br><br><br><a href="cardmanagement.php?mode=main">Return to Card Management</a>';
}
?>