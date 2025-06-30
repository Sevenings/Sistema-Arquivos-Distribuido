# Lista de Erros

from .utils import pyro_serializable_exc


# Erros Cliente
# -----------------------

@pyro_serializable_exc
class OperacaoInvalidaError(BaseException):
    def __init__(self, uso, *args: object) -> None:
        super().__init__(*args)
        self.uso = uso

@pyro_serializable_exc
class ParametrosInvalidosError(BaseException):
    def __init__(self, uso, *args: object) -> None:
        super().__init__(*args)
        self.uso = uso

@pyro_serializable_exc
class UsoIncorretoClientError(BaseException):
    pass


# Erros Server
# -----------------------

@pyro_serializable_exc
class ErroArquivoNaoExiste(BaseException):
    def __init__(self, arquivo=None, *args: object) -> None:
        super().__init__(*args)
        self.arquivo = arquivo

@pyro_serializable_exc
class ErroArquivoJaExiste(Exception):
    def __init__(self, arquivo=None, *args: object) -> None:
        super().__init__(*args)
        self.arquivo = arquivo

@pyro_serializable_exc
class ErroPoucaMemoria(BaseException):
    pass


# Erros Master
# -----------------------

@pyro_serializable_exc
class ErroMaquinasNaoEncontradas(BaseException):
    pass


