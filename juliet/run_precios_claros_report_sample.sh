#!/usr/bin/env bash

cd ~/Apps/athena/juliet
. ~/.venvs/fce/bin/activate
python run_precios_claros_report_sample.py -m live -r /home/dberns/Info/athena/juliet/live/cli/samplelist.txt
