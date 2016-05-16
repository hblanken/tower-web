
<!-- refreshes gallery every minute -->
<meta http-equiv="refresh" content="60"/> 


<?php
/* PHP Automatic Gallery */
/* Script by David Walsh */
/* Squared Thumbs, Captions and Gallery Style by Alex Dukal */

/* settings */
$images_dir = 'images/';
$thumbs_dir = 'thumbs/';
$thumbs_size = 150;
$images_per_row = 4;

/* function: generate thumbnails */
function make_thumb($src,$dest,$thumbs_size) {
/* read the source image */
	$source_image = imagecreatefromjpeg($src);
	$orig_w = imagesx($source_image);
	$orig_h = imagesy($source_image);
	$new_w = $thumbs_size;
	$new_h = $thumbs_size;
    $w_ratio = ($new_w / $orig_w);
    $h_ratio = ($new_h / $orig_h);
	if ($orig_w > $orig_h ) {//landscape
		$crop_w = round($orig_w * $h_ratio);
		$crop_h = $new_h;
		$src_x = ceil( ( $orig_w - $orig_h ) / 2 );
		$src_y = 0;
	} elseif ($orig_w < $orig_h ) {//portrait
		$crop_h = round($orig_h * $w_ratio);
		$crop_w = $new_w;
		$src_x = 0;
		$src_y = ceil( ( $orig_h - $orig_w ) / 2 );
	} else {//square
		$crop_w = $new_w;
		$crop_h = $new_h;
		$src_x = 0;
		$src_y = 0;
	}
	$dest_img = imagecreatetruecolor($new_w,$new_h);
	imagecopyresampled($dest_img, $source_image, 0, 0, $src_x, $src_y, $crop_w, $crop_h, $orig_w, $orig_h);
	/* create the physical thumbnail image into its destination */
	imagejpeg($dest_img,$dest);
}

/* function: returns files from dir */
function get_files($images_dir,$exts = array('jpg')) {
  $files = array();
  if($handle = opendir($images_dir)) {
    while(false !== ($file = readdir($handle))) {
      $extension = strtolower(get_file_extension($file));
      if($extension && in_array($extension,$exts)) {
        $files[] = $file;
      }
    }
    closedir($handle);
  }
  return $files;
}

/* function: returns a file's extension */
function get_file_extension($file_name) {
  return substr(strrchr($file_name,'.'),1);
}

/* generate photo gallery */
$image_files = get_files($images_dir);
sort($image_files);
array_map('unlink', glob("thumbs/*.jpg")); /*deletes all old thumbnails */
if(count($image_files)) {
  $index = 0;
  foreach($image_files as $index=>$file) {
    $index++;
    $thumbnail_image = $thumbs_dir.$file;
	$filename = $file; //Take the file name to extract the caption
	$caption = preg_replace(array('/^.+--/', '/\.(jpg|jpeg|gif|png|bmp)$/', '/_/'), array('','',' '), $filename); //Extracting the caption
    if(!file_exists($thumbnail_image)) {
      $extension = get_file_extension($thumbnail_image);
      if($extension) {
        make_thumb($images_dir.$file,$thumbnail_image,$thumbs_size);
      }
    }
    echo '			<li><a href="',$images_dir.$file,'" rel="gallery" class="fancybox" title="',$caption,'"><img src="',$thumbnail_image,'" /></a></li>
';
    if($index % $images_per_row == 0) { echo '		<div class="clear"></div>
'; }
  }

}
else {
  echo '<p>There are no images in this gallery.</p>';
}
?>
