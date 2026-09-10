import time
from rich.console import Console
from tomba.client import Client
from tomba.services.domain import Domain
from tomba.exceptions import TombaException

console = Console()

def run(target_domain: str, keys: list) -> list:
    """
    Executa a raspagem no Tomba.io usando o SDK oficial e rotação de chaves.
    A API exige Key e Secret, passados no formato "key:secret".
    """
    if not keys:
        console.print("[dim]  [Tomba] Nenhuma chave configurada. Pulando...[/dim]")
        return []

    results = []
    console.print(f"[cyan]  [Tomba] Iniciando extração para: {target_domain}[/cyan]")

    for key_pair in keys:
        try:
            api_key, api_secret = key_pair.split(":", 1)
        except ValueError:
            console.print(f"[red]  [Tomba] Formato inválido. Use 'key:secret'. Pulando...[/red]")
            continue

        console.print(f"[dim]  [Tomba] Tentando usar chave: {api_key[:4]}...[/dim]")
        
        # Inicializa o Client Oficial
        client = Client()
        client.set_key(api_key).set_secret(api_secret)
        domain_service = Domain(client)
        
        page = 1
        
        while True:
            try:
                # Faz a chamada oficial
                response = domain_service.domain_search(
                    domain=target_domain,
                    page=page,
                    limit=10
                )
                
                # O SDK retorna um dicionário parseado
                emails = response.get("data", {}).get("emails", [])
                
                if not emails:
                    console.print(f"[green]  [Tomba] Fim da lista na página {page}.[/green]")
                    return results

                for item in emails:
                    results.append({
                        "first_name": item.get("first_name") or "",
                        "last_name": item.get("last_name") or "",
                        "title": item.get("position") or "Desconhecido",
                        "email": item.get("email") or "",
                        "source": "tomba.io"
                    })
                
                meta = response.get("meta", {})
                total_pages = meta.get("total_pages", 1)
                
                if page >= total_pages:
                    console.print(f"[green]  [Tomba] Extração concluída! Total: {len(results)} contatos.[/green]")
                    return results
                    
                page += 1
                time.sleep(1)

            except TombaException as e:
                # O SDK lança exceções próprias. Se for rate limit ou auth, rotacionamos.
                error_msg = str(e)
                console.print(f"[yellow]  [Tomba] Erro/Limite da API. Mensagem: {error_msg}. Rotacionando...[/yellow]")
                break # Quebra o while da paginação, passa para a próxima chave
                
            except Exception as e:
                console.print(f"[bold red]  [Tomba] Erro inesperado: {str(e)}[/bold red]")
                return results

    console.print("[bold red]  [Tomba] Todas as chaves esgotaram! Retornando o que foi salvo.[/bold red]")
    return results