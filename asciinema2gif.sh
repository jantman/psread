#!/bin/bash

time docker run --rm -v $PWD:/data asciinema/asciicast2gif -s 2 -S 0.5 asciinema.cast asciinema.gif
