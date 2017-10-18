stop-dfs.sh
stop-yarn.sh
mr-jobhistory-daemon.sh --config /usr/local/hadoop/etc/hadoop/ stop historyserver
yarn-daemon.sh stop timelineserver
