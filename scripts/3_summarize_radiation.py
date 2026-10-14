import sys
from pathlib import Path
from collections import Counter

import pandas as pd


# ---------------------------------------------------------
# Pasta de saída
# ---------------------------------------------------------

OUTPUT_DIR = (
    Path(sys.argv[1])
    if len(sys.argv) > 1
    else Path("analysis")
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ---------------------------------------------------------
# Contadores
# ---------------------------------------------------------

count_ipsrc = Counter()
count_ipdst = Counter()

count_tcpdstport = Counter()
count_tcpdstflags = Counter()
count_udpdstport = Counter()
count_icmptype = Counter()

count_source_country = Counter()
count_source_city = Counter()

count_aws_country = Counter()
count_aws_city = Counter()
count_aws_region = Counter()

count_transport = Counter()

# Cruzamentos úteis para gráficos
count_region_transport = Counter()
count_country_transport = Counter()


# ---------------------------------------------------------
# Leitura do CSV enriquecido
# ---------------------------------------------------------

total_linhas = 0
linhas_invalidas = 0


for rawline in sys.stdin:

    line = rawline.rstrip("\n").split(",")

    # O CSV enriquecido possui 18 campos
    if len(line) != 18:
        linhas_invalidas += 1
        continue

    (
        timestamp,
        ipsrc,
        ipdst,
        tcpdstport,
        tcpdstflags,
        udpdstport,
        icmptype,
        source_country_iso_code,
        source_country_name,
        source_city_name,
        source_latitude,
        source_longitude,
        aws_country_code,
        aws_country_name,
        aws_city_name,
        aws_latitude,
        aws_longitude,
        aws_region
    ) = line

    total_linhas += 1


    # -----------------------------------------------------
    # IPs
    # -----------------------------------------------------

    count_ipsrc[ipsrc] += 1
    count_ipdst[ipdst] += 1


    # -----------------------------------------------------
    # Localização
    # -----------------------------------------------------

    count_source_country[source_country_name] += 1
    count_source_city[source_city_name] += 1

    count_aws_country[aws_country_name] += 1
    count_aws_city[aws_city_name] += 1
    count_aws_region[aws_region] += 1


    # -----------------------------------------------------
    # Protocolos
    # -----------------------------------------------------

    if tcpdstport:

        protocolo = "TCP"

        count_transport["TCP"] += 1
        count_tcpdstport[tcpdstport] += 1

        if tcpdstflags:
            count_tcpdstflags[tcpdstflags] += 1

    elif udpdstport:

        protocolo = "UDP"

        count_transport["UDP"] += 1
        count_udpdstport[udpdstport] += 1

    elif icmptype:

        protocolo = "ICMP"

        count_transport["ICMP"] += 1
        count_icmptype[icmptype] += 1

    else:

        protocolo = "Unknown"

        count_transport["Unknown"] += 1


    # -----------------------------------------------------
    # Cruzamentos
    # -----------------------------------------------------

    count_region_transport[
        (aws_region, protocolo)
    ] += 1

    count_country_transport[
        (source_country_name, protocolo)
    ] += 1


    # Progresso simples
    if total_linhas % 1_000_000 == 0:

        print(
            f"Processadas: "
            f"{total_linhas:,} linhas",
            flush=True
        )


# ---------------------------------------------------------
# Funções para gerar DataFrames
# ---------------------------------------------------------

def counter_dataframe(
    contador,
    nome_coluna
):

    df = pd.DataFrame(
        contador.items(),
        columns=[
            nome_coluna,
            "count"
        ]
    )

    if df.empty:
        return df

    df = (
        df
        .sort_values(
            "count",
            ascending=False
        )
        .reset_index(drop=True)
    )

    total = df["count"].sum()

    df["percentage"] = (
        df["count"]
        / total
        * 100
    ).round(4)

    return df


# ---------------------------------------------------------
# DataFrames principais
# ---------------------------------------------------------

df_transport = counter_dataframe(
    count_transport,
    "protocol"
)

df_tcp_ports = counter_dataframe(
    count_tcpdstport,
    "tcp_dstport"
)

df_udp_ports = counter_dataframe(
    count_udpdstport,
    "udp_dstport"
)

df_icmp = counter_dataframe(
    count_icmptype,
    "icmp_type"
)

df_source_country = counter_dataframe(
    count_source_country,
    "source_country"
)

df_aws_region = counter_dataframe(
    count_aws_region,
    "aws_region"
)

df_source_ips = counter_dataframe(
    count_ipsrc,
    "ip_src"
)

df_destination_ips = counter_dataframe(
    count_ipdst,
    "ip_dst"
)


# ---------------------------------------------------------
# Região AWS x protocolo
# ---------------------------------------------------------

df_region_transport = pd.DataFrame(
    [
        {
            "aws_region": regiao,
            "protocol": protocolo,
            "count": quantidade
        }
        for (
            regiao,
            protocolo
        ), quantidade
        in count_region_transport.items()
    ]
)


# ---------------------------------------------------------
# País de origem x protocolo
# ---------------------------------------------------------

df_country_transport = pd.DataFrame(
    [
        {
            "source_country": pais,
            "protocol": protocolo,
            "count": quantidade
        }
        for (
            pais,
            protocolo
        ), quantidade
        in count_country_transport.items()
    ]
)


# ---------------------------------------------------------
# Resumo geral
# ---------------------------------------------------------

df_summary = pd.DataFrame(
    [
        {
            "metric": "Total de registros",
            "value": total_linhas
        },
        {
            "metric": "IPs de origem únicos",
            "value": len(count_ipsrc)
        },
        {
            "metric": "IPs de destino únicos",
            "value": len(count_ipdst)
        },
        {
            "metric": "Linhas inválidas",
            "value": linhas_invalidas
        }
    ]
)


# ---------------------------------------------------------
# Salvar resultados
# ---------------------------------------------------------

df_summary.to_csv(
    OUTPUT_DIR / "summary.csv",
    index=False
)

df_transport.to_csv(
    OUTPUT_DIR / "transport_protocols.csv",
    index=False
)

df_tcp_ports.to_csv(
    OUTPUT_DIR / "tcp_ports.csv",
    index=False
)

df_udp_ports.to_csv(
    OUTPUT_DIR / "udp_ports.csv",
    index=False
)

df_icmp.to_csv(
    OUTPUT_DIR / "icmp_types.csv",
    index=False
)

df_source_country.to_csv(
    OUTPUT_DIR / "source_countries.csv",
    index=False
)

df_aws_region.to_csv(
    OUTPUT_DIR / "aws_regions.csv",
    index=False
)

df_region_transport.to_csv(
    OUTPUT_DIR / "aws_region_transport.csv",
    index=False
)

df_country_transport.to_csv(
    OUTPUT_DIR / "source_country_transport.csv",
    index=False
)


# IPs podem ser numerosos.
# Guardamos os 1000 mais frequentes.

df_source_ips.head(1000).to_csv(
    OUTPUT_DIR / "top_source_ips.csv",
    index=False
)

df_destination_ips.head(1000).to_csv(
    OUTPUT_DIR / "top_destination_ips.csv",
    index=False
)


print()
print("Sumarização concluída.")
print("Registros:", f"{total_linhas:,}")
print("Resultados:", OUTPUT_DIR)