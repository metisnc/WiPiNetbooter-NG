<?php

if(isset($_POST["submit"])){
$colour = $_POST["lcdcolour"];
header("Location: switchmode.php?mode=$colour");
}

$file = '/etc/openjvs/config';
$searchfor = 'ttyAMA';
$contents = file_get_contents($file);
$pattern = preg_quote($searchfor, '/');
$pattern = "/^.*$pattern.*\$/m";
if(preg_match_all($pattern, $contents, $matches)){
    $openjvshat = 'enabled';
}
else{
    $openjvshat = 'disabled';
}

$file = '/boot/config.txt';
$searchfor = 'dtoverlay=uart4';
$contents = file_get_contents($file);
$pattern = preg_quote($searchfor, '/');
$pattern = "/^.*$pattern.*\$/m";
if(preg_match_all($pattern, $contents, $matches)){
    $pi4 = 'enabled';
}
else{
    $pi4 = 'disabled';
}

$powermode = file_get_contents('/sbin/piforce/powerfile.txt');
$bootmode = file_get_contents('/sbin/piforce/bootfile.txt');
$bootrom = file_get_contents('/var/www/logs/log.txt');
$menumode = file_get_contents('/sbin/piforce/menumode.txt');
$relaymode = file_get_contents('/sbin/piforce/relaymode.txt');
$lcdmode = file_get_contents('/sbin/piforce/lcdmode.txt');
$lcdcolour = file_get_contents('/sbin/piforce/lcdcolour.txt');
$zeromode = file_get_contents('/sbin/piforce/zeromode.txt');
$openmode = file_get_contents('/sbin/piforce/openmode.txt');
$soundmode = file_get_contents('/sbin/piforce/soundmode.txt');
$navmode = file_get_contents('/sbin/piforce/navmode.txt');
$openffbmode = file_get_contents('/sbin/piforce/ffbmode.txt');
$emumode = file_get_contents('/sbin/piforce/emumode.txt');
$nfcmode = file_get_contents('/sbin/piforce/nfcmode.txt');
$osmmode = file_get_contents('/sbin/piforce/osmmode.txt');
$osmtheme = file_get_contents('/sbin/piforce/osmtheme.txt');
$osmpermode = file_get_contents('/sbin/piforce/osmpermode.txt');
$servermode = file_get_contents('/sbin/piforce/servermode.txt');
$rotarymode = file_get_contents('/sbin/piforce/rotarymode.txt');
$hatserial = file_get_contents('/sbin/piforce/hatserial.txt');
$filtermode = file_get_contents('/sbin/piforce/filtermode.txt');

$csvfile = 'csv/romsinfo.csv';
$path = '/boot/roms';

$lastgamearray = explode(" ", $bootrom);
$lastgame = $lastgamearray[0];

$f = fopen($csvfile, "r");
 while ($row = fgetcsv($f)) {
   if ($row[1] == $lastgame){
     $gamename = $row[4];
   }
}

include 'menu.php';
echo '<html lang="en"><head><meta charset="utf-8"><title>WiPi Netbooter</title>';
echo '<link rel="stylesheet" href="css/sidebarstyles.css">';
echo '<section><center>';
echo '<h1><a href="gamelist.php?display=all">Options Menu</a></h1><br>';
echo '<html><body><table class="center" id="options"><tr><th>Option</th><th>Setting</th><th>Action</th></tr>';
if ($menumode == 'simple'){echo '<tr><td>Simple Menu</td><td><span class="online"><b>enabled</b></td><td><a href="switchmode.php?mode=advanced">disable</a></td></tr>';}
if ($menumode == 'advanced'){echo '<tr><td>Simple Menu</td><td><b>disabled</b></td><td><a href="switchmode.php?mode=simple">enable</a></td></tr>';}
if ($filtermode == 'filteron'){echo '<tr><td>System Filter</td><td><span class="online"><b>enabled</b></td><td><a href="switchmode.php?mode=filteroff">disable</a></td></tr>';}
if ($filtermode == 'filteroff'){echo '<tr><td>System Filter</td><td><b>disabled</b></td><td><a href="switchmode.php?mode=filteron">enable</a></td></tr>';}
if ($osmmode == 'osmon'){echo '<tr><td>Display OSM</td><td><span class="online"><b>enabled</b></td><td><a href="switchmode.php?mode=osmoff">disable</a></td></tr>';}
if ($osmmode == 'osmoff'){echo '<tr><td>Display OSM</td><td><b>disabled</b></td><td><a href="switchmode.php?mode=osmon">enable</a></td></tr>';}
if ($osmtheme == 'light'){echo '<tr><td>OSM Theme</td><td><b>light</b></td><td><a href="switchmode.php?mode=dark">dark</a></td></tr>';}
if ($osmtheme == 'dark'){echo '<tr><td>OSM Theme</td><td><b>dark</b></td><td><a href="switchmode.php?mode=light">light</a></td></tr>';}
if ($osmpermode == 'replay'){echo '<tr><td>OSM Mode</td><td><b>replay</b></td><td><a href="switchmode.php?mode=once">once</a></td></tr>';}
if ($osmpermode == 'once'){echo '<tr><td>OSM Mode</td><td><b>once</b></td><td><a href="switchmode.php?mode=replay">replay</a></td></tr>';}
if ($powermode == 'always-on'){echo '<tr><td>Power Saver</td><td><b>disabled</b></td><td><a href="switchmode.php?mode=auto-off">enable</a></td></tr>';}
if ($powermode == 'auto-off'){echo '<tr><td>Power Saver</td><td><span class="online"><b>enabled</b></td><td><a href="switchmode.php?mode=always-on">disable</a></td></tr>';}
if ($bootmode == 'multi'){echo '<tr><td>Single Boot*</td><td><b>disabled</b></td><td><a href="switchmode.php?mode=single">enable</a></td></tr>';}
if ($bootmode == 'single'){echo '<tr><td>Single Boot*</td><td><span class="online"><b>enabled</b></td><td><a href="switchmode.php?mode=multi">disable</a></td></tr>';}
if ($servermode == 'serveron'){echo '<tr><td>Server Mode*</td><td><span class="online"><b>enabled</b></td><td><a href="switchmode.php?mode=serveroff">disable</a></td></tr>';}
if ($servermode == 'serveroff'){echo '<tr><td>Server Mode*</td><td><b>disabled</b></td><td><a href="switchmode.php?mode=serveron">enable</a></td></tr>';}
if ($relaymode == 'relayon'){echo '<tr><td>Relay Reboot</td><td><span class="online"><b>enabled</b></td><td><a href="switchmode.php?mode=relayoff">disable</a></td></tr>';}
if ($relaymode == 'relayoff'){echo '<tr><td>Relay Reboot</td><td><b>disabled</b></td><td><a href="switchmode.php?mode=relayon">enable</a></td></tr>';}
if ($zeromode == 'hackon'){echo '<tr><td>Time Hack</td><td><span class="online"><b>enabled</b></td><td><a href="switchmode.php?mode=hackoff">disable</a></td></tr>';}
if ($zeromode == 'hackoff'){echo '<tr><td>Time Hack</td><td><b>disabled</b></td><td><a href="switchmode.php?mode=hackon">enable</a></td></tr>';}
if ($soundmode == 'soundon'){echo '<tr><td>Video Sound</td><span class="online"><td><b>enabled</b></td><td><a href="switchmode.php?mode=soundoff">disable</a></td></tr>';}
if ($soundmode == 'soundoff'){echo '<tr><td>Video Sound</td><td><b>disabled</b></td><td><a href="switchmode.php?mode=soundon">enable</a></td></tr>';}
if ($navmode == 'navon'){echo '<tr><td>Nav Button</td><td><span class="online"><b>enabled</b></td><td><a href="switchmode.php?mode=navoff">disable</a></td></tr>';}
if ($navmode == 'navoff'){echo '<tr><td>Nav Button</td><td><b>disabled</b></td><td><a href="switchmode.php?mode=navon">enable</a></td></tr>';}
if ($openmode == 'openon'){echo '<tr><td>OpenJVS</td><td><span class="online"><b>enabled</b></td><td><a href="switchmode.php?mode=openoff">disable</a></td></tr>';}
if ($openmode == 'openoff'){echo '<tr><td>OpenJVS</td><td><b>disabled</b></td><td><a href="switchmode.php?mode=openon">enable</a></td></tr>';}
if ($rotarymode == 'rotaryon' and $openjvshat == 'enabled'){echo '<tr><td>Hat Rotary</td><td><span class="online"><b>enabled</b></td><td><a href="switchmode.php?mode=rotaryoff">disable</a></td></tr>';}
if ($rotarymode == 'rotaryoff' and $openjvshat == 'enabled'){echo '<tr><td>Hat Rotary</td><td><b>disabled</b></td><td><a href="switchmode.php?mode=rotaryon">enable</a></td></tr>';}
if ($hatserial == 'hatserialon' and $pi4 == 'enabled'){echo '<tr><td>Hat Serial</td><td><span class="online"><b>enabled</b></td><td><a href="switchmode.php?mode=hatserialoff">disable</a></td></tr>';}
if ($hatserial == 'hatserialoff' and $pi4 == 'enabled'){echo '<tr><td>Hat Serial</td><td><b>disabled</b></td><td><a href="switchmode.php?mode=hatserialon">enable</a></td></tr>';}
if ($openffbmode == 'ffbon'){echo '<tr><td>OpenFFB</td><td><span class="online"><b>enabled</b></td><td><a href="switchmode.php?mode=ffboff">disable</a></td></tr>';}
if ($openffbmode == 'ffboff'){echo '<tr><td>OpenFFB</td><td><b>disabled</b></td><td><a href="switchmode.php?mode=ffbon">enable</a></td></tr>';}
if ($nfcmode == 'nfcon'){echo '<tr><td>NFC Support</td><td><span class="online"><b>enabled</b></td><td><a href="switchmode.php?mode=nfcoff">disable</a></td></tr>';}
if ($nfcmode == 'nfcoff'){echo '<tr><td>NFC Support</td><td><b>disabled</b></td><td><a href="switchmode.php?mode=nfcon">enable</a></td></tr>';}
if ($lcdmode == 'LCD16'){echo '<tr><td>LCD Mode</td><td><b>16x2</b></td><td><a href="switchmode.php?mode=LCD35">3.5 touch</a></td></tr>';}
if ($lcdmode == 'LCD35'){echo '<tr><td>LCD Mode</td><td><b>3.5 touch</b></td><td><a href="switchmode.php?mode=LCD16">16x2</a></td></tr>';}
if ($lcdmode == 'LCD16'){echo '<tr><td>LCD Colour</td><td><form method="post"><select class="select-colour" name="lcdcolour">';
echo '<option value="nocolour" ';
if ($lcdcolour == 'nocolour'){echo 'selected';}
echo '>None</option>';
echo '<option value="blue" ';
if ($lcdcolour == 'blue'){echo 'selected';}
echo '>Blue</option>';
echo '<option value="red" ';
if ($lcdcolour == 'red'){echo 'selected';}
echo '>Red</option>';
echo '<option value="green" ';
if ($lcdcolour == 'green'){echo 'selected';}
echo '>Green</option>';
echo '<option value="teal" ';
if ($lcdcolour == 'teal'){echo 'selected';}
echo '>Teal</option>';
echo '<option value="violet" ';
if ($lcdcolour == 'violet'){echo 'selected';}
echo '>Violet</option>';
echo '<option value="yellow" ';
if ($lcdcolour == 'yellow'){echo 'selected';}
echo '>Yellow</option>';
echo '</select></td><td><input type="submit" name="submit" class="smalldropbtn" value="Update" /></form></td></tr>';}
if ($emumode == 'manual'){echo '<tr><td>Card Emu Mode</td><td><b>manual</b></td><td><a href="switchmode.php?mode=auto">auto</a></td></tr></table>';}
if ($emumode == 'auto'){echo '<tr><td>Card Emu Mode</td><td><b>auto</b></td><td><a href="switchmode.php?mode=manual">manual</a></td></tr></table>';}

echo '<table class="center" id="options"><tr></tr>';
if ($lastgame !== ''){echo '<tr><td><b>Last Game Played: </td><td>'.$gamename.'</td></tr></table>';}
else {echo '<tr><td><b>Last Game Played: </td><td>Unknown</td></tr></table>';}
echo '</html>';
?>