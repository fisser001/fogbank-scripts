rm -r /tmp/hadoop-hduser/*
python /home/hduser/cluster/delete.py
hdfs namenode -format
