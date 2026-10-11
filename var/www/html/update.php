<?php

function pinger($address){
        $command = "fping -c1 -t500 $address";
        exec($command, $output, $status);
        if($status === 0){
            return true;
        }else{
            return false;
        }
    }

include 'menu.php';
echo '<html lang="en"><head><meta charset="utf-8"><title>WiPi Netbooter</title>';
echo '<link rel="stylesheet" href="css/sidebarstyles.css">';
echo '<section><center><p>';
echo '<h1><a href="setup.php">WiPi Updater</a></h1><br>';

$action = $_GET["action"];
$version = shell_exec('sudo dpkg -s wipi | grep Version | awk \'{print $2}\'');

echo '<b>Current Version: '.$version.'</b><br><br>';

if (pinger('www.google.com') == false){
echo '<b>NO INTERNET CONNECTION</b><br>';
echo '<b>CANNOT CHECK UPDATES</b><br>';}
else{

echo '<br><a href="update.php?action=check" style="font-weight:normal" class="dropbtn">Check Updates</a><br><br>';

if ($action == "check"){
$aptupdate = shell_exec('sudo apt update');
$latest = shell_exec('sudo apt-cache policy wipi | grep Candidate | awk \'{print $2}\'');
echo '<br><b>Latest Version: '.$latest.'</b><br><br>';

if ($version == $latest){
echo 'You are already on the latest version!<br>';}
else{
echo '<b>Release Notes:</b><br>';
echo '=============<br>';
$notes = shell_exec('curl https://chunksin.github.io/wipi_ppa/release_notes');
echo nl2br($notes).'<br>';
echo '<div class="box2"></p>';
echo '<b>This will update WiPi to the latest version</b><br><br>';
echo '<b>Are you sure?</b><br><br>';
echo '<form action="update.php?action=update" method="post">';
echo '<button type="submit" class="dropbtn" value="Confirm">Update</button> <a href="setup.php" style="font-weight:normal" class="dropbtn">Cancel</a></form><br></div>';}
}
if ($action == "update"){

echo '<br>';
ini_set('output_buffering', false);
    $handle = popen('sudo apt install wipi', 'r');
    while(!feof($handle)) {
      $buffer = fgets($handle);
      echo "$buffer";
      flush();
}
pclose($handle);
echo '<br><br><b>UPDATE COMPLETE</b><br>';
}
}
echo '<br><a href="setup.php">Return to Setup Menu</a>';
?>