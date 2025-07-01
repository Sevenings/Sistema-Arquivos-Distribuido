import os
from datetime import datetime

def registra_logs(nome_acao: str, texto: str, pasta_logs: str = 'logs', arquivo_logs: str = 'logs.txt') -> None:
    # Garante existência da pasta
    os.makedirs(pasta_logs, exist_ok=True)
    
    # Caminho completo do arquivo de log
    path = os.path.join(pasta_logs, arquivo_logs)
    
    # Timestamp da operação
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Linha que será escrita
    linha = f'[{ts}] [{nome_acao}] {texto}\n'
    
    # Abre em modo append (cria o arquivo se não existir) e escreve
    with open(path, 'a', encoding='utf-8') as f:
        f.write(linha)
