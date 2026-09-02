from zipfile import ZipFile
from pathlib import Path
import pandas as pd
import re
import os

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

ZIP_PATH = Path(
    os.getenv(
        "DATASET_ZIP_PATH",
        PROJECT_ROOT / "data/raw/cloud_telescope_raw_dataset_3.zip"
    )
)

OUTPUT = PROJECT_ROOT / "data/index/indice_dataset3.csv"

def extrair_regiao(nome_arquivo):
    """
    Exemplo esperado:
    eu-south-1b-15.161.227.161-2023...
    
    A zona é eu-south-1b.
    A região é eu-south-1.
    """
    base = Path(nome_arquivo).name

    match = re.search(r"([a-z]{2}-[a-z]+-\d+)[a-z]?", base)
    if match:
        return match.group(1)

    return None

def extrair_ip(nome_arquivo):
    match = re.search(r"(\d{1,3}(?:\.\d{1,3}){3})", nome_arquivo)
    if match:
        return match.group(1)

    return None

linhas = []

with ZipFile(ZIP_PATH) as z:
    for info in z.infolist():
        nome = info.filename

        if not nome.endswith((".pcap", ".pcap.gz")):
            continue

        linhas.append({
            "arquivo_zip": nome,
            "nome_arquivo": Path(nome).name,
            "regiao": extrair_regiao(nome),
            "ip_sensor": extrair_ip(nome),
            "tamanho_compactado": info.compress_size,
            "tamanho_original": info.file_size
        })

df = pd.DataFrame(linhas)

df.to_csv(OUTPUT, index=False)

print(f"Índice gerado em: {OUTPUT}")
print(f"Total de arquivos PCAP encontrados: {len(df)}")
print(df.head())