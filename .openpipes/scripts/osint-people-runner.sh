#!/bin/bash
source ~/.openpipes/config.sh

echo -e "\n\e[34m[+]\e[0m Iniciando OSINT: Mapeamento Humano Passivo (CrossLinked)..."

# ========================================================
# MAGIA NINJA: CONVERTER ARGS CUSTOMIZADOS PARA ARRAY
# ========================================================
extra_args=()
if [[ -n "${OP_TOOL_ARGS:-}" ]]; then
    eval "extra_args=($OP_TOOL_ARGS)"
fi
# ========================================================

# Verifica dependência
if ! command -v crosslinked &>/dev/null; then
    echo -e "\e[31m[!] Dependência ausente: crosslinked (Instale com: pipx install crosslinked)\e[0m"
    exit 1
fi

# Cria o diretório global de OSINT dentro do projeto
OSINT_DIR="$proj_path/OSINT"
mkdir -p "$OSINT_DIR"

DOMAIN_FILE="$proj_path/domains.txt"
if [ ! -f "$DOMAIN_FILE" ]; then
    echo "[!] domains.txt não encontrado. Não há alvos para mapear."
    exit 1
fi

# Vamos ler os domínios do escopo
while read -r domain; do
    # Pula linhas vazias ou comentários
    [[ -z "$domain" || "$domain" =~ ^# ]] && continue

    # Extrai um nome base para a empresa (ex: randonconsorcios.com.br -> randonconsorcios)
    company_name=$(echo "$domain" | awk -F'.' '{print $1}')
    
    # Arquivo de saída em CSV (Natívo do CrossLinked, fácil pro Python ler depois)
    OUT_CSV="$OSINT_DIR/people_${company_name}.csv"
    
    echo "  → Caçando perfis corporativos para: $domain ($company_name)..."

    # Executa o CrossLinked
    # -f: Formato de palpite de e-mail (podemos refinar isso depois, o foco agora é nome/cargo)
    # Ele fará buscas passivas nos motores de busca usando dorks do LinkedIn
    crosslinked -f '{first}.{last}@'"$domain" -o "$OUT_CSV" "${extra_args[@]}" "$company_name" > /dev/null 2>&1

    if [ -s "$OUT_CSV" ]; then
        # Conta as linhas ignorando o cabeçalho
        count=$(tail -n +2 "$OUT_CSV" | wc -l)
        echo -e "  \e[32m[✔] $count perfis extraídos com sucesso!\e[0m"
    else
        echo "  [✖] Nenhum perfil encontrado na web aberta para $company_name."
    fi

done < "$DOMAIN_FILE"

echo -e "\e[32m[✔]\e[0m Mapeamento Humano finalizado."

# Sanity check da internet
if ! ping -c 2 8.8.8.8 &> /dev/null; then
    echo "[!] AVISO: Queda de conexão detectada durante ou após o scan!"
    exit 1  
fi

exit 0