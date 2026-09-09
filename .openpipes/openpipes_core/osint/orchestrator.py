import sys
import os
import json
import re
from pathlib import Path
from rich.console import Console

# Importa as nossas Engines isoladas
from openpipes_core.osint import engine_apollo
from openpipes_core.osint import engine_hunter

console = Console()

def load_secrets():
    """
    Lê o secrets.conf e traduz os arrays do Bash para listas do Python.
    Isso é mágico porque mantém a compatibilidade com a infraestrutura shell!
    """
    secrets_path = os.path.join(str(Path.home()), ".openpipes", "secrets.conf")
    secrets = {
        "apollo": [],
        "hunter": []
    }
    
    if not os.path.exists(secrets_path):
        console.print("[yellow][!] secrets.conf não encontrado. Orquestrador rodará sem chaves.[/yellow]")
        return secrets

    with open(secrets_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex Ninja: Busca por APOLLO_KEYS=("chave1" "chave2")
    apollo_match = re.search(r'APOLLO_KEYS=\((.*?)\)', content, re.DOTALL)
    if apollo_match:
        # Pega tudo dentro dos parênteses, divide por espaços e arranca as aspas
        raw_keys = apollo_match.group(1).split()
        secrets["apollo"] = [k.strip("'\"") for k in raw_keys if k.strip("'\"")]

    # Regex do Hunter ficaria aqui no futuro!
    
    return secrets

def deduplicate(results):
    """
    A faxina fina! Remove contatos duplicados cruzando as bases.
    Prioriza o E-mail como identificador único. Se não tiver e-mail, usa Nome+Sobrenome.
    """
    seen = {}
    for p in results:
        email = p.get("email", "").strip().lower()
        fname = p.get("first_name", "").strip().lower()
        lname = p.get("last_name", "").strip().lower()
        
        # Define a chave de identidade do contato
        if email:
            uid = email
        else:
            uid = f"{fname}_{lname}"
            
        if not uid or uid == "_":
            continue # Pula "fantasmas" que não têm nem nome nem e-mail
            
        if uid not in seen:
            seen[uid] = p
            
    return list(seen.values())

def main():
    if len(sys.argv) < 3:
        console.print("[bold red]Uso: python -m openpipes_core.osint.orchestrator <domain> <out_json>[/bold red]")
        sys.exit(1)

    domain = sys.argv[1]
    out_json = sys.argv[2]
    
    # 1. Carrega as armas do Cofre
    secrets = load_secrets()
    all_results = []
    
    # 2. Aciona o Motor do Apollo
    apollo_keys = secrets.get("apollo", [])
    if apollo_keys:
        apollo_data = engine_apollo.run(domain, apollo_keys)
        all_results.extend(apollo_data)
    else:
        console.print("[dim]  [Orchestrator] Nenhuma chave APOLLO encontrada no secrets.conf.[/dim]")

    # 3. Aciona Motore do Hunter
    hunter_keys = secrets.get("hunter", [])
    if hunter_keys:
        hunter_data = engine_hunter.run(domain, hunter_keys)
        all_results.extend(hunter_data)
    
    # 4. Consolida e limpa a sujeira
    final_results = deduplicate(all_results)
    
    console.print(f"[bold green]  [Orchestrator] OSINT Consolidado: {len(final_results)} contatos únicos mapeados.[/bold green]")
    
    # 5. Entrega a bandeja de prata para o parser
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()