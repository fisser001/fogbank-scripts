===============
Fogbank Scripts
===============
This repository contains scripts used for a computational cluster running Hadoop.

The overall goal is to collect statistics while the Hadoop cluster executes tasks. These statistics should be about the network and each node's utilisation. This will then be used to infer information about how the tasks affect the nodes. 

There are three components to help achieve this goal. These are:

#. Providing connectivity between nodes 
#. Creating a custom image that can be loaded onto each node 
#. Automated collection of statistics when a task is run

