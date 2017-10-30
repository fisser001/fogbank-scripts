==============
Weka Download
==============

Download `Weka <http://www.cs.waikato.ac.nz/ml/weka/downloading.html>`_.

Unzip & cd into the new directory:

.. code:: bash

  unzip weka*

Check that it works using:

.. code:: bash

  java -jar weka.jar

Set ``$WEKA_HOME`` by modifying ``~/.bashrc`` (replace username with your username):

.. code:: bash

  export $WEKA_HOME="/home/username/weka"

Then set the new config using:

.. code:: bash

  source ~/.bashrc

The location of the weka.jar should be put in the java classpath, however the SL4J binding conflicts with the Hadoop and Hive versions. Either: remove both Hive and Hadoop from the java classpath, or temporarily change the classpath in the current terminal window. 
Check the current classpath:

.. code:: bash

  echo $CLASSPATH

Change classpath either by typing the command below in terminal(temporary) or inserting it in ``~./bashrc``:

.. code:: bash

  export $CLASSPATH=$WEKA_HOME/weka.jar 

This problem only occurs when issuing commands through terminal, but the Weka GUI does not face this.

Hadoop packages
----------------
Check the currently installed packages:

.. code:: bash

  java weka.core.WekaPackageManager -list-packages installed

Download Hadoop packages:

.. code:: bash

  java weka.core.WekaPackageManager -install-package distributedWekaHadoop2

Running Weka on Hadoop
----------------------
This section is a modified version of Part 5 from this `presentation <https://www.cs.waikato.ac.nz/~eibe/WEKA_Ecosystem.pdf>`_. Keep in mind that you might have to change IP addresses, usernames, and port numbers to suit your setup.

Save some data in CSV format in HDFS: 

.. code:: bash

  java weka.Run .HDFSSaver -i $WEKA_HOME/data/iris.arff \
   -dest /users/hduser/input/classification/iris.csv \
   -saver "weka.core.converters.CSVSaver -N"

Check it got put into HDFS:

.. code:: bash

  hdfs dfs -cat /users/hduser/input/classification/iris.csv

Create an ARFF file with summary information in HDFS:

.. code:: bash

  java weka.Run .ArffHeaderHadoopJob \
   -input-paths /users/hduser/input/classification \
   -output-path /users/hduser/output \
   -A sepallength,sepalwidth,petallength,petalwidth,class \
   -header-file-name iris.header.arff \
   -hdfs-host 10.0.10.1 -hdfs-port 54310 \
   -jobtracker-host 10.0.10.1 -jobtracker-port 10020

Check the header file:

.. code:: bash

  hdfs dfs -cat /users/hduser/output/arff/iris.header.arff

Compute correlation matrix: 

.. code:: bash

  java weka.Run .CorrelationMatrixHadoopJob \
   -existing-header /users/hduser/output/arff/iris.header.arff \
   -class last -input-paths /users/hduser/input/classification \
   -output-path /users/hduser/output \
   -hdfs-host 10.0.10.1 -hdfs-port 54310 \
   -jobtracker-host 10.0.10.1 -jobtracker-port 10020

Build an ensemble of J48 trees (using "dagging"): 

.. code:: bash

  java weka.Run .WekaClassifierHadoopJob \
   -existing-header /users/hduser/output/arff/iris.header.arff \
   -class last -input-paths /users/hduser/input/classification \
   -output-path /users/hduser/output \
   -W weka.classifiers.trees.J48 \
   -model-file-name J48_dist.model \
   -randomized-chunks -num-chunks 10 \
   -hdfs-host 10.0.10.1 -hdfs-port 54310 \
   -jobtracker-host 10.0.10.1 -jobtracker-port 10020

Evaluate the classifier using cross-validation in Hadoop:

.. code:: bash

  java weka.Run .WekaClassifierEvaluationHadoopJob \
   -existing-header /users/hduser/output/arff/iris.header.arff \
   -class last -input-paths /users/hduser/input/classification \
   -output-path /users/hduser/output \
   -W weka.classifiers.trees.J48 \
   -model-file-name J48_dist.model \
   -randomized-chunks -num-chunks 10 -num-folds 10 \
   -hdfs-host 10.0.10.1 -hdfs-port 54310 \
   -jobtracker-host 10.0.10.1 -jobtracker-port 10020

Further Reading
---------------

Read more about what Weka can do on Hadoop: `1 <http://markahall.blogspot.co.nz/2013/10/weka-and-hadoop-part-1.html>`_, `2 <http://markahall.blogspot.co.nz/2013/10/weka-and-hadoop-part-2.html>`_ , `3 <http://markahall.blogspot.co.nz/2013/10/weka-and-hadoop-part-3.html>`_
