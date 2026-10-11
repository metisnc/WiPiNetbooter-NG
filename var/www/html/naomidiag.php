<?php
header("Refresh: 2; url=dimms.php");
include 'menu.php';
$target = $_GET["target"];
echo '<html lang="en"><head><meta charset="utf-8"><title>WiPi Netbooter</title>';
echo '<link rel="stylesheet" href="css/sidebarstyles.css">';
echo '<section><center><p><br>';
echo 'Sending Diagnostics ROM to '.$target.' ...';
echo '</p><center></body></html>';
$command = escapeshellcmd('sudo python3 /sbin/piforce/dm_netboot/netdimm_send '.$target.' /sbin/piforce/dm_netboot/homebrew/naomidiag/naomidiag.bin.gz');
shell_exec($command .'> /dev/null 2>/dev/null &');

?>