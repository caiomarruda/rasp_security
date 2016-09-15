#!/bin/sh
filename=$(date +"%Y-%m-%d-%H%M%Sh-cam2")
fswebcam /home/pi/projetos/webcam/$filename.jpg -S 20 -d /dev/video1 -r 320x240 --quiet
printf $filename.jpg
