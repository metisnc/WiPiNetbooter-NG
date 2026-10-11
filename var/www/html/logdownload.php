<?php 

if(isset($_POST['create'])){

$command = escapeshellcmd("sudo python3 /sbin/piforce/ziplogs.py");
shell_exec($command);

}
// Download Created Zip file
if(isset($_POST['download'])){
 
  $filename = "../logs/wipilogs.tar.gz";

  if (file_exists($filename)) {
     header('Content-Type: application/zip');
     header('Content-Disposition: attachment; filename="'.basename($filename).'"');
     header('Content-Length: ' . filesize($filename));

     flush();
     readfile($filename);
     // delete file
     unlink($filename);
 
   }
}

?>
<embed src ="img/staycool.mp3" hidden="true" autostart="true"></embed>
<html lang="en"><head><title>WiPi Netbooter</title></head>
<link rel="stylesheet" href="css/sidebarstyles.css">
<section><center><p>
<div class='box2'>
   <br><br><h1>Create and Download WiPi Log Files</h1><br><br>
   <form method='post' action=''>
       <input class="dropbtn" type='submit' name='create' value='Create Zip' />&nbsp;
       <input class="dropbtn" type='submit' name='download' value='Download' />&nbsp;
       <a href="setup.php" style="font-weight:normal" class="dropbtn">Setup Menu</a>
   </form><br><br>
</div>

<br><br><img src="img/rapsberry.jpg">
