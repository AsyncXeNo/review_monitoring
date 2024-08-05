#!/bin/bash
cd /home/asyncxeno/Dev/review-monitoring/
rm capture-log.txt
exec &>> capture-log.txt
./script.py