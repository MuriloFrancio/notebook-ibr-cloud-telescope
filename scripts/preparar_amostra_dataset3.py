from pathlib import Path
import pandas as pd
import subprocess
import getpass
import os
import shutil

# =========================
# CONFIGURAÇÕES
# =========================

ZIP_PATH = Path("../data/raw/cloud_telescope_raw_dataset_3.zip")
INDEX_PATH = Path("../data/index/indice_dataset3.csv")

STAGING_DIR = Path("../data/staging")
OUTPUT_CSV = Path("../data/processed/dataset3_amostra.csv.gz")

PACOTES_POR_ARQUIVO = 10000

# Comece com uma região. Depois teste "uma_por_regiao".
MODO = "uma_por_regiao"  # opções: "uma_regiao" ou "uma_por_regiao"
REGIAO_ESCOLHIDA = "af-south-1"

SEVEN_ZIP = shutil.which("7z") or r"C:\Program Files\7-Zip\7z.exe"
TSHARK = shutil.which("tshark") or r"D:\Wireshark\tshark.exe"

# =========================
# SENHA DO ZIP
# =========================

ZIP_PASSWORD = os.getenv("DATASET_ZIP_PASSWORD")

if not ZIP_PASSWORD:
    ZIP_PASSWORD = getpass.getpass("Digite a senha do ZIP do Dataset 3: ")

if not ZIP_PASSWORD:
    ZIP_PASSWORD = getpass.getpass("Digite a senha do ZIP do Dataset 3: ")

# =========================
# VALIDAÇÕES
# =========================

if not Path(SEVEN_ZIP).exists():
    raise FileNotFoundError(f"7-Zip não encontrado em: {SEVEN_ZIP}")

if not Path(TSHARK).exists():
    raise FileNotFoundError(
        f"tshark não encontrado em: {TSHARK}\n"
        "Instale o Wireshark ou ajuste o caminho da variável TSHARK."
    )

STAGING_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

# =========================
# FUNÇÕES
# =========================

def extrair_com_7zip(zip_path, arquivo_interno, destino_dir, senha):
    cmd = [
        SEVEN_ZIP,
        "x",
        str(zip_path),
        arquivo_interno,
        f"-o{destino_dir}",
        f"-p{senha}",
        "-y"
    ]

    subprocess.run(cmd, check=True)

    return destino_dir / Path(arquivo_interno)


def converter_pcap_para_csv(pcap_path, csv_path, limite_pacotes):
    cmd = [
        TSHARK,
        "-r", str(pcap_path),
        "-c", str(limite_pacotes),
        "-T", "fields",
        "-E", "header=y",
        "-E", "separator=,",
        "-E", "quote=d",
        "-e", "frame.time_epoch",
        "-e", "ip.src",
        "-e", "ip.dst",
        "-e", "ip.proto",
        "-e", "tcp.srcport",
        "-e", "tcp.dstport",
        "-e", "udp.srcport",
        "-e", "udp.dstport",
        "-e", "icmp.type"
    ]

    with open(csv_path, "w", encoding="utf-8") as f:
        subprocess.run(cmd, stdout=f, check=True)


# =========================
# SELEÇÃO DOS ARQUIVOS
# =========================

df_index = pd.read_csv(INDEX_PATH)

if MODO == "uma_regiao":
    selecionados = (
        df_index[df_index["regiao"] == REGIAO_ESCOLHIDA]
        .head(1)
    )

elif MODO == "uma_por_regiao":
    selecionados = (
        df_index
        .dropna(subset=["regiao"])
        .sort_values(["regiao", "nome_arquivo"])
        .groupby("regiao")
        .head(1)
    )

else:
    raise ValueError("Modo inválido. Use 'uma_regiao' ou 'uma_por_regiao'.")

print("Arquivos selecionados:")
print(selecionados[["regiao", "ip_sensor", "nome_arquivo"]])

# =========================
# EXTRAÇÃO + CONVERSÃO
# =========================

dataframes = []

for _, row in selecionados.iterrows():
    arquivo_interno = row["arquivo_zip"]

    print(f"\nExtraindo com 7-Zip: {arquivo_interno}")

    pcap_local = extrair_com_7zip(
        ZIP_PATH,
        arquivo_interno,
        STAGING_DIR,
        ZIP_PASSWORD
    )

    print(f"Arquivo extraído: {pcap_local}")

    csv_temp = STAGING_DIR / f"{Path(arquivo_interno).name}.csv"

    print(f"Convertendo para CSV com tshark: {csv_temp}")

    converter_pcap_para_csv(
        pcap_local,
        csv_temp,
        PACOTES_POR_ARQUIVO
    )

    df_temp = pd.read_csv(csv_temp)

    df_temp["regiao_sensor"] = row["regiao"]
    df_temp["ip_sensor_arquivo"] = row["ip_sensor"]
    df_temp["arquivo_origem"] = row["nome_arquivo"]

    dataframes.append(df_temp)

# =========================
# CSV FINAL
# =========================

df_final = pd.concat(dataframes, ignore_index=True)

df_final.to_csv(OUTPUT_CSV, index=False)

print("\nCSV final gerado com sucesso!")
print(f"Arquivo: {OUTPUT_CSV}")
print(f"Total de linhas: {len(df_final)}")
print(df_final.head())