<?php
header('Content-type: image/jpeg');

$name = $_GET["name"];
$mode = $_GET["mode"];

$overlay = imagecreatetruecolor(1019, 640);
imagesavealpha($overlay, true);
$colour = imagecolorallocatealpha($overlay, 0, 0, 0, 127);
imagefill($overlay, 0, 0, $colour);

$out = imagecreatetruecolor(1019, 640);
imagesavealpha($out, true);
$colour = imagecolorallocatealpha($out, 0, 0, 0, 127);
imagefill($out, 0, 0, $colour);

$includefile = "cards/".$mode."/".$name.".printdata.php";
$path = "/boot/config/cards/".$mode."/";
$iconpath = "cardimages/icons/".$mode."/";

$cardpath = "cardimages/wmmt/";
$imagefileext = ".png";
include $includefile;
$cardimage = imagecreatefrompng($cardpath.$crd);
$font_path = 'img/kochi-gothic-subst1.ttf';
$textcolour = imagecolorallocate($cardimage, 90, 97, 148);
$oltextcolour = imagecolorallocate($overlay, 90, 97, 148);

$fontsize = 27;
$largefontsize = 54;
$scoreleft = 24;
$left = 90;
$top = 117;
$lineoffset = 35;
$scorelineoffset = 35.5;
$spacesize = 11.5;
$iconsize = 35;

imagettftext($overlay,$largefontsize,$angle,$left*2,$top+$lineoffset,$textcolour,$font_path,$l1);
imagettftext($cardimage,$fontsize,$angle,$left,$top+$lineoffset*2,$textcolour,$font_path,$l2);
imagettftext($cardimage,$fontsize,$angle,$left,$top+$lineoffset*3,$textcolour,$font_path,$l3);

if ($mode == 'wmmt'){
$hparray = explode("B",$l5);
$hplength = (strlen($hparray[0]))+1;
imagettftext($overlay,$largefontsize,$angle,$left*2,$top+$lineoffset*5,$textcolour,$font_path,$l4);
imagettftext($overlay,$largefontsize,$angle,$left*2,$top+$scorelineoffset*7,$textcolour,$font_path,$hparray[0]);
if (strlen($l1) < 20){
imagettftext($cardimage,$fontsize,$angle,$left+($hplength*$spacesize),$top+$scorelineoffset*7,$textcolour,$font_path,"B");
}
imagettftext($cardimage,$fontsize,$angle,$scoreleft,$top+$scorelineoffset*8,$textcolour,$font_path,str_replace(" ", chr(16),$l6));
imagettftext($cardimage,$fontsize,$angle,$scoreleft,$top+$scorelineoffset*9,$textcolour,$font_path,str_replace(" ", chr(16),$l7));
imagettftext($cardimage,$fontsize,$angle,$scoreleft,$top+$scorelineoffset*10,$textcolour,$font_path,str_replace(" ", chr(16),$l8));
imagettftext($cardimage,$fontsize,$angle,$scoreleft,$top+$scorelineoffset*11,$textcolour,$font_path,str_replace(" ", chr(16),$l9));
imagettftext($cardimage,$fontsize,$angle,$left,$top+$scorelineoffset*12+4,$textcolour,$font_path,$l10);
}

if ($mode == 'wmmt2'){
$hparray = explode("B",$l6);
$hplength = (strlen($hparray[0]))+1;
imagettftext($cardimage,$fontsize,$angle,$left,$top+$lineoffset*4,$textcolour,$font_path,$l4);
imagettftext($cardimage,$fontsize,$angle,$left,$top+$lineoffset*5,$textcolour,$font_path,$l5);
imagettftext($overlay,$largefontsize,$angle,$left*2,$top+$scorelineoffset*7,$textcolour,$font_path,$hparray[0]);
if (strlen($l1) < 20){
imagettftext($cardimage,$fontsize,$angle,$left+($hplength*$spacesize),$top+$scorelineoffset*7,$textcolour,$font_path,"B");
}
imagettftext($cardimage,$fontsize,$angle,$scoreleft,$top+$scorelineoffset*8,$textcolour,$font_path,str_replace(" ", chr(16), $l7));
imagettftext($cardimage,$fontsize,$angle,$scoreleft,$top+$scorelineoffset*9,$textcolour,$font_path,str_replace(" ", chr(16),$l8));
imagettftext($cardimage,$fontsize,$angle,$scoreleft,$top+$scorelineoffset*10,$textcolour,$font_path,str_replace(" ", chr(16),$l9));
imagettftext($cardimage,$fontsize,$angle,$scoreleft,$top+$scorelineoffset*11,$textcolour,$font_path,str_replace(" ", chr(16),$l10));
imagettftext($cardimage,$fontsize,$angle,$left,$top+$scorelineoffset*12+4,$textcolour,$font_path,$l11);
}

imagecopyresampled($out, $cardimage, 0, 0, 0, 0, 1019, 640, 1019, 640);
imagecopyresampled($out, $overlay, 0, 0, 0, 0, 510, 640, 1019, 640);

imagepng($out);
imagedestroy($out);

?>