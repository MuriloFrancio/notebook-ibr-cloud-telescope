from pathlib import Path
import os
import getpass
import pandas as pd
import subprocess
import shutil
import random

script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent

zip_path = Path(
    os.getenv(
        "DATASET_ZIP_PATH",
        str(project_root / "data/raw/cloud_telescope_raw_dataset_3.zip")
    ).strip().strip('"')
)

index_path = project_root / "data/index/indice_dataset3.csv"
staging_dir = project_root / "data/staging"
output_csv = project_root / "data/processed/dataset3_amostra.csv.gz"

seven_zip = shutil.which("7z") or r"C:\Program Files\7-Zip\7z.exe"
tshark = shutil.which("tshark") or r"D:\Wireshark\tshark.exe"

zip_password = os.getenv("DATASET_ZIP_PASSWORD", "").strip().strip('"')
pacotes_por_arquivo = int(os.getenv("PACOTES_POR_ARQUIVO", "10000"))

if not zip_password:
    zip_password = getpass.getpass("Digite a senha do ZIP do Dataset 3: ")

if not zip_path.exists():
    raise FileNotFoundError(f"Dataset não encontrado em: {zip_path}")

if not index_path.exists():
    raise FileNotFoundError(f"Índice não encontrado em: {index_path}")

if not Path(seven_zip).exists():
    raise FileNotFoundError(f"7-Zip não encontrado em: {seven_zip}")

if not Path(tshark).exists():
    raise FileNotFoundError(
        f"tshark não encontrado em: {tshark}\n"
        "Instale o Wireshark ou ajuste o caminho do tshark."
    )

staging_dir.mkdir(parents=True, exist_ok=True)
output_csv.parent.mkdir(parents=True, exist_ok=True)

def extrair_com_7zip(zip_path, arquivo_interno, destino_dir, senha):
    cmd = [
        seven_zip,
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
        tshark,
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

    with open(csv_path, "w", encoding="utf-8") as arquivo_saida:
        subprocess.run(cmd, stdout=arquivo_saida, check=True)

def escolher_arquivos(df_index):
    regioes = sorted(df_index["regiao"].dropna().unique())

    print("\nRegiões disponíveis:")
    for regiao in regioes:
        print(f"- {regiao}")

    print("\nEscolha o tipo de amostra:")
    print("1 - Uma amostra de todas as regiões")
    print("2 - Uma amostra de uma região específica")
    print("3 - Uma amostra de uma região aleatória")

    opcao = input("\nDigite a opção desejada: ").strip()

    if opcao == "1":
        selecionados = (
            df_index
            .dropna(subset=["regiao"])
            .sort_values(["regiao", "nome_arquivo"])
            .groupby("regiao")
            .head(1)
        )

        return selecionados

    if opcao == "2":
        regiao_escolhida = input("\nDigite a região desejada, exemplo eu-central-1: ").strip()

        if regiao_escolhida not in regioes:
            raise ValueError(f"Região inválida: {regiao_escolhida}")

        selecionados = (
            df_index[df_index["regiao"] == regiao_escolhida]
            .sort_values("nome_arquivo")
            .head(1)
        )

        return selecionados

    if opcao == "3":
        regiao_aleatoria = random.choice(regioes)

        print(f"\nRegião aleatória escolhida: {regiao_aleatoria}")

        selecionados = (
            df_index[df_index["regiao"] == regiao_aleatoria]
            .sample(n=1, random_state=None)
        )

        return selecionados

    raise ValueError("Opção inválida. Use 1, 2 ou 3.")

df_index = pd.read_csv(index_path)

selecionados = escolher_arquivos(df_index)

if selecionados.empty:
    raise ValueError("Nenhum arquivo foi selecionado para gerar a amostra.")

print("\nArquivos selecionados:")
print(selecionados[["regiao", "ip_sensor", "nome_arquivo"]])

dataframes = []

for _, row in selecionados.iterrows():
    arquivo_interno = row["arquivo_zip"]

    print(f"\nExtraindo com 7-Zip: {arquivo_interno}")

    pcap_local = extrair_com_7zip(
        zip_path,
        arquivo_interno,
        staging_dir,
        zip_password
    )

    print(f"Arquivo extraído: {pcap_local}")

    csv_temp = staging_dir / f"{Path(arquivo_interno).name}.csv"

    print(f"Convertendo para CSV com tshark: {csv_temp}")

    converter_pcap_para_csv(
        pcap_local,
        csv_temp,
        pacotes_por_arquivo
    )

    df_temp = pd.read_csv(csv_temp)

    df_temp["regiao_sensor"] = row["regiao"]
    df_temp["ip_sensor_arquivo"] = row["ip_sensor"]
    df_temp["arquivo_origem"] = row["nome_arquivo"]

    dataframes.append(df_temp)

df_final = pd.concat(dataframes, ignore_index=True)

df_final.to_csv(output_csv, index=False)

print("\nCSV final gerado com sucesso!")
print(f"Arquivo: {output_csv}")
print(f"Total de linhas: {len(df_final)}")
print(df_final.head())