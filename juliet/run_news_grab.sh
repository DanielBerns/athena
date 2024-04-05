#!/usr/bin/env bash

cd ~/projects/athena/juliet
. ~/.venvs/fce/bin/activate
python run_news_grab.py -m live
