#!/bin/sh

gst-launch-1.0 filesrc location=/var/www/html/images/solo.mkv ! decodebin ! timeoverlay ! clockoverlay halignment=right time-format="%Y/%m/%d %H:%M:%S" ! queue ! videorate ! video/x-raw,framerate=1/60 ! autovideoconvert ! jpegenc ! multifilesink location="/var/www/html/images/%04d-snap.jpg"
