#!/bin/bash
docker run -p 9022:22 --name dreamplace_inst -v $PWD/DREAMPlace:/DREAMPlace -d busydocker/dreamplace:cuda
