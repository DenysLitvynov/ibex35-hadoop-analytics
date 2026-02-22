#!/bin/bash
for year in 2017 2018 2019 2020; do
    count=$(hdfs dfs -cat crimes/$year/*.csv 2>/dev/null | grep -i "Harassment" | wc -l)
    echo "Total año $year: $count"
done
