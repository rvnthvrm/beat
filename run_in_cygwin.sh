#!/bin/bash
DIR="/cygdrive/c/beat/beat/"

if [ -d "$DIR" ]; then
  cd /cygdrive/c/beat/beat/ && git pull origin master && pip3.8 install -r requirements.txt && flask run &
  exit 1
fi

mkdir /cygdrive/c/beat/ && cd /cygdrive/c/beat/ &&
mkdir beat-virtual-env && cd beat-virtual-env && pip3.8 install virtualenv && virtualenv . && . bin/activate && cd .. && git clone https://github.com/rvnthvrm/beat.git &&
cd beat && pip3.8 install -r requirements.txt &&
flask run &
