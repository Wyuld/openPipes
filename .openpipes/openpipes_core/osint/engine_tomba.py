import requests
import time
from rich.console import Console

console = Console()

def run(domain: str, keys: list) -> list:
    """
    Executa a raspagem no Tomba.io usando rotação de chaves.
    A API exige Key e Secret, que passamos no formato "key:secret".
    """
    if not keys:
        console.print("[dim]  [Tomba] Nenhuma chave configurada. Pulando...[/dim]")
        return []

    url = "https://api.tomba.io/v1/domain-search"
    results = []

    console.print(f"[cyan]  [Tomba] Iniciando extração para: {domain}[/cyan]")

    for key_pair in keys:
        # Separa a Key do Secret
        try:
            api_key, api_secret = key_pair.split(":", 1)
        except ValueError:
            console.print(f"[red]  [Tomba] Formato de chave inválido. Use 'key:secret'. Pulando...[/red]")
            continue

        console.print(f"[dim]  [Tomba] Tentando usar chave: {api_key[:4]}...[/dim]")
        
        page = 1
        
        while True:
            headers = {
                "X-Tomba-Key": api_key,
                "X-Tomba-Secret": api_secret,
                "Content-Type": "application/json"
            }
            
            params = {
                "domain": domain,
                "limit": 100,
                "page": page
            }

            try:
                response = requests.get(url, headers=headers, params=params, timeout=15)
                
                # Sucesso!
                if response.status_code == 200:
                    data = response.json()
                    emails = data.get("data", {}).get("emails", [])
                    
                    if not emails:
                        console.print(f"[green]  [Tomba] Fim da lista. Página {page} não retornou novos dados.[/green]")
                        return results

                    for item in emails:
                        results.append({
                            "first_name": item.get("first_name") or "",
                            "last_name": item.get("last_name") or "",
                            "title": item.get("position") or "Desconhecido",
                            "email": item.get("email") or "",
                            "source": "tomba.io"
                        })
                    
                    # Verifica se precisamos ir para a próxima página
                    meta = data.get("meta", {})
                    total_pages = meta.get("total_pages", 1)
                    
                    if page >= total_pages:
                        console.print(f"[green]  [Tomba] Extração concluída! Total: {len(results)} contatos.[/green]")
                        return results
                        
                    page += 1
                    time.sleep(1) # Delay anti-ban

                # Limite atingido (429) ou Chave Inválida (401)
                elif response.status_code in [401, 429]:
                    console.print(f"[yellow]  [Tomba] Chave esgotada ou inválida (HTTP {response.status_code}). Rotacionando...[/yellow]")
                    break # Sai do while da paginação, pula para a próxima chave no 'for'

                else:
                    console.print(f"[red]  [Tomba] Erro API (HTTP {response.status_code}). Detalhes: {response.text}[/red]")
                    return results

            except Exception as e:
                console.print(f"[bold red]  [Tomba] Erro de conexão: {str(e)}[/bold red]")
                return results

    console.print("[bold red]  [Tomba] Todas as chaves esgotaram! Retornando o que foi salvo até agora...[/bold red]")
    return results