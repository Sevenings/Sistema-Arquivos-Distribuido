import json

def teste():
    comando = {
            'operacao': 'adicionar',
            'nome_arquivo': 'shibuia.png'
            }
    comando_string = json.dumps(comando)

    operacao = interpretador(comando_string)
    operacao()

