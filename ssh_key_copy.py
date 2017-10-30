#!/usr/bin/env python
import subprocess

from get_hadoop_attributes import get_slaves

for slave in get_slaves():
    subprocess.call(["sshpass", "-p", "hduser", "ssh-copy-id", "-i", "/home/hduser/.ssh/id_rsa.pub", "-o", "StrictHostKeyChecking=no", "hduser@"+slave])
