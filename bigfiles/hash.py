import hashlib

def calcular_sha256_bytes(arquivo_data: bytes):
    """
    Calcula o hash SHA-256 de bytes de um arquivo

    :param arquivo_data: Bytes a serem calculados o hash
    :return: Hash SHA-256 como string hexadecimal.
    """
    sha256_hash = hashlib.sha256()
    sha256_hash.update(arquivo_data)
    return sha256_hash.hexdigest()


def calcular_sha256(caminho_arquivo, tamanho_bloco=65536):
    """
    Calcula o hash SHA-256 de um arquivo lendo em blocos.
    
    :param caminho_arquivo: Caminho para o arquivo.
    :param tamanho_bloco: Tamanho de bloco de leitura (padrão: 64KB).
    :return: Hash SHA-256 como string hexadecimal.
    """
    sha256 = hashlib.sha256()
    with open(caminho_arquivo, 'rb') as f:
        for bloco in iter(lambda: f.read(tamanho_bloco), b''):
            sha256.update(bloco)
    return sha256.hexdigest()

