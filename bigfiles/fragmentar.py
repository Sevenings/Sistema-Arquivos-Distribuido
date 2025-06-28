def fragmentar(path_arquivo: str, tamanho_fragmento=1024*1024):
    """
    Fragmenta o arquivo em partes do tamanho especificado.
    
    :param caminho_arquivo: Caminho para o arquivo a ser fragmentado.
    :param tamanho_fragmento: Tamanho de cada fragmento em bytes (default: 1MB).
    :yield: Um fragmento do arquivo.
    """
    i = 0
    with open(path_arquivo, 'rb') as f:
        while True:
            fragmento = f.read(tamanho_fragmento)
            if not fragmento:
                break
            yield i, fragmento
            i += 1


