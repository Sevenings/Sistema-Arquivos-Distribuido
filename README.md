# Sistema-Arquivos-Distribuido
Projeto para a criação de um sistema de arquivos distribuidos. Suportando arquivos pesados e altamente escalável.

## Executar

Dependências:
- Python
- Git
- Make

1. Clone o repositório localmente, crie uma venv python e instale as dependências
```
git clone https://github.com/Sevenings/Sistema-Arquivos-Distribuido.git
cd Sistema-Arquivos-Distribuido
make setup
```

2. No mesmo terminal execute o servidor de nomes
```
cd Sistema-Arquivos-Distribuido
make nameserver
```

3. Em um segundo terminal, execute o servidor de arquivos
```
cd Sistema-Arquivos-Distribuido
make server
```

4. Em um terceiro terminal, execute o cliente
```
cd Sistema-Arquivos-Distribuido
./client [-h] <operação> [argumentos]
```

