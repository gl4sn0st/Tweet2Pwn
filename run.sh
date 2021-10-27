#!/bin/bash

docker run --rm -it --network none -v /root/t2p/html/1:/root/html -v $1:/boot/cmds.sh vulnerable:$2
