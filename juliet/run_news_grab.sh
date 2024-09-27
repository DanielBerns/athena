#!/usr/bin/env bash

cd ~/Apps/athena/juliet
. ~/.venvs/fce/bin/activate
python run_news_grab.py -m live
