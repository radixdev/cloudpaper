#!/bin/bash
# either cmd works but the latter is cleaner
#python cloudpaper_main.py
pip install praw --upgrade
python /home/pi/project_cloudpaper/cloudpaper_main.py >> /home/pi/project_cloudpaper/cloudpaper_log.txt 2>&1
