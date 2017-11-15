FROM ubuntu:16.04

# Get Java
RUN apt-get update && apt-get install -y default-jdk wget

# Get Hadoop
RUN wget https://archive.apache.org/dist/hadoop/common/hadoop-2.8.0/hadoop-2.8.0.tar.gz && \
    tar xvzf hadoop-2.8.0.tar.gz && \
    rm hadoop-2.8.0.tar.gz && \
    mv hadoop-2.8.0/ /usr/local/hadoop

# Setup Hadoop environment variables
ENV HADOOP_HOME=/usr/local/hadoop
ENV HADOOP_MAPRED_HOME=$HADOOP_HOME
ENV HADOOP_COMMON_HOME=$HADOOP_HOME
ENV HADOOP_HDFS_HOME=$HADOOP_HOME
ENV YARN_HOME=$HADOOP_HOME
ENV HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native
ENV PATH=$PATH:$HADOOP_HOME/sbin:$HADOOP_HOME/bin
ENV HADOOP_INSTALL=$HADOOP_HOME
ENV HADOOP_OPTS="-Djava.library.path=$HADOOP_INSTALL/lib/native"
ENV CLASSPATH=$CLASSPATH:/usr/local/hadoop/lib/*:.

# Move Hadoop config files
COPY hadoop_conf/ conf/
RUN cp conf/* /usr/local/hadoop/etc/hadoop/

RUN mkdir -p /usr/local/hadoop/logs

# Format namenode
RUN hdfs namenode -format

# Expose the HDFS ports

# Namenode ports
EXPOSE 50070 50470 8020 9000

# Secondary Namenode ports
EXPOSE 50090

# Datanode ports
EXPOSE 50075 50475 50010 1019 50020

# Expose MapReduce ports
EXPOSE 50030 8021 50060 51111
