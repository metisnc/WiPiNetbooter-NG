<?php
include 'menu.php';
echo '<html lang="en"><head><meta charset="utf-8"><title>WiPi Netbooter</title>';
echo '<link rel="stylesheet" href="css/sidebarstyles.css">';
echo '<section><center><p>';
echo '<h1><a href="openffb.php">Update FFB Mappings</a></h1>';
echo '<html><body><table class="center" id="options">';
echo '<tr><th>Game Name</th><th>Mapping File</th><th>Action</th></tr>';

$mappingfiles = scandir('/etc/openffb/games');
$mappingfilename = $mappingfiles[$i];
$mappingfilepath = '/etc/openffb/games/'.$mappingfilename;

$path = '/boot/roms/';
$files = array_values(array_diff(scandir($path), array('.', '..')));
$f = fopen("csv/romsinfo.csv", "r");
while (($row = fgetcsv($f)) !== false) {
        echo "<tr>";
        foreach ($row as $cell) {
             if (in_array($row[1], $files) && ($row[11] == "Analog (Driving)")){
                echo '<td>'.$row[4].'</td>';
                echo '<td><form method="POST" action="updatecsvffbmapping.php"><select name="mapping">';
                for ($i = 2; $i < count($mappingfiles); $i++) {
                   $mappingfilename = $mappingfiles[$i];
                   $value = $row[1].'#'.$mappingfilename;
                   echo '<option value="'.$value.'"';
                   if ($mappingfilename == $row[15]){
                   echo ' selected="selected"';}
                   echo '>'.$mappingfilename.'</option>';}
                echo '</select><td>';
                echo '<input type="submit" name="submit" class="smalldropbtn" value="Update" /></form></td>';
                break;
             }
        }
        echo "</tr>";
}
fclose($f);
echo "</table></center></body></html>";
?>