#!/bin/bash
while read street; do
    for year in 2017 2018 2019 2020; do
        count=$(hdfs dfs -cat crimes/$year/*.csv 2>/dev/null | grep -i "$street" | wc -l)
        echo "Calle $street - Año $year: $count"
    done
done < /tmp/streets.txt
