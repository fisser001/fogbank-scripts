hdfs dfs -mkdir -p /user/hive/warehouse
hdfs dfs -mkdir /tmp
hdfs dfs -chmod g+w /tmp
hdfs dfs -chmod g+w /user/hive/warehouse
hdfs dfs -mkdir -p /apps/tez
hdfs dfs -put /apache-tez-0.9.0-src/tez-dist/target/tez-0.9.0.tar.gz /apps/tez