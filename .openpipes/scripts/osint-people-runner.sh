#!/bin/bash
source ~/.openpipes/config.sh

# === MODO DE AJUDA & STATUS DAS APIs ===
if [ -z "$1" ]; then
    echo -e "\n\e[34m[+]\e[0m OPenPipeS OSINT - Mapeamento Humano"
    echo -e "Uso: \e[32mopenpipes-core run osint-people-runner <dominio1> [dominio2...]\e[0m"
    echo -e "\n\e[33m[*] Verificando status das APIs configuradas no secrets.conf...\e[0m"
    
    # Chama o Python passando a flag especial --status
    PYTHONPATH="$HOME/.openpipes" python -m openpipes_core.osint.orchestrator --status
    exit 0
fi
# =======================================

echo -e "\n\e[34m[+]\e[0m Iniciando OSINT: Mapeamento Humano Multi-Engine..."
OSINT_DIR="$proj_path/OSINT"
mkdir -p "$OSINT_DIR"

# Itera sobre todos os domínios passados como argumento (ex: arg1 arg2 arg3)
for domain in "$@"; do
    # Limpa espaços acidentais
    domain=$(echo "$domain" | tr -d ' ')
    [[ -z "$domain" ]] && continue

    company_name=$(echo "$domain" | awk -F'.' '{print $1}')
    OUT_JSON="$OSINT_DIR/osint_people_${company_name}.json"
    
    echo "  → Acionando motores de busca para: $domain..."
    
    # Chama o Orquestrador em Python
    PYTHONPATH="$HOME/.openpipes" python -m openpipes_core.osint.orchestrator "$domain" "$OUT_JSON"
done

echo -e "\e[32m[✔]\e[0m Mapeamento OSINT finalizado."
exit 0