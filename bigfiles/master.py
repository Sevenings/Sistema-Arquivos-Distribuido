from Pyro5.api import Proxy, expose, Daemon, locate_ns
from sqlalchemy import desc
from bigfiles.database import iniciar_db, session
from bigfiles.erros.erros import ErroArquivoNaoExiste, ErroMaquinasNaoEncontradas
from bigfiles.models import Arquivo, Maquina, Shard


@expose
class Master:
    def __init__(self):
        pass

    def start(self):
        # Iniciar o banco de dados
        iniciar_db()

        # Se registrar no serviço de nomes
        daemon = Daemon()
        ns = locate_ns()
        uri = daemon.register(self)
        ns.register("bigfs.master", uri)
        daemon.requestLoop()


    def registrar_nova_maquina(self):
        """
        Função chamada pelo Node para se registrar ao cluster.

        Ao chamar essa função, é criado um registro no banco de dados de uma nova máquina
        e é retornado o id dessa nova máquina para que o node guarde. Dessa forma o node
        deve se registrar no servidor de nomes usando o ID que recebeu.

        É possível fazer uma lógica de "recadastro" caso haja algum problema com o registro. 
        Situação: o node tem um ID que por algum erro, não está mais registrado no banco de dados.
        Solução, o Node envia o ID, caso não esteja cadastrado, o Master cria um novo registro com 
        esse ID e eles começam um protocolo de sincronização. O Node "conta" ao Master quais 
        shards ele possui.

        A partir dessa situação, também é possível fazer um mecanismo de: Master percebe que alguns 
        dados do Node estão desatualizados e atualiza eles.

        :return: id
        """
        print("Registrando nova maquina no cluster")
        ultima_maquina = session.query(Maquina).order_by(desc(Maquina.id)).first()

        if not ultima_maquina:
            novo_id = 0
        else:
            novo_id = ultima_maquina.id + 1

        print(f"Novo id: {novo_id}")

        nova_maquina = Maquina(id=novo_id, endereco=f"bigfs.node.{novo_id}")
        session.add(nova_maquina)
        session.commit()

        print(f"Máquina com id {novo_id} registrada com sucesso")
        return novo_id



    def upload_fragmento(self, nome_arquivo: str, hash_arquivo: str, hash_fragmento: str, ordem: int, fragmento_data: bytes):
        """
        Função que recebe um fragmento, escolhe as melhores máquinas para guardá-lo, envia a elas
        e atualiza o index no banco de dados.

        :param nome_arquivo: nome do arquivo ao qual o fragmento pertence
        :param hash_arquivo: string hash que identifica o arquivo
        :param hash_fragmento: string hash que identifica os bytes do fragmento
        :param ordem: número que identifica qual a ordem do fragmento
        :param fragmento_data: dados do fragmento
        :return: resultado da operação
        """

        print("Upload de arquivo:")
        print(f"Arquivo: {nome_arquivo}")
        print(f"Hash arquivo: {hash_arquivo}")
        print(f"Hash fragmento: {hash_fragmento}")
        print(f"Ordem: {ordem}")

        # Registrar no banco de dados o arquivo caso não exista
        print("Registrando arquivo no banco de dados")
        arquivo = self._registrar_arquivo(hash_arquivo, nome_arquivo, tamanho=None)

        # Salvar no banco de dados o novo shard
        print("Registrando shard no banco de dados")
        novo_shard = Shard(hash=hash_fragmento, ordem=ordem, id_arquivo=arquivo.id)
        session.add(novo_shard)

        # Escolher no máximo 3 máquinas para replicar o fragmento
        maquinas_destino = self._maquinas_destino()
        print(f"Maquinas selecionadas: {maquinas_destino}")

        # Enviar uma réplica para cada máquina
        print("Enviando réplicas do fragmento aos nós")
        for maquina in maquinas_destino:
            with Proxy(f"PYRONAME:{maquina.endereco}") as node:
                node.upload_fragmento(nome_arquivo=nome_arquivo,
                        arquivo_data_pkg=fragmento_data,
                        ordem=ordem,
                        hash_esperado=hash_fragmento)
            novo_shard.maquinas.append(maquina)
        session.commit()

        return True



    def listar_arquivos(self):
        arquivos = session.query(Arquivo).order_by(Arquivo.nome).all()
        return [ a.nome for a in arquivos ]


    def remover_arquivo(self, nome_arquivo: str):
        # Verificar se o arquivo existe
        arquivo = session.query(Arquivo).filter_by(nome=nome_arquivo).first()
        if not arquivo:
            raise ErroArquivoNaoExiste(nome_arquivo)

        # Encontrar os shards do arquivo
        shards = arquivo.shards

        # Remover os shards de todas as máquinas
        for shard in shards:
            for maquina in shard.maquinas:
                with Proxy(f"PYRONAME:{maquina.endereco}") as node:
                    node.rm(nome_arquivo, shard.ordem)
                maquina.shards.remove(shard)

        # Remover arquivo e seus shards do banco de dados
        session.delete(arquivo)
        session.commit()


    def baixar_arquivo(self, nome_arquivo):
        pass


    def possui(self, nome_arquivo):
        if session.query(Arquivo).filter_by(nome=nome_arquivo).first():
            return True
        return False


    def _maquinas_destino(self) -> list[Maquina]:
        """ Seleciona no máximo as 3 melhores máquinas para se realizar o upload do fragmento"""
        maquinas = session.query(Maquina).all()
        if not maquinas:
            raise ErroMaquinasNaoEncontradas
        return maquinas


    def _registrar_arquivo(self, hash, nome, tamanho):    # TODO: Tamanho do arquivo
        tamanho = 0
        # Se arquivo já existe, não registre novamente
        arquivo = session.query(Arquivo).filter_by(nome=nome).first()
        if arquivo:
            return arquivo
        arquivo = Arquivo(hash=hash, nome=nome, tamanho=tamanho)
        session.add(arquivo)
        session.commit()
        return arquivo


