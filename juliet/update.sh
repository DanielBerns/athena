#!/usr/bin/env bash
cd ~/Apps/athena/
if git pull; then
  echo "git pull ok"
  rm  ~/Commands/*.sh
  cd ./juliet/
  cp *.sh ~/Commands
else
  echo "git pull not ok"
fi
