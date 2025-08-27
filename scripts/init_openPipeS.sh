#!/bin/bash

# Configs
source $HOME/.templates/config.sh

# Função para log com timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Verifica se diretórios existem
if [ ! -d "$tpdir" ]; then
    log "Diretório de templates não encontrado: $tpdir"
    exit 1
fi

if [ ! -d "$obsdir" ]; then
    log "Diretório do Obsidian não montado: $obsdir"
    exit 1
fi

# Copia templates base para dentro do diretório do Obsidian
log "Copiando templates principais para a Vault..."
cp -n "$tpdir/Dashboard_Global.md" "$obsdir/Pentest/"
cp -n "$tpdir/Tarefas.md" "$obsdir/Pentest/"

# Criação da estrutura básica de Alvo (interativo)
read -p "Digite o nome do novo alvo (ex: sistema.exemplo.com): " targetName
read -p "Digite o IP do novo alvo (ex: 10.10.10.10): " ip

# Verifica se alvo já existe
if [ -d "$obsdir/Pentest/Alvos/$targetName" ]; then
    log "Alvo '$targetName' já existe. Abortando."
    exit 1
fi

# Criação das pastas
log "Criando estrutura para o alvo $targetName..."
mkdir -p "$obsdir/Pentest/Alvos/$targetName/Vulnerabilidades"

# Cria uma vulnerabilidade stub
cp -n "$tpdir/vuln.stub.md" "$obsdir/Pentest/Alvos/$targetName/Vulnerabilidades/Vuln.stub.md""

# Substituição de variáveis nos templates
sed "s/{{targetName}}/$targetName/g;s/{{ip}}/$ip/g" "$tpdir/target.stub.md" > "$obsdir/Pentest/Alvos/$targetName/$targetName.md"
sed "s/{{targetName}}/$targetName/g" "$tpdir/dashboard.stub.md" > "$obsdir/Pentest/Alvos/$targetName/Dashboard_${targetName}.md"

log "Estrutura criada com sucesso para o alvo $targetName."
