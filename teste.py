from bigfiles.index import Index

with Index() as index:
    print('\n'.join(index.listar()))

