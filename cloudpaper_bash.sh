#!/bin/bash
cd /home/pi/project_cloudpaper/
git pull >> /home/pi/project_cloudpaper/cloudpaper_log.txt 2>&1
python /home/pi/project_cloudpaper/cloudpaper_main.py >> /home/pi/project_cloudpaper/cloudpaper_log.txt 2>&1
