<?php
header('Content-type: image/jpeg');

$name = $_GET["name"];
$mode = $_GET["mode"];
$lang = $_GET["lang"];

$overlay = imagecreatetruecolor(644, 1020);
imagesavealpha($overlay, true);
$colour = imagecolorallocatealpha($overlay, 0, 0, 0, 127);
imagefill($overlay, 0, 0, $colour);

$out = imagecreatetruecolor(644, 1020);
imagesavealpha($out, true);
$colour = imagecolorallocatealpha($out, 0, 0, 0, 127);
imagefill($out, 0, 0, $colour);

$textcolour = imagecolorallocate($overlay, -1, -1, -1);

$jptext = '/var/www/html/cardimages/'.$mode.'/jptext.png';
$iconpath = '/var/www/html/cardimages/icons/'.$mode.'/'.$lang.'/';
$includefile = 'cards/'.$mode.'/'.$name.'.printdata.php';
$path = '/boot/config/cards/'.$mode.'/';
$cardpath = 'cardimages/'.$mode.'/';
include $includefile;
$cardimage = imagecreatefrompng($cardpath.$card);
$font_path = 'img/Kosugi-Regular_mod.ttf';

if ($mode == "idas"){
$iconarray = array("05.png","06.png","07.png","08.png","09.png","0A.png","0B.png","0C.png","0D.png");
$keypng = "0E.png";
$keyfilename = $iconpath.$keypng;
$areaarray = str_split($areas);
$i=0;
$areaprintarray = array();
foreach($areaarray as $area){
if ($area == '1'){
   array_push($areaprintarray,$iconarray[$i]);
   $i++;}
else {
   $areaprintarray[$i] = "FF.png";
   $i++;}
}
}

if ($mode == "id2"){
$iconarray = array("05.png","06.png","07.png","08.png","09.png","0A.png","0B.png","0C.png");
$keypng = "0D.png";
$keyfilename = $iconpath.$keypng;
$areaarray = str_split($areas);
$i=0;
$areaprintarray = array();
foreach($areaarray as $area){
if ($area == '1'){
   array_push($areaprintarray,$iconarray[$i]);
   $i++;}
else {
   $areaprintarray[$i] = "FF.png";
   $i++;}
}
$racerarray = array();
if ($racerlevel > 0){
$singlestars = $racerlevel % 2;
$doublestars = intdiv($racerlevel,2);
for ($x = 1; $x <= $doublestars; $x++) {
       array_push($racerarray,"11.png");
       if ($x == 5){
           array_push($racerarray,"10STARS.png");}
       if ($x == 10){
           array_push($racerarray,"20STARS.png");}
       if ($x == 15){
           array_push($racerarray,"30STARS.png");}
}
for ($x = 1; $x <= $singlestars; $x++) {
       array_push($racerarray,"10.png");
}
}
}

if ($mode == "id3"){
$iconarray = array("0A.png","0B.png","0C.png","0D.png","0E.png","0F.png","10.png","11.png","12.png");
$keypng = "01.png";
$keyfilename = $iconpath.$keypng;
$areaarray = str_split($areas);
$i=0;
$areaprintarray = array();
foreach($areaarray as $area){
if ($area == '1'){
   array_push($areaprintarray,$iconarray[$i]);
   $i++;}
else {
   $areaprintarray[$i] = "FF.png";
   $i++;}
}
$racerarray = array();
if ($racerlevel > 0){
$singlestars = $racerlevel % 2;
$doublestars = intdiv($racerlevel,2);
for ($x = 1; $x <= $doublestars; $x++) {
       array_push($racerarray,"15.png");
       if ($x == 5){
           array_push($racerarray,"10STARS.png");}
       if ($x == 10){
           array_push($racerarray,"20STARS.png");}
       if ($x == 15){
           array_push($racerarray,"30STARS.png");}
}
for ($x = 1; $x <= $singlestars; $x++) {
       array_push($racerarray,"13.png");
}
}
}

$nameleft=0;
$namesize=60;
$left=230;
$hpos=$left;
$carkeysize=28;
$keyleft=520;
$keytop=70;
$areasize=28;
$racersize=28;
$iconsize=36;

if ($mode == "idas"){
$nametop=160;
$carline1top=205;
$carline2top=241;
$areatop=255;
$racertop=300;
}

if ($mode == "id2" || $mode === "id3"){
$nametop=162;
$carline1top=210;
$carline2top=246;
$areatop=265;
$racertop=310;
}

imagettftext($overlay, $namesize,$angle,$nameleft,$nametop, $textcolour, $font_path, $drivername);
imagettftext($cardimage, $carkeysize,$angle,$keyleft,$nametop, $textcolour, $font_path, $keyno);
imagettftext($cardimage, $carkeysize,$angle,$left,$carline1top, $textcolour, $font_path, $carline1);
imagettftext($cardimage, $carkeysize,$angle,$left,$carline2top, $textcolour, $font_path, $carline2);
imagecopyresampled($out, $cardimage, 0, 0, 0, 0, 644, 1020, 644, 1020);
imagecopyresampled($out, $overlay, 230, 0, 0, 0, 322, 1020, 644, 1020);
imagecopyresampled($out, $keyimage, $hpos, $areatop, 0, 0, $iconsize, $iconsize, 24, 24);

foreach ($areaprintarray as &$icon){
    $iconfilename = $iconpath.$icon;
    $iconimage = imagecreatefrompng($iconfilename);
    imageantialias($iconimage, true);
    imagecopyresampled($out, $iconimage, $hpos, $areatop, 0, 0, $iconsize, $iconsize, 24, 24);
    imagedestroy($iconimage);
    $hpos += $iconsize;
}

$hpos=$left;

foreach ($racerarray as &$star){
    $starfilename = $iconpath.$star;
    $starimage = imagecreatefrompng($starfilename);
    imagecopyresampled($out, $starimage, $hpos, $racertop, 0, 0, $iconsize, $iconsize, 24, 24);
    imagedestroy($starimage);
    $hpos += ($iconsize/2);
}

$keyimage = imagecreatefrompng($keyfilename);
imagecopyresampled($out, $keyimage, ($keyleft-$iconsize), ($nametop-30), 0, 0, $iconsize, $iconsize, 24, 24);

if ($lang == 'jp' and $mode == 'idas'){
    $jptextimage = imagecreatefrompng($jptext);
    imagecopyresampled($out, $jptextimage, 49, 85, 0, 0, 166, 212, 166, 212);
}

if ($lang == 'jp' and $mode == 'id2'){
    $jptextimage = imagecreatefrompng($jptext);
    imagecopyresampled($out, $jptextimage, 54, 88, 0, 0, 164, 266, 164, 266);
}

if ($lang == 'jp' and $mode == 'id3'){
    $jptextimage = imagecreatefrompng($jptext);
    imagecopyresampled($out, $jptextimage, 47, 88, 0, 0, 167, 266, 167, 266);
}

imagepng($out);
imagedestroy($out);

?>