#!/bin/bash
rm -r /tmp/hadoop-hduser/*
/home/hduser/cluster/delete.py
hdfs namenode -format
