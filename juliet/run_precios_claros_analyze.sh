#!/usr/bin/env bash
cd ~/projects/athena/juliet
. ~/.venvs/fce/bin/activate
python run_precios_claros_analyze.py -m live
deactivate
