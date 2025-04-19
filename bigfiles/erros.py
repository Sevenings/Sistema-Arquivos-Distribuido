# Lista de Erros

class ErroArquivoNaoExiste(Exception):
    id = 0
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ErroArquivoJaExiste(Exception):
    id = 1
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ErroPoucaMemoria(Exception):
    id = 2
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


# Códigos dos erros
error_by_id = {
        '0': ErroArquivoNaoExiste(),
        '1': ErroArquivoJaExiste(),
        '2': ErroPoucaMemoria()
        }


