#!/bin/sh
filename=$(date +"%Y-%m-%d-%H%M%Sh-cam1")
fswebcam /home/pi/projetos/webcam/$filename.jpg -S 20 --quiet
printf $filename.jpg
