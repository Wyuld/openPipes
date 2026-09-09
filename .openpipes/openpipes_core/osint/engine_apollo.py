import requests
import time
from rich.console import Console

console = Console()

def run(domain: str, keys: list) -> list:
    """
    Executa a raspagem no Apollo.io usando rotação de chaves.
    Retorna uma lista de dicionários com os contatos.
    """
    if not keys:
        console.print("[dim]  [Apollo] Nenhuma chave configurada. Pulando...[/dim]")
        return []

    url = "https://api.apollo.io/v1/mixed_people/search"
    results = []
    page = 1

    console.print(f"[cyan]  [Apollo] Iniciando extração para: {domain}[/cyan]")

    for key in keys:
        console.print(f"[dim]  [Apollo] Tentando usar chave: {key[:4]}...{key[-4:]}[/dim]")
        
        while True:
            headers = {
                "Cache-Control": "no-cache",
                "Content-Type": "application/json"
            }
            payload = {
                "api_key": key,
                "q_organization_domains": domain,
                "page": page,
                "per_page": 25  # Máximo permitido pela API free do Apollo
            }

            try:
                response = requests.post(url, headers=headers, json=payload, timeout=15)
                
                # Sucesso!
                if response.status_code == 200:
                    data = response.json()
                    people = data.get('people', [])
                    
                    if not people:
                        console.print(f"[green]  [Apollo] Fim da lista. Total extraído: {len(results)}[/green]")
                        return results

                    for person in people:
                        results.append({
                            "first_name": person.get("first_name") or "",
                            "last_name": person.get("last_name") or "",
                            "title": person.get("title") or "",
                            "email": person.get("email") or "",
                            "source": "apollo.io"
                        })
                    
                    console.print(f"[dim]  [Apollo] Página {page} extraída ({len(people)} contatos).[/dim]")
                    
                    # Verifica paginação
                    pagination = data.get('pagination', {})
                    if page >= pagination.get('total_pages', 1):
                        console.print(f"[green]  [Apollo] Extração concluída! Total: {len(results)} contatos.[/green]")
                        return results
                        
                    page += 1
                    time.sleep(1) # Delay anti-ban

                # Limite atingido (429) ou Chave Incorreta (401)
                elif response.status_code in [401, 429]:
                    console.print(f"[yellow]  [Apollo] Chave esgotada (HTTP {response.status_code}). Rotacionando...[/yellow]")
                    break # Sai do 'while' e passa para a próxima chave do 'for'

                else:
                    console.print(f"[red]  [Apollo] Erro API (HTTP {response.status_code}). Detalhes: {response.text}[/red]")
                    return results

            except Exception as e:
                console.print(f"[bold red]  [Apollo] Erro de conexão: {str(e)}[/bold red]")
                return results

    console.print("[bold red]  [Apollo] Todas as chaves esgotaram! Retornando o que foi salvo até agora...[/bold red]")
    return results