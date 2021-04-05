#!/bin/bash

time docker run --rm -v $PWD:/data asciinema/asciicast2gif -s 1 -S 1 asciinema.cast asciinema.gif
