# Lista de Erros

# Erros Cliente
# -----------------------

class OperacaoInvalidaError(Exception):
    def __init__(self, uso, *args: object) -> None:
        super().__init__(*args)
        self.uso = uso

class ParametrosInvalidosError(Exception):
    def __init__(self, uso, *args: object) -> None:
        super().__init__(*args)
        self.uso = uso

class UsoIncorretoClientError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


# Erros Server
# -----------------------

class ErroArquivoNaoExiste(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ErroArquivoJaExiste(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ErroPoucaMemoria(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

# Erros Master
# -----------------------

class ErroMaquinasNaoEncontradas(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
