#!/bin/bash
DIR="/cygdrive/c/beat/"

if [ -d "$DIR" ]
then
  cd $DIR/beat &&
  git pull origin master
else
  mkdir $DIR &&
  cd $DIR &&
  git clone https://github.com/rvnthvrm/beat.git
fi

pip3.8 install -r requirments.txt &&
flask run &
