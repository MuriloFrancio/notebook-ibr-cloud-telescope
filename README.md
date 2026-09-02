# IBR Notebook

Disponibiliza um Jupyter Notebook didático para exploração de amostras de Radiação de Fundo da Internet

---

## Requisitos

Para executar o projeto, é necessário ter instalado:

- Docker Desktop
- Git, apenas caso deseje baixar o repositório pelo GitHub
- Dataset 3 do Cloud Telescope, apenas para quem quiser processar os dados completos

O Dataset 3 completo **não está incluído** na imagem Docker nem no repositório.

---

# 1. Executar pela imagem Docker

esse modo não é necessário baixar o repositório do github.

Execute:

```powershell
docker run --rm -it -p 8888:8888 --cap-add NET_RAW --cap-add NET_ADMIN murilofrancio770/ibr-notebook:latest
```
Esse comando baixa a imagem, inicia o Jupyter Notebook na porta 8888 e libera permissões de rede para ferramentas como tcpdump

Depois abra no navegador:

```text
http://localhost:8888/lab
```

Para parar:

```powershell
docker stop ibr-notebook
```

Para iniciar novamente:

```powershell
docker start ibr-notebook
```

---

# 2. Executar pela imagem Docker com o Dataset 3

Use este modo caso você já tenha baixado o arquivo:

```text
cloud_telescope_raw_dataset_3.zip
```

Baixe o arquivo `rodar_com_dataset.bat` disponível neste repositório e execute.

O script irá pedir:

```text
1. caminho da pasta onde está o Dataset 3
2. senha do Dataset 3
```

Exemplo de caminho:

```text
C:\downloads
```

Dentro dessa pasta deve existir o arquivo:

```text
cloud_telescope_raw_dataset_3.zip
```
Depois abra no navegador:

```text
http://localhost:8888/lab
```

---

# 3. GitHub sem Dataset 3

Clone o repositório:

```powershell
git clone https://github.com/MuriloFrancio/notebook-ibr-cloud-telescope
```

Entre na pasta:

```powershell
cd REPOSITORIO
```

Execute com Docker Compose:

```powershell
docker compose up --build
```

Depois abra:

```text
http://localhost:8888/lab
```

Constrói a imagem localmente a partir do `Dockerfile` e monta as pastas do projeto dentro do container.

---

# 4. GitHub com Dataset 3

Clone o repositório:

```powershell
git clone https://github.com/MuriloFrancio/notebook-ibr-cloud-telescope
```

Entre na pasta:

```powershell
cd REPOSITORIO
```

Copie o arquivo de exemplo:

```powershell
copy .env.example .env
```

Edite o arquivo `.env` e informe o caminho da pasta onde está o Dataset 3:

EX env
```.env
DATASET_DIR=C:\downloads
DATASET_ZIP_PASSWORD=senha
```

Depois execute:
```powershell
docker compose up --build
```

Abra no navegador:

```text
http://localhost:8888/lab
```
---
O Dataset 3 deve ser baixado separadamente por quem tiver acesso.

Para uso simples, recomenda-se executar diretamente pela imagem Docker.
