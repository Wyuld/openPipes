#!/bin/bash
source ~/.openpipes/config.sh

echo -e "\n\e[34m[+]\e[0m Iniciando OSINT: Mapeamento Humano Multi-Engine..."

OSINT_DIR="$proj_path/OSINT"
mkdir -p "$OSINT_DIR"

DOMAIN_FILE="$proj_path/domains.txt"
if [ ! -f "$DOMAIN_FILE" ]; then
    echo "[!] domains.txt não encontrado. Não há alvos para mapear."
    exit 1
fi

while read -r domain; do
    [[ -z "$domain" || "$domain" =~ ^# ]] && continue

    company_name=$(echo "$domain" | awk -F'.' '{print $1}')
    
    # Adotei um padrão de nome que o nosso parsers.py vai amar ler depois!
    OUT_JSON="$OSINT_DIR/osint_people_${company_name}.json"
    
    if [ -s "$OUT_JSON" ]; then
        echo "  [SKIP] $domain já foi mapeado (arquivo $OUT_JSON existe)."
        continue
    fi

    echo "  → Acionando motores de busca para: $domain..."
    
    # Chama o Orquestrador em Python passando o mapa (PYTHONPATH) e os argumentos vitais
    PYTHONPATH="$HOME/.openpipes" python -m openpipes_core.osint.orchestrator "$domain" "$OUT_JSON"
    
done < "$DOMAIN_FILE"

echo -e "\e[32m[✔]\e[0m Mapeamento OSINT finalizado."

# Sanity Check de internet
if ! ping -c 2 8.8.8.8 &> /dev/null; then
    echo "[!] AVISO: Queda de conexão detectada!"
    exit 1  
fi

exit 0