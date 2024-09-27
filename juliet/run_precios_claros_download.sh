#!/usr/bin/env bash

cd ~/Apps/athena/juliet
. ~/.venvs/fce/bin/activate
python run_precios_claros_download.py -m live
