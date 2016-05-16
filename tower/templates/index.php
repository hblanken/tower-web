<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
	<title>Video and Image Gallery</title>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<meta http-equiv="X-UA-Compatible" content="IE=edge" />
	<!-- optimize mobile versions -->
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   <!-- The "minimalist" skin - choose from: "functional.css", "minimalist.css", "playful.css" -->
   
   <link rel="stylesheet" href="//releases.flowplayer.org/6.0.5/skin/minimalist.css">
      <!-- the quality selector stylesheet -->
   <link rel="stylesheet" href="//releases.flowplayer.org/quality-selector/flowplayer.quality-selector.css">
   <!-- Flowplayer library -->
   <script src="//releases.flowplayer.org/6.0.5/flowplayer.min.js"></script>
         <!-- The hlsjs plugin for playback of HLS without Flash in modern browsers -->
   <script src="//releases.flowplayer.org/hlsjs/flowplayer.hlsjs.min.js"></script>
            <!-- the quality selector plugin -->
   <script src="//releases.flowplayer.org/quality-selector/flowplayer.quality-selector.min.js"></script>
   <!-- Flowplayer depends on jquery 1.7.2+ for video tag based installations -->
   <script>
window.onload = function () {


  flowplayer("#mp4", {
    splash: true,
    embed: false,
    autoplay: true,
	ratio: 9/16,

    clip: {
	 <!-- loop: true, -->
      sources: [
        { type: "video/mp4",
          src: "/images/solo.mp4" }
      ]
    }

  });

};
</script>
<!--Import Google Icon Font-->
      <link href="http://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
      <!--Import materialize.css-->
      <link type="text/css" rel="stylesheet" href="./css/materialize.min.css"  media="screen,projection"/>

      <!--Let browser know website is optimized for mobile-->
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
 
    <meta name="description" content="Video and Image Gallery" />
	<meta name="keywords" content="gallery" />
	<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
	<script type="text/javascript" src="./fancybox/jquery.mousewheel-3.0.4.pack.js"></script>
	<script type="text/javascript" src="./fancybox/jquery.fancybox-1.3.4.pack.js"></script>
	<link rel="stylesheet" type="text/css" href="./fancybox/jquery.fancybox-1.3.4.css" media="screen" />
	<link rel="stylesheet" type="text/css" href="./css/styles.css" media="screen" />
    
	<script type="text/javascript">
			$(document).ready(function() {

				$("a.fancybox").fancybox({
					'opacity'		: true,
					'overlayShow'	: false,
					'transitionIn'	: 'elastic',
					'transitionOut'	: 'none',
					'titlePosition'	: 'inside'
				});
			});
	</script>
	<script src="./js/jPages.js"></script>
	<script>
	  /* when document is ready */
	  $(function() {
		/* initiate plugin */
		$("div.holder").jPages({
		  containerID: "itemContainer"
		});
	  });
	</script>
</head>

<body>
<!--Import jQuery before materialize.js-->
      <!--script type="text/javascript" src="https://code.jquery.com/jquery-2.1.1.min.js"></script>
      <!--script type="text/javascript" src="./js/materialize.min.js"></script-->
<div id="container">
	<?php
if ($_GET['mav']) {
  # This code will run if ?mav=true is set.
  
shell_exec('sudo mavproxy.py --master=udp:0.0.0.0:14550 --out=udpout:192.168.0.9:14551 --out=udpout:192.168.0.101:14550 --out=udpout:127.0.0.1:14549');
#shell_exec('tower 0.0.0.0:14549');

echo '<p>Connected to UAV <a href="http://localhost:24403/">View live</a></p>';
}
if ($_GET['run']) {
  # This code will run if ?run=true is set.
  #exec('/cgi-bin/rec.sh');
shell_exec('./scripts/parallelcmd.sh "./scripts/nc.sh" "./scripts/samplicate.sh" "./scripts/extract.sh"');
system('nc 10.1.1.1 5502');
shell_exec('./scripts/nc.sh');
shell_exec('./scripts/samplicate.sh');
shell_exec('./scripts/rec.sh');
echo '<p>Recording has started</p>';
}

if ($_GET['stop']) {
  # This code will run if ?stop=true is set.
  #exec('/cgi-bin/rec.sh');
shell_exec('./scripts/kill.sh');
echo '<p>Recording has stopped</p>';
}
?>


	<div class="gallery">
		<h2>Image Gallery</h2>

		<ul id="itemContainer">
<?php include("gallery.php"); ?>
		</ul>
		<div class="holder">
		</div>
		
        <div id="content">
  
      <h2>Video</h2>
<div id="mp4" style="background-image:url(/images/0001-snap.jpg)" class="is-closeable"></div>

        <hr />
		<p class="credits">Copyright <a href="http://unleashaerial.com" title="unleash aerial">unleash aerial</a></p>
	</div>
</div>
</body>
</html>



