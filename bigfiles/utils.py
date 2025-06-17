import hashlib

def gerar_hash_arquivo(arquivo_data: bytes):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(arquivo_data)
    return sha256_hash.hexdigest()

