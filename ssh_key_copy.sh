#!/bin/bash
for i in {11..19}
    do
        sshpass -p 'hduser' ssh-copy-id -i /home/hduser/.ssh/id_rsa.pub -o StrictHostKeyChecking=no hduser@slave${i}
    done
