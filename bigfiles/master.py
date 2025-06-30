from Pyro5.api import Proxy, expose, Daemon, locate_ns
from sqlalchemy import desc
from bigfiles.database import iniciar_db, session
from bigfiles.erros import ErroMaquinasNaoEncontradas
from bigfiles.models import Arquivo, Maquina, Shard
from bigfiles.logs import registra_logs


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
        registra_logs("REGISTRO NOVA MÁQUINA AO CLUSTER", f"Máquina com id {novo_id} registrada com sucesso")
        
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
                node.cp_mock(nome_arquivo, fragmento_data, hash_fragmento)
            novo_shard.maquinas.append(maquina)
        session.commit()

        registra_logs("UPLOAD DE FRAGMENTO", f"Fragmento {hash_fragmento} enviado para {maquinas_destino}")

        return True



    def listar_arquivos(self):
        """
        Lista todos os arquivos registrados no sistema.
        :return: lista de dicionários com id e nome de cada arquivo
        """
        arquivos = session.query(Arquivo).all()
        resultados = []
        for arq in arquivos:
            resultados.append({'id': arq.id, 'nome': arq.nome})
            print(f"[{arq.id}] {arq.nome}")
        return resultados


    def remover_arquivo(self, nome_arquivo: str):
        """
        Remove um arquivo e todos os seus shards do sistema:
        1. Busca o Arquivo pelo nome.
        2. Para cada shard, solicita a remoção em cada nó.
        3. Deleta os shards e por fim o registro do Arquivo.
        :param nome_arquivo: nome do arquivo a remover
        :return: True se removido, False se não encontrado
        """
        try:
            arquivo = session.query(Arquivo).filter_by(nome=nome_arquivo).one()
        except Exception:
            print(f"Arquivo '{nome_arquivo}' não encontrado.")
            return False

        print(f"Removendo arquivo '{nome_arquivo}' (ID {arquivo.id}) e seus shards…")
        for shard in arquivo.shards:
            print(f" • Shard {shard.hash} (ordem {shard.ordem}):")
            for maquina in shard.maquinas:
                print(f"   → removendo réplica no nó {maquina.endereco}")
                with Proxy(f"PYRONAME:{maquina.endereco}") as node:
                    # supondo que exista um método rm_mock ou delete_fragment
                    node.rm_mock(shard.hash)
            # depois de remover as réplicas, desvincula máquinas
            shard.maquinas.clear()
            session.delete(shard)

        session.delete(arquivo)
        session.commit()

        registra_logs("REMOÇÃO DE ARQUIVO", f"Arquivo {nome_arquivo} removido com sucesso")

        print("Remoção concluída.")
        return True


    def baixar_arquivo(self, nome_arquivo: str) -> bytes:
        """
        Reconstroi um arquivo a partir dos seus shards:
        1. Busca o Arquivo pelo nome.
        2. Recupera todos os shards ordenados pela ordem original.
        3. Para cada shard, faz download do fragmento do primeiro nó disponível.
        4. Concatena todos os bytes e retorna o conteúdo completo.
        :param nome_arquivo: nome do arquivo a baixar
        :return: bytes com o arquivo reconstruído
        """
        try:
            arquivo = session.query(Arquivo).filter_by(nome=nome_arquivo).one()
        except Exception:
            raise FileNotFoundError(f"Arquivo '{nome_arquivo}' não encontrado no sistema.")

        print(f"Arquivo encontrado: {arquivo.nome} com {len(arquivo.shards)} shards")
        for shard in arquivo.shards:
            print(f"Shard {shard.id}: ordem={shard.ordem} (tipo: {type(shard.ordem)})")

        def safe_ordem(shard):
            try:
                if shard.ordem is None or str(shard.ordem).strip() == "":
                    return 0
                return int(str(shard.ordem).strip())
            except Exception as e:
                print(f'AVISO: ordem inválida para shard {shard.id}: {shard.ordem}, usando 0 ({e})')
                return 0

        shards = sorted(arquivo.shards, key=safe_ordem)
        conteudo = bytearray()

        for shard in shards:
            dados_fragmento = None
            print(f"Baixando shard {shard.hash} (ordem {shard.ordem})…")
            for maquina in shard.maquinas:
                try:
                    with Proxy(f"PYRONAME:{maquina.endereco}") as node:
                        dados_fragmento = node.get_mock(shard.hash)
                        print(f" • obtido de {maquina.endereco}")
                        break
                except Exception as e:
                    print(f"   erro ao baixar de {maquina.endereco}: {e}")
            if dados_fragmento is None:
                raise IOError(f"Não foi possível baixar o shard {shard.hash} de nenhum nó.")
            conteudo.extend(dados_fragmento)
        
        registra_logs("BAIXAR ARQUIVO", f"Arquivo {nome_arquivo} baixado com sucesso")

        print(f"Download de '{nome_arquivo}' concluído ({len(conteudo)} bytes).")
        return bytes(conteudo)


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

        registra_logs("REGISTRO DE ARQUIVO", f"Arquivo {nome} registrado com sucesso")
        return arquivo