import requests
import time
from rich.console import Console

console = Console()

def run(target_domain: str, keys: list) -> list:
    if not keys:
        console.print("[dim]  [Tomba] Nenhuma chave configurada. Pulando...[/dim]")
        return []

    results = []
    console.print(f"[cyan]  [Tomba] Iniciando extração para: {target_domain}[/cyan]")

    url = "https://api.tomba.io/v1/domain-search"

    for key_pair in keys:
        try:
            api_key, api_secret = key_pair.split(":", 1)
        except ValueError:
            console.print(f"[red]  [Tomba] Formato inválido. Use 'key:secret'. Pulando...[/red]")
            continue

        console.print(f"[dim]  [Tomba] Tentando usar chave: {api_key[:4]}...[/dim]")
        page = 1
        
        while True:
            # 🕵️‍♂️ MÁGICA NINJA: Spoofing de Headers para enganar o WAF
            headers = {
                "X-Tomba-Key": api_key,
                "X-Tomba-Secret": api_secret,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Tomba-Python/1.0.3" # Imita o SDK oficial do Python!
            }
            
            params = {
                "domain": target_domain,
                "limit": 10,
                "page": page
            }

            try:
                response = requests.get(url, headers=headers, params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    emails = data.get("data", {}).get("emails", [])
                    
                    if not emails:
                        console.print(f"[green]  [Tomba] Fim da lista. Página {page} sem novos dados.[/green]")
                        return results

                    for item in emails:
                        results.append({
                            "first_name": item.get("first_name") or "",
                            "last_name": item.get("last_name") or "",
                            "title": item.get("position") or "Desconhecido",
                            "email": item.get("email") or "",
                            "source": "tomba.io"
                        })
                    
                    meta = data.get("meta", {})
                    total_pages = meta.get("total_pages", 1)
                    
                    if page >= total_pages:
                        console.print(f"[green]  [Tomba] Extração concluída! Total: {len(results)} contatos.[/green]")
                        return results
                        
                    page += 1
                    time.sleep(1.5) # Delay um pouco maior para evitar rajadas (Burst limit)

                elif response.status_code in [401, 429]:
                    console.print(f"[yellow]  [Tomba] Limite da API (HTTP {response.status_code}). Rotacionando...[/yellow]")
                    break # Passa para a próxima chave
                else:
                    console.print(f"[red]  [Tomba] Erro API (HTTP {response.status_code}). Detalhes: {response.text}[/red]")
                    return results

            except Exception as e:
                console.print(f"[bold red]  [Tomba] Erro de conexão: {str(e)}[/bold red]")
                return results

    console.print("[bold red]  [Tomba] Todas as chaves esgotaram! Retornando o que foi salvo.[/bold red]")
    return results