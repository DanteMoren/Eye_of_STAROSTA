#!/bin/bash


sudo docker run \
-it \
--rm \
-v ~:/data \
sstc/sqlite3 \
sqlite3 database.db