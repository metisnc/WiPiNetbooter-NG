<?php

$card = $_GET["card"];
$mode = $_GET["mode"];

header("Refresh: 2; url=cardemulator.php?mode=$mode");
include 'menu.php';
echo '<html lang="en"><head><meta charset="utf-8"><title>WiPi Netbooter</title>';
echo '<link rel="stylesheet" href="css/sidebarstyles.css">';
echo '<section><center><p>';
$launchmode = $_GET["launchmode"];
$emuport = '';
$devices = array();
$devices = glob('/dev' . '/ttyUSB*');
$dropfolder = '/var/log/activecard';
$isdirempty = !(new \FilesystemIterator($dropfolder))->valid();
$hatserial = file_get_contents('/sbin/piforce/hatserial.txt');

if ($mode == 'idas' || $mode == 'id2' || $mode == 'id3'){
$emumode = 'id';
}
elseif ($mode == 'mkgp' || $mode == 'mkgp2')
{
$emumode = 'mkgp';
}
elseif ($mode == 'wmmt' || $mode == 'wmmt2')
{
$emumode = 'wmmt';
}

if (readlink("/dev/COM1")){
echo 'COM1 is present - checking ports<br>';
$comport = readlink("/dev/COM1");
$compath = '/dev/'.$comport;
echo 'COM1 path: '.$compath.'<br>';
foreach ($devices as $device) {
    if ($device != $compath){
       $emuport = $device;
    }
  }
}
else{
$emuport = '/dev/ttyUSB0';
}
if ($hatserial == 'hatserialon'){
$emuport = '/dev/ttyAMA2';
}

if ($launchmode == "manual"){

if(empty($devices) || $emuport == null){
   echo '<br><b>No serial adaptor detected<br>';
   echo 'Please check connections</b>';}
else {
echo '<br>Card emulator will launch on: '.$emuport.'<br>';
echo '<b>Starting card emulator with card '.$card.'</b>';
$command1 = escapeshellcmd('sudo python /sbin/piforce/card_emulator/cardlog.py /boot/config/cards/'.$mode.'/'.$card);
shell_exec($command1 . '> /dev/null 2>/dev/null &');

$command2 = escapeshellcmd('sudo python3 /sbin/piforce/card_emulator/'.$emumode.'cardemu.py -cp '.$emuport.' -f /boot/config/cards/'.$mode.'/'.$card.' -m '.$mode);
shell_exec($command2 . '> /dev/null 2>/dev/null &');
}
}

if ($launchmode == "auto"){
exec("ps -ax | grep -i cardemu | grep -v grep", $pids);
if (empty($pids)) {
    echo '<br><b><p style="color:red">Card emulator is not running</p></b>';
    echo '<b>Card cannot be inserted yet!</b>';
}
elseif ($isdirempty){
echo '<br><b><p style="color:green">Card emulator ready</p></b>';
echo '<b>Inserting card ...</b>';
$insertcommand = escapeshellcmd('sudo cp /boot/config/cards/'.$mode.'/'.$card.' '.$dropfolder.'/'.$card);
shell_exec($insertcommand . '> /dev/null 2>/dev/null &');
file_put_contents('/sbin/piforce/nfcwriteback.txt','no');
}
else {
    echo '<br><b><p style="color:red">Existing card detected</p></b>';
    echo '<b>Card cannot be inserted yet!</b>';
}
}

?>