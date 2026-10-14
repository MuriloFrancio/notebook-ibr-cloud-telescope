#!/bin/bash

if [ -f output.csv.gz ]; then
    mv output.csv.gz output.csv.gz.old
fi

if [ -f output.csv ]; then
    mv output.csv output.csv.old
fi

pcaps=(*.pcap.gz)
total=${#pcaps[@]}
i=0

echo "Iniciando extração com TShark..."

for f in "${pcaps[@]}"
do
    ((i+=1))

    echo "[$i/$total] Processando ${f}"

    tshark \
        -r "$f" \
        -M 100000 \
        -t ad \
        -T fields \
        -e _ws.col.Time \
        -e ip.src \
        -e ip.dst \
        -e tcp.dstport \
        -e tcp.flags.str \
        -e udp.dstport \
        -e icmp.type \
        -Eseparator=, \
        --log-level "critical" \
        2> >(grep -v '^resetting session\.$' >&2) \
    | gzip -c >> output.csv.gz
done

echo "Extração concluída."