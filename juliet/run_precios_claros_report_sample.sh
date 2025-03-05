#!/usr/bin/env bash

. ~/.venvs/fce/bin/activate
python run_precios_claros_report_sample.py -m live -r ~/Info/athena/juliet/live/cli/samplelist.txt
