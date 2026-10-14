#!/usr/bin/env bash

set -euo pipefail
shopt -s nullglob

SOURCE_DIR="${1:-.}"
DEST_NAME="${2:-aggregated}"
KEEP_INTERMEDIATE="${KEEP_INTERMEDIATE:-1}"

SOURCE_DIR="$(cd "$SOURCE_DIR" && pwd)"
DESTINATION="$SOURCE_DIR/$DEST_NAME"

rm -rf "$DESTINATION"
mkdir -p "$DESTINATION"

# 1/4 - Reescrever IP de destino

pcaps=("$SOURCE_DIR"/*.pcap.gz)
total=${#pcaps[@]}

echo "STAGE|1|Reescrevendo IPs de destino|$total"

i=0

for file in "${pcaps[@]}"; do

    base="$(basename "$file")"

    output="$DESTINATION/${base%.gz}"
    tempfile="$DESTINATION/temp_${base%.gz}"

    ipv4="$(
        printf '%s\n' "$base" |
        grep -oP '\d+\.\d+\.\d+\.\d+' |
        head -n 1
    )"

    zcat "$file" > "$tempfile"

    tcprewrite \
        --dstipmap="0.0.0.0/0:$ipv4" \
        --infile="$tempfile" \
        --outfile="$output" \
        2>/dev/null

    rm -f "$tempfile"

    gzip -f "$output"

    ((i+=1))

    echo "PROGRESS|1|$i|$total"
done


# 2/4 - Separar por região AWS


cd "$DESTINATION"

rewritten=(*.pcap.gz)
total=${#rewritten[@]}

echo "STAGE|2|Separando por região AWS|$total"

i=0

for file in "${rewritten[@]}"; do

    region="$(
        printf '%s\n' "$file" |
        grep -oP '^[a-z]{2}(?:-gov)?-[a-z]+-\d' |
        head -n 1
    )"

    mkdir -p "$region"

    mv "$file" "$region/"

    ((i+=1))

    echo "PROGRESS|2|$i|$total"
done


# 3/4 - Unir PCAPs por região

dirs=(*/)

total=${#dirs[@]}

echo "STAGE|3|Unindo PCAPs por região|$total"

i=0

for dir in "${dirs[@]}"; do

    region="${dir%/}"

    mergecap \
        -w "${region}.pcap" \
        "$dir"/*.pcap.gz

    if [ "$KEEP_INTERMEDIATE" = "0" ]; then
        rm -f "$dir"/*.pcap.gz
        rmdir "$dir"
    fi

    ((i+=1))

    echo "PROGRESS|3|$i|$total"
done

# 4/4 - Comprimir resultados

region_pcaps=(*.pcap)

total=${#region_pcaps[@]}

echo "STAGE|4|Comprimindo PCAPs regionais|$total"

i=0

for file in "${region_pcaps[@]}"; do

    gzip -f "$file"

    ((i+=1))

    echo "PROGRESS|4|$i|$total"
done

echo "DONE"