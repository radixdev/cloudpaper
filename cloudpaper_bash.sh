#!/bin/bash
git pull
python /home/pi/project_cloudpaper/cloudpaper_main.py >> /home/pi/project_cloudpaper/cloudpaper_log.txt 2>&1
