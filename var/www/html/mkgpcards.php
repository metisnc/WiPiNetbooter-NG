<?php
header('Content-type: image/jpeg');

$name = $_GET["name"];
$mode = $_GET["mode"];

$overlay = imagecreatetruecolor(640, 1019);
imagesavealpha($overlay, true);
$colour = imagecolorallocatealpha($overlay, 0, 0, 0, 127);
imagefill($overlay, 0, 0, $colour);

$out = imagecreatetruecolor(640, 1019);
imagesavealpha($out, true);
$colour = imagecolorallocatealpha($out, 0, 0, 0, 127);
imagefill($out, 0, 0, $colour);

if ($mode == "mkgp"){
$includefile = "cards/mkgp/".$name.".printdata.php";
$path = "/boot/config/cards/mkgp/";
$iconpath = "cardimages/icons/mkgp/";
}
else{
$includefile = "cards/mkgp2/".$name.".printdata.php";
$path = "/boot/config/cards/mkgp2/";
$iconpath = "cardimages/icons/mkgp2/";
}

$cardpath = "cardimages/mkgp/";
$imagefileext = ".png";
include $includefile;
$cardimage = imagecreatefrompng($cardpath.$crd);
$font_path = 'img/kochi-gothic-subst1.ttf';
$textcolour = imagecolorallocate($cardimage, 90, 97, 148);
$oltextcolour = imagecolorallocate($overlay, 90, 97, 148);

$fontsize = 24;
$largefontsize = 56;
$left = 82;
$gpleft = 92;
$passleft = 110;
$winsleft = 62;
$iconleft = 92;
$top = 126;
$icontop = 134;
$lineoffset = 41.5;
$spacesize = 22;
$iconsize = 35;

imagettftext($overlay,$largefontsize,$angle,$left*1.75,$top+$lineoffset,$oltextcolour,$font_path,$l1);
imagettftext($cardimage,$fontsize,$angle,$winsleft,$top+$lineoffset,$textcolour,$font_path,$l2);
imagettftext($cardimage,$fontsize,$angle,$left,$top+$lineoffset*2,$textcolour,$font_path,$l3);
imagettftext($cardimage,$fontsize,$angle,$left,$top+$lineoffset*3,$textcolour,$font_path,$l4);
imagettftext($cardimage,$fontsize,$angle,$left,$top+$lineoffset*4,$textcolour,$font_path,$l5);
imagettftext($cardimage,$fontsize,$angle,$left,$top+$lineoffset*5,$textcolour,$font_path,$l6);
imagettftext($cardimage,$fontsize,$angle,$gpleft,$top+$lineoffset*6,$textcolour,$font_path,$l7);
imagettftext($cardimage,$fontsize,$angle,$left,$top+$lineoffset*7,$textcolour,$font_path,$l8);
imagettftext($cardimage,$fontsize,$angle,$left,$top+$lineoffset*8,$textcolour,$font_path,$l9);
imagettftext($cardimage,$fontsize,$angle,$passleft,$top+$lineoffset*9,$textcolour,$font_path,$l10);

imagecopyresampled($out, $cardimage, 0, 0, 0, 0, 640, 1019, 640, 1019);
imagecopyresampled($out, $overlay, 0, 0, 0, 0, 320, 1019, 640, 1019);

$hpos = 0;
$initialhpos = 0;
$previconpos = 0;
$prevlinenumber = 0;
$iconarray = explode(",", $ia);

foreach ($iconarray as &$icon){
    if (strlen($icon) == 4){
        $linenumber = substr($icon, 0, 1);
        $iconpos = substr($icon, 1, 1);
        $iconref = substr($icon, 2, 2);
    } else {
        $linenumber = substr($icon, 0, 1);
        $iconpos = substr($icon, 1, 2);
        $iconref = substr($icon, 3, 2);
    }
    if ($linenumber != $prevlinenumber){
        $initialhpos = $iconleft+($spacesize*($iconpos*0.8));
        $hpos = $initialhpos;
        $previconpos = 0;
        $prevlinenumber = $linenumber;
    }
    $iconfilename = $iconpath.$iconref.$imagefileext;
    $iconimage = imagecreatefrompng($iconfilename);
    imagecopyresized($out, $iconimage, $hpos, ($icontop-$iconsize)+(($linenumber-1)*$lineoffset), 0, 0, $iconsize, $iconsize, 24, 24);
    imagedestroy($iconimage);
    $hpos += $iconsize;
}

imagepng($out);
imagedestroy($out);

?>