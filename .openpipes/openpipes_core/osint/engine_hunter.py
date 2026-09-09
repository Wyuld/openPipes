import requests
from rich.console import Console

console = Console()

def run(domain: str, keys: list) -> list:
    """
    Executa a raspagem no Hunter.io usando rotação de chaves.
    Retorna uma lista de dicionários padronizada com os contatos.
    """
    if not keys:
        console.print("[dim]  [Hunter] Nenhuma chave configurada. Pulando...[/dim]")
        return []

    url = "https://api.hunter.io/v2/domain-search"
    results = []

    console.print(f"[cyan]  [Hunter] Iniciando extração para: {domain}[/cyan]")

    for key in keys:
        console.print(f"[dim]  [Hunter] Tentando usar chave: {key[:4]}...{key[-4:]}[/dim]")
        
        params = {
            "domain": domain,
            "api_key": key,
            "limit": 100  # O Hunter permite puxar até 100 resultados de uma vez
        }

        try:
            response = requests.get(url, params=params, timeout=15)
            
            # Sucesso!
            if response.status_code == 200:
                data = response.json()
                emails = data.get("data", {}).get("emails", [])
                
                if not emails:
                    console.print(f"[green]  [Hunter] Fim da lista. Nenhum e-mail encontrado para o domínio.[/green]")
                    return results

                for item in emails:
                    results.append({
                        "first_name": item.get("first_name") or "",
                        "last_name": item.get("last_name") or "",
                        "title": item.get("position") or "Desconhecido",
                        "email": item.get("value") or "",
                        "source": "hunter.io"
                    })
                
                console.print(f"[green]  [Hunter] Extração concluída! Total: {len(results)} contatos.[/green]")
                return results

            # Limite atingido (429) ou Chave Inválida (401)
            elif response.status_code in [401, 429]:
                console.print(f"[yellow]  [Hunter] Chave esgotada ou inválida (HTTP {response.status_code}). Rotacionando...[/yellow]")
                continue # Pula para a próxima chave do array

            else:
                console.print(f"[red]  [Hunter] Erro API (HTTP {response.status_code}). Detalhes: {response.text}[/red]")
                return results

        except Exception as e:
            console.print(f"[bold red]  [Hunter] Erro de conexão: {str(e)}[/bold red]")
            return results

    console.print("[bold red]  [Hunter] Todas as chaves esgotaram! Retornando o que foi salvo até agora...[/bold red]")
    return results