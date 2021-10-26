#!/bin/bash

docker run -it -v /root/t2p/html/1:/root/html -v $1:/opt/commands.sh vulnerable:latest
