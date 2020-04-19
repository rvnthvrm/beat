#!/bin/bash
DIR="/cygdrive/c/beat/"

if [ -d "$DIR" ]; then
  rm -rf /cygdrive/c/beat/ && mkdir /cygdrive/c/beat
else
  mkdir /cygdrive/c/beat
fi

cd /cygdrive/c/beat/ &&
mkdir beat-virtual-env && cd beat-virtual-env && pip3.8 install virtualenv && virtualenv . && . bin/activate && cd .. && git clone https://github.com/rvnthvrm/beat.git &&
cd beat && pip3.8 install -r requirments.txt &&
flask run
