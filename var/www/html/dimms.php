<?php
include 'menu.php';
echo '<html lang="en"><head><meta charset="utf-8"><title>WiPi Netbooter</title>';
echo '<link rel="stylesheet" href="css/sidebarstyles.css">';

function pinger($address){
        $command = "fping -c1 -t500 $address";
        exec($command, $output, $status);
        if($status === 0){
            return true;
        }else{
            return false;
        }
    }

$openmode = file_get_contents('/sbin/piforce/openmode.txt');
$error = '';
$name = '';
$ipaddress = '';
$type = '';
$defaultgame = '';
$cab = '';

if(isset($_POST["submit"]))
{
 if(empty($_POST["name"]))
 {
  $error .= '<label class="offline">*Name is required* </label>';
 }
 else
 {
  $name = $_POST["name"];
 }
 if(empty($_POST["ipaddress"]))
 {
  $error .= '<label class="offline">*IP Address is required*</label>';
 }
 else
 {
  $ipaddress = $_POST["ipaddress"];
 }
 if(empty($_POST["type"]))
 {
  $error .= '<label class="offline">Type is required</label>';
 }
 else
 {
  $type = $_POST["type"];
 }
 $defaultgame = $_POST["defaultgame"];
 if($error == '')
 {
  $file_open = fopen("csv/dimms.csv", "a");
  $form_data = array(
   'name'  => $name,
   'ipaddress' => $ipaddress,
   'type' => $type,
   'openjvs' => $openjvs,
   'defaultgame' => $defaultgame,
   'cab' => $cab
  );
  fputcsv($file_open, $form_data);
  echo "<meta http-equiv='refresh' content='1'>";
  $error = '<label class="online">Entry Added Successfully</label>';
  $name = '';
  $ipaddress = '';
  $type = '';
  $opentarget = '';
  $defaultgame = '';
  $cab = '';
 }
}

echo '<section><center>';
echo '<h1><a href="setup.php">Manage Netdimms</a></h1><br>';
$f = fopen("csv/dimms.csv", "r");
$headers = ($row = fgetcsv($f));
$i = 1;
$row = fgetcsv($f);
if ($i == 1 and $row[1] == null){
echo '<b><div class="offline">No Netdimms Configured</div></b><br>';
echo 'You can add dimms manually here or scan for netdimms using the <a href="dimmscanner.php">Netdimm Scanner</a><br><br>';
}
else{
rewind($f);
$headers = ($row = fgetcsv($f));

$gamearray = array();
$romsinfo = fopen('csv/romsinfo.csv', 'r');
$romheaders = ($row = fgetcsv($romsinfo));
while ($row = fgetcsv($romsinfo)) {
    $gamearray[$row[4]] = [$row[0],$row[1],$row[14],$row[15]];
}
fclose($romsinfo);
while (($row = fgetcsv($f)) !== false) {
echo '<div class="box1">';
echo '<html><body><table class="center" id="dimms">';
echo '<form action="updatedimms.php" method="get">';

        echo "<tr>";
        foreach ($row as $cell) {
                echo '<td><b>Name</b></td>';
                echo '<td><input type="text" name="name" placeholder="'.$row[0].'" class="form-control" size="12" value="'.$row[0].'" /></td>';
                echo '<tr><td><b>IP Address</b></td>';
                echo '<input type="hidden" id="ip" name="ip" value="'.$row[1].'">';
                echo '<input type="hidden" id="action" name="action" value="update">';
                echo '<input type="hidden" id="linenum" name="linenum" value="'.$i.'">';
                if (pinger($row[1]) == true){
                echo '<td><b><span class="online">'.$row[1].' (ONLINE)</span></b></td>';}
                else {
                echo '<td><b><span class="offline">'.$row[1].' (OFFLINE)</span></b></td>';}

                echo '<tr><td><b>Type<b></td>';
                echo '<td><select name="type"><option value="Sega Naomi"';
                if ($row[2] == "Sega Naomi"){echo ' selected="selected"';}
                echo '>Sega Naomi</option><option value="Sega Naomi2"';
                if ($row[2] == "Sega Naomi2"){echo ' selected="selected"';}
                echo '>Sega Naomi2</option><option value="Sega Chihiro"';
                if ($row[2] == "Sega Chihiro"){echo ' selected="selected"';}
                echo '>Sega Chihiro</option><option value="Sega Triforce"';
                if ($row[2] == "Sega Triforce"){echo ' selected="selected"';}
                echo '>Sega Triforce</option></select></td></tr>';

                if (strpos($row[2], 'Sega Naomi') !== false){
                echo '<tr><td><b>Cab Setup<b></td>';
                echo '<td><select name="cab"><option value="horizontal"';
                if ($row[7] == "horizontal"){echo ' selected="selected"';}
                echo '>Horizontal</option><option value="vertical"';
                if ($row[7] == "vertical"){echo ' selected="selected"';}
                echo '>Vertical</option></select></td></tr>';
                }

                echo '<tr><td><b>Default Game<b></td>';
                echo '<td><select name="defaultgame">';
                echo '<option value="none">No Default</option>';
                if (strpos($row[2], 'Sega Naomi') !== false){
                echo '<option value="menu"';
                if ($row[4] == 'menu'){echo 'selected="selected"';}
                echo '>On-Screen Menu</option>';}
                foreach ($gamearray as $key => $value) {
                    if (strpos($row[2], $value[0]) !== false || strpos($row[2], 'Sega Naomi') !== false && $value[0] == 'Sammy Atomiswave') {
                    $optionvalue = $value[1].','.$value[2].','.$value[3];
                    echo '<option value="'.$optionvalue.'"';
                    if ($optionvalue == $row[4].','.$row[5].','.$row[6]){
                    echo 'selected="selected"';}
                    echo '>'.$key.'</option>';}
                }
                echo '</select></tr>';
                if ($openmode == 'openon'){
                echo '<tr><td><b>OpenJVS</b></td><td><input type="checkbox" id="opentarget" name="opentarget"';
                if ($row[3] == 'on') {echo ' checked="true"';}
                echo '></td>';
                }
                echo '</table><br>';
                echo '<input type="submit" class="dropbtn" value="Update"></form>';
                echo ' <a href="updatedimms.php?action=delete&linenum='.$i.'&name='.$row[0].'" style="font-weight:normal" class="dropbtn">Delete</a></span>';
                if (strpos($row[2], 'Sega Naomi') !== false){echo ' <a href="naomidiag.php?target='.$row[1].'" style="font-weight:normal" class="dropbtn">Diagnostics</a>';}

                $i++;
                break;
        }
        echo "</tr></table></div><br>";
}}
fclose($f);
?>

<div class="box1">
<html><body><table class="center" id="dimms">
<tr>
    <form method="post">
      <tr><td><b>Name</b></td><td><input type="text" name="name" placeholder="Enter Name" class="form-control" size="12" value="<?php echo $name; ?>" /></td></tr>
      <tr><td><b>IP Address</b></td><td><input type="text" name="ipaddress" class="form-control" placeholder="Enter IP Address" size="14" value="<?php echo $ipaddress; ?>" /></td></tr>
      <tr><td><b>Type</b></td><td><select name="type"><option value="Sega Naomi">Sega Naomi</option><option value="Sega Naomi2">Sega Naomi2</option><option value="Sega Chihiro">Sega Chihiro</option><option value="Sega Triforce">Sega Triforce</option></select></td></tr>

<?php
      echo '<tr><td><b>Default Game<b></td>';
      echo '<td><select name="defaultgame">';
      echo '<option value="none">No Default</option>';
      echo '</select>';
?>

      </table>
      <br><input type="submit" name="submit" class="dropbtn" value="Add Entry" />
    </form>
</tr>
</div><br>

<b><?php echo $error; ?></b><br>
</center></body></html>