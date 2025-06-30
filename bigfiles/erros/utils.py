
# Utils
# -----------------------

from Pyro5.api import register_class_to_dict, register_dict_to_class

def pyro_serializable_exc(cls):
    """
    Decora a exception para que ela seja registrada automaticamente
    no Serpent sempre que o módulo for importado, sem precisar
    mexer no Serializer diretamente.
    """
    # função que transforma a exceção em dict
    def _to_dict(exc):
        return {"args": exc.args}

    # função que recria a exceção a partir do dict
    def _from_dict(classname, d):
        return cls(*d["args"])

    # registra os converters no Pyro (Serpent)
    register_class_to_dict(cls, _to_dict)                             # :contentReference[oaicite:0]{index=0}
    register_dict_to_class(f"{cls.__module__}.{cls.__name__}", _from_dict)  # :contentReference[oaicite:1]{index=1}

    return cls
