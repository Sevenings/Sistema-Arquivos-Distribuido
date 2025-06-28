import pytest, os
from bigfiles.hash import calcular_sha256

from bigfiles.fragmentar import fragmentar

def test_fragmentar_e_salvar():
    output_folder = "tests/fragmentos_dinossauro"
    for i, fragmento in fragmentar("arquivos/dinossauro.webp", tamanho_fragmento=16*1024):
        with open(f"{output_folder}/fragmento_{i}", 'wb') as f:
            f.write(fragmento)


def test_fragmentar_e_remontar():
    """ 
    Fragmenta um arquivo, remonta em outro lugar e 
    verifica se os arquivos são os mesmos, pela comparação dos hashs
    """
    
    input_path = "arquivos/dinossauro.webp"
    output_path = "tests/data/dinossauro_remontado.webp"

    # apagar output caso já exista
    if os.path.exists(output_path):
        os.remove(output_path)

    for i, fragmento in fragmentar(input_path, tamanho_fragmento=16*1024):
        with open(output_path, 'ab') as output:
            output.write(fragmento)

    hash_input = calcular_sha256(input_path)
    hash_output = calcular_sha256(output_path)

    assert hash_input == hash_output

