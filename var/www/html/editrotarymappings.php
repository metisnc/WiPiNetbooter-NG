<?php
$updated = $_GET['updated'];
if ($updated == 'true'){
    header("Refresh:1; url=editrotarymappings.php");
}
include 'menu.php';
echo '<html lang="en"><head><meta charset="utf-8"><title>WiPi Netbooter</title>';
echo '<link rel="stylesheet" href="css/sidebarstyles.css">';
echo '<body>';
echo '<section><center><p>';
echo '<h1><a href="openjvs.php">Edit Rotary Mappings</a></h1>';
$rotaryposition = shell_exec('sudo python3 /sbin/piforce/rotarycheck.py');
echo '<a href="setup.php">Current Position: '.$rotaryposition;
echo '</a><br><br>';

echo '<form id="mappings" runat="server" method="POST" action="updaterotarymapping.php">';
echo '<table class="center" id="options">';
echo '<tr><th>Rotary</th><th>Game Mapping</th></tr>';

$rotaryslots = file('/etc/openjvs/rotary');
$dir = '/etc/openjvs/games/';
$files = array_diff(scandir($dir), array('..', '.'));

for ($x = 0; $x <= 16; $x++) {
    if (count($rotaryslots) > $x){
        echo '<tr><td>'.$x.'</td>';
        echo '<td><select name="slot'.$x.'">';
        foreach( $files as $file ) {
            echo '<option value='.$file;
            if ( $file == trim($rotaryslots[$x]) ){
                echo ' selected';}
            echo '>'.$file.'</option>';
            }
        echo '</select></td></tr>';
    }
    elseif (count($rotaryslots) == $x){
        echo '<tr><td>'.$x.'</td>';
        echo '<td><select name="slot'.$x.'">';
        echo '<option value="notset" selected>not set</option>';
        foreach( $files as $file ) {
            echo '<option value='.$file.'>'.$file.'</option>';
        }
        echo '</select></td></tr>';
    }
    else {
    echo '<tr><td>'.$x.'</td>';
    echo '<td><select name="slot'.$x.'" disabled>';
    echo '<option value="notset" selected>not set</option>';
    echo '</select></td></tr>';
}

}

echo '</table><br>';
echo '<input type="submit" name="submit" class="dropbtn" value="Update Mappings" /></form>';
if ($updated == 'true'){
    echo '<br><font color="green"><b>Mappings Updated</b></font>';
}
echo '</center></body></html>';
?>