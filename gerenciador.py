import json
import os
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import StrEnum
from typing import Any

# --- CONFIGURAÇÕES E TIPOS DE DADOS ---

CATEGORIAS_PADRAO = [
    "Carregador", "Smartphones", "iOS", "Cabos", "Capas", "Pendrive",
    "Fones de ouvido", "Suporte", "Películas"
]

class Cores(StrEnum):
    """Enum para códigos de cores ANSI, facilitando a manutenção do estilo."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

@dataclass
class Produto:
    """Representa a estrutura de um produto usando um dataclass."""
    id: int
    nome: str
    categoria: str
    descricao: str
    quantidade: int
    preco: float

class GerenciadorEstoque:
    """Classe responsável pela lógica de negócio e persistência dos dados."""
    def __init__(self, nome_arquivo: str | Path = 'estoque.json', estoque_minimo: int = 10):
        self.caminho_arquivo = Path(nome_arquivo)
        self.estoque_minimo = estoque_minimo
        self.produtos: dict[int, Produto] = {}
        self.categorias: set[str] = set()
        self.proximo_id: int = 1
        self._carregar_dados()

    def _carregar_dados(self) -> None:
        """Carrega os dados do arquivo JSON, garantindo compatibilidade com versões antigas."""
        if not self.caminho_arquivo.exists():
            self.categorias.update(CATEGORIAS_PADRAO)
            return
        try:
            dados = json.loads(self.caminho_arquivo.read_text(encoding='utf-8'))
            self.proximo_id = dados.get('proximo_id', 1)
            categorias_salvas = dados.get('categorias', [])
            self.categorias = set(categorias_salvas if categorias_salvas else CATEGORIAS_PADRAO)
            produtos_carregados = dados.get('produtos', {})
            for id_p, dados_p in produtos_carregados.items():
                dados_p.setdefault('descricao', 'Sem descrição')
                self.produtos[int(id_p)] = Produto(**dados_p)
        except (json.JSONDecodeError, IOError):
            print(f"{Cores.WARNING}Aviso: Arquivo '{self.caminho_arquivo}' corrompido. Começando com dados limpos.{Cores.ENDC}")
            self.categorias.update(CATEGORIAS_PADRAO)

    def _salvar_dados(self) -> None:
        """Salva o estado atual da memória no arquivo JSON."""
        dados_para_salvar = {
            'proximo_id': self.proximo_id,
            'categorias': sorted(list(self.categorias)),
            'produtos': {p_id: asdict(produto) for p_id, produto in self.produtos.items()}
        }
        json_string = json.dumps(dados_para_salvar, indent=4, ensure_ascii=False)
        self.caminho_arquivo.write_text(json_string, encoding='utf-8')

    def adicionar_produto(self, nome: str, categoria: str, descricao: str, quantidade: int, preco: float) -> Produto:
        """Adiciona um novo produto ao estoque."""
        id_novo = self.proximo_id
        produto_novo = Produto(id=id_novo, nome=nome, categoria=categoria, descricao=descricao, quantidade=quantidade, preco=preco)
        self.produtos[id_novo] = produto_novo
        self.proximo_id += 1
        self._salvar_dados()
        return produto_novo

    def buscar_produto(self, id_produto: int) -> Produto | None:
        """Busca um produto pelo seu ID."""
        return self.produtos.get(id_produto)

    def buscar_produtos_por_termo(self, termo: str) -> list[Produto]:
        """Busca produtos por ID (exato), nome ou categoria (parcial e case-insensitive)."""
        termo_lower = termo.lower()
        resultados = []
        for produto in self.produtos.values():
            if produto in resultados:
                continue
            if termo == str(produto.id) or \
               termo_lower in produto.nome.lower() or \
               termo_lower in produto.categoria.lower():
                resultados.append(produto)
        return resultados

    def atualizar_produto(self, id_produto: int, nome: str | None, categoria: str | None, descricao: str | None) -> Produto | None:
        """Atualiza os dados de um produto existente."""
        produto = self.buscar_produto(id_produto)
        if not produto: return None
        if nome: produto.nome = nome
        if categoria: produto.categoria = categoria
        if descricao: produto.descricao = descricao
        self._salvar_dados()
        return produto

    def remover_produto(self, id_produto: int) -> bool:
        """Remove um produto do estoque."""
        if id_produto in self.produtos:
            del self.produtos[id_produto]
            self._salvar_dados()
            return True
        return False

    def movimentar_estoque(self, id_produto: int, quantidade: int) -> Produto | None:
        """Adiciona ou remove uma quantidade do estoque de um produto."""
        produto = self.buscar_produto(id_produto)
        if not produto: return None
        if produto.quantidade + quantidade < 0:
            raise ValueError("Quantidade de saída maior que o estoque disponível.")
        produto.quantidade += quantidade
        self._salvar_dados()
        return produto

    def obter_estatisticas(self) -> dict[str, Any]:
        """Calcula as estatísticas gerais do estoque."""
        total_produtos = len(self.produtos)
        if total_produtos == 0:
            return {'total_produtos': 0, 'total_itens': 0, 'baixo_estoque': 0, 'valor_total': 0.0}
        produtos_lista = self.produtos.values()
        return {
            'total_produtos': total_produtos,
            'total_itens': sum(p.quantidade for p in produtos_lista),
            'baixo_estoque': sum(1 for p in produtos_lista if p.quantidade < self.estoque_minimo),
            'valor_total': sum(p.quantidade * p.preco for p in produtos_lista)
        }
    
    def obter_categorias(self) -> list[str]:
        """Retorna uma lista ordenada de todas as categorias."""
        return sorted(list(self.categorias))

    def adicionar_categoria(self, nova_categoria: str) -> None:
        """Adiciona uma nova categoria à lista."""
        self.categorias.add(nova_categoria.strip())
        self._salvar_dados()


class InterfaceUsuario:
    """Classe responsável por toda a interação com o usuário (menus, inputs, prints)."""
    def __init__(self, gerenciador: GerenciadorEstoque):
        self.gerenciador = gerenciador

    @staticmethod
    def _limpar_tela():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def _pressione_enter_para_continuar():
        input(f"\n{Cores.OKCYAN}Pressione Enter para continuar...{Cores.ENDC}")

    def _ler_texto(self, prompt: str, permitir_vazio: bool = False) -> str:
        while True:
            texto = input(prompt).strip()
            if texto or permitir_vazio: return texto
            self.exibir_erro("Este campo não pode ser vazio.")

    def _ler_inteiro_positivo(self, prompt: str) -> int:
        while True:
            try:
                numero = int(input(prompt))
                if numero >= 0: return numero
                self.exibir_erro("O número deve ser zero ou positivo.")
            except ValueError:
                self.exibir_erro("Por favor, digite um número inteiro válido.")

    def _ler_float_positivo(self, prompt: str) -> float:
        while True:
            try:
                valor_str = input(prompt).replace(',', '.')
                numero = float(valor_str)
                if numero >= 0.0: return numero
                self.exibir_erro("O número deve ser positivo.")
            except ValueError:
                self.exibir_erro("Digite um número válido (ex: 29.90).")

    def exibir_sucesso(self, mensagem: str):
        print(f"\n{Cores.OKGREEN}{mensagem}{Cores.ENDC}")

    def exibir_erro(self, mensagem: str):
        print(f"{Cores.FAIL}Erro: {mensagem}{Cores.ENDC}")

    def exibir_aviso(self, mensagem: str):
        print(f"{Cores.WARNING}{mensagem}{Cores.ENDC}")

    def _selecionar_ou_criar_categoria(self) -> str | None:
        print(f"\n{Cores.HEADER}--- Selecione uma Categoria ---{Cores.ENDC}")
        categorias = self.gerenciador.obter_categorias()
        for i, categoria in enumerate(categorias, 1):
            print(f"[{i}] {categoria}")
        print(f"\n{Cores.OKCYAN}[N] Cadastrar NOVA categoria{Cores.ENDC}")
        while True:
            escolha = input("Escolha o número, [N] para nova, ou 'cancelar': ").strip().lower()
            if escolha == 'cancelar': return None
            if escolha == 'n':
                nova_categoria = self._ler_texto("Digite o nome da nova categoria: ")
                self.gerenciador.adicionar_categoria(nova_categoria)
                self.exibir_sucesso(f"Categoria '{nova_categoria}' criada!")
                return nova_categoria
            try:
                indice = int(escolha) - 1
                if 0 <= indice < len(categorias): return categorias[indice]
                else: self.exibir_erro("Número fora do intervalo.")
            except ValueError:
                self.exibir_erro("Opção inválida.")

    def adicionar_produto(self):
        self._limpar_tela()
        print(f"{Cores.HEADER}--- Adicionar Novo Produto ---{Cores.ENDC}")
        nome = self._ler_texto("Nome do produto: ")
        categoria = self._selecionar_ou_criar_categoria()
        if categoria is None:
            print("\nOperação cancelada."); self._pressione_enter_para_continuar()
            return
        print(f"Categoria selecionada: {Cores.OKCYAN}{categoria}{Cores.ENDC}")
        descricao = self._ler_texto("Descrição do produto: ")
        quantidade = self._ler_inteiro_positivo("Quantidade inicial: ")
        preco = self._ler_float_positivo("Preço (R$): ")
        produto = self.gerenciador.adicionar_produto(nome, categoria, descricao, quantidade, preco)
        self.exibir_sucesso(f"Produto '{produto.nome}' (ID: {produto.id}) adicionado!")
        self._pressione_enter_para_continuar()

    def _selecionar_produto(self, titulo: str) -> Produto | None:
        self._limpar_tela()
        print(f"{Cores.HEADER}{titulo}{Cores.ENDC}")
        if not self.gerenciador.produtos:
            self.exibir_aviso("Nenhum produto cadastrado.")
            self._pressione_enter_para_continuar()
            return None
        print(f"{Cores.BOLD}{'ID':<5}{'Nome':<30}{'Qtd':>5}{Cores.ENDC}")
        print("-" * 42)
        produtos_ordenados = sorted(self.gerenciador.produtos.values(), key=lambda p: p.nome)
        for produto in produtos_ordenados:
            cor_qtd = Cores.WARNING if produto.quantidade < self.gerenciador.estoque_minimo else ""
            print(f"{produto.id:<5}{produto.nome:<30}{cor_qtd}{produto.quantidade:>5}{Cores.ENDC}")
        print("-" * 42)
        while True:
            id_str = self._ler_texto("Digite o ID do produto (ou 'cancelar'): ")
            if id_str.lower() == 'cancelar': return None
            try:
                produto = self.gerenciador.buscar_produto(int(id_str))
                if produto: return produto
                self.exibir_erro("ID não encontrado.")
            except ValueError:
                self.exibir_erro("ID inválido.")

    def editar_produto(self):
        produto = self._selecionar_produto("--- Editar Produto ---")
        if not produto: return
        print(f"\n{Cores.OKCYAN}Editando: {produto.nome}{Cores.ENDC} (Deixe em branco para não alterar)")
        novo_nome = self._ler_texto(f"Nome ({produto.nome}): ", permitir_vazio=True) or None
        nova_categoria = self._ler_texto(f"Categoria ({produto.categoria}): ", permitir_vazio=True) or None
        nova_descricao = self._ler_texto(f"Descrição ({produto.descricao}): ", permitir_vazio=True) or None
        self.gerenciador.atualizar_produto(produto.id, novo_nome, nova_categoria, nova_descricao)
        self.exibir_sucesso("Produto atualizado com sucesso!")
        self._pressione_enter_para_continuar()

    def remover_produto(self):
        produto = self._selecionar_produto("--- Remover Produto ---")
        if not produto: return
        confirmacao = input(f"\n{Cores.WARNING}Tem certeza que quer remover '{produto.nome}'? (s/n): {Cores.ENDC}").lower()
        if confirmacao == 's':
            if self.gerenciador.remover_produto(produto.id):
                self.exibir_sucesso("Produto removido.")
        else:
            print("\nOperação cancelada.")
        self._pressione_enter_para_continuar()

    def registrar_movimentacao(self):
        produto = self._selecionar_produto("--- Movimentar Estoque ---")
        if not produto: return
        print(f"\nProduto: {Cores.OKCYAN}{produto.nome}{Cores.ENDC} | Estoque: {Cores.BOLD}{produto.quantidade}{Cores.ENDC}")
        tipo_mov = input("Digite 'E' para Entrada ou 'S' para Saída: ").upper()
        if tipo_mov not in ['E', 'S']:
            self.exibir_erro("Opção inválida."); self._pressione_enter_para_continuar()
            return
        qtd = self._ler_inteiro_positivo("Digite a quantidade: ")
        try:
            self.gerenciador.movimentar_estoque(produto.id, qtd if tipo_mov == 'E' else -qtd)
            self.exibir_sucesso(f"{'Entrada' if tipo_mov == 'E' else 'Saída'} registrada.")
        except ValueError as e:
            self.exibir_erro(str(e))
        self._pressione_enter_para_continuar()

    def _exibir_lista_produtos(self, lista_produtos: list[Produto], titulo: str):
        self._limpar_tela()
        print(f"{Cores.HEADER}{titulo}{Cores.ENDC}")
        if not lista_produtos:
            self.exibir_aviso("Nenhum produto encontrado.")
            return
        print(f"\n{Cores.BOLD}{'ID':<4} {'Nome':<25} {'Categoria':<15} {'Qtd':>5} {'Preço (R$)':>12}{Cores.ENDC}")
        print("-" * 78)
        for p in sorted(lista_produtos, key=lambda prod: prod.nome):
            cor_qtd = Cores.WARNING if p.quantidade < self.gerenciador.estoque_minimo else ""
            preco_str = f"{p.preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            print(f"{p.id:<4} {p.nome:<25} {p.categoria:<15} {cor_qtd}{p.quantidade:>5}{Cores.ENDC} {preco_str:>12}")
        print("-" * 78)

    def _relatorio_todos_produtos(self):
        self._exibir_lista_produtos(list(self.gerenciador.produtos.values()), "--- Relatório: Todos os Produtos ---")

    def _relatorio_estoque_baixo(self):
        produtos_baixo = [p for p in self.gerenciador.produtos.values() if p.quantidade < self.gerenciador.estoque_minimo]
        if not produtos_baixo:
            self._limpar_tela()
            print(f"{Cores.HEADER}--- Relatório: Produtos com Estoque Baixo ---{Cores.ENDC}")
            self.exibir_sucesso(f"Nenhum produto com estoque abaixo de {self.gerenciador.estoque_minimo} unidades.")
            return
        self._exibir_lista_produtos(produtos_baixo, "--- Relatório: Produtos com Estoque Baixo ---")

    def buscar_produto_dialogo(self):
        while True:
            self._limpar_tela()
            print(f"{Cores.HEADER}--- Buscar Produto ---{Cores.ENDC}")
            termo = self._ler_texto("Digite o termo para buscar (ou 'cancelar' para voltar): ", permitir_vazio=True)
            if termo.lower() == 'cancelar' or not termo:
                break
            resultados = self.gerenciador.buscar_produtos_por_termo(termo)
            self._exibir_lista_produtos(resultados, f"Resultados da Busca por '{termo}'")
            self._pressione_enter_para_continuar()
    
    def _ver_detalhes_produto(self):
        produto = self._selecionar_produto("--- Ver Detalhes de um Produto ---")
        if not produto: return
        self._limpar_tela()
        print(f"{Cores.HEADER}--- Detalhes do Produto ---{Cores.ENDC}")
        print(f"{Cores.BOLD}{'ID:':<12}{Cores.ENDC}{produto.id}")
        print(f"{Cores.BOLD}{'Nome:':<12}{Cores.ENDC}{produto.nome}")
        print(f"{Cores.BOLD}{'Categoria:':<12}{Cores.ENDC}{produto.categoria}")
        print(f"{Cores.BOLD}{'Descrição:':<12}{Cores.ENDC}{produto.descricao}")
        print(f"{Cores.BOLD}{'Quantidade:':<12}{Cores.ENDC}{produto.quantidade}")
        preco_str = f"R$ {produto.preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        print(f"{Cores.BOLD}{'Preço:':<12}{Cores.ENDC}{preco_str}")

    # [ALTERADO] Menu de relatórios simplificado.
    def _menu_relatorios(self):
        acoes = {
            '1': self._relatorio_todos_produtos,
            '2': self._relatorio_estoque_baixo,
            '3': self._ver_detalhes_produto
        }
        while True:
            self._limpar_tela()
            print(f"{Cores.HEADER}--- Menu de Relatórios ---{Cores.ENDC}")
            print("[1] Listar todos os produtos")
            print("[2] Listar produtos com estoque baixo")
            print(f"{Cores.OKCYAN}[3] Ver Detalhes de um Produto{Cores.ENDC}")
            print("[4] Voltar ao menu principal")
            opcao = input("\nEscolha uma opção: ")
            if opcao == '4': break
            acao = acoes.get(opcao)
            if acao:
                acao()
                self._pressione_enter_para_continuar()
            else:
                self.exibir_erro("Opção inválida.")
                self._pressione_enter_para_continuar()

    def exibir_dashboard(self):
        self._limpar_tela()
        stats = self.gerenciador.obter_estatisticas()
        cor_alerta = Cores.FAIL if stats['baixo_estoque'] > 0 else Cores.OKGREEN
        LARGURA_TOTAL, LARGURA_COL_1, LARGURA_COL_2 = 76, 37, 38
        titulo_centralizado = "EstoqueFacil - Dashboard".center(LARGURA_TOTAL)
        celula_esq_l1 = f" Quantidade de Produtos Únicos: {stats['total_produtos']}".ljust(LARGURA_COL_1)
        celula_dir_l1 = f" Total de Itens em Estoque: {stats['total_itens']}".ljust(LARGURA_COL_2)
        celula_esq_l2 = f" Produtos com Estoque Baixo: {stats['baixo_estoque']}".ljust(LARGURA_COL_1)
        celula_dir_l2 = f" Valor Total do Estoque (R$): {stats['valor_total']:.2f}".ljust(LARGURA_COL_2)
        dashboard = f"""
{Cores.BOLD}╔{'═' * LARGURA_TOTAL}╗
║{Cores.HEADER}{titulo_centralizado}{Cores.ENDC}║
╠{'═' * LARGURA_COL_1}╦{'═' * LARGURA_COL_2}╣
║{Cores.OKBLUE}{celula_esq_l1}{Cores.ENDC}║{celula_dir_l1}║
║{cor_alerta}{celula_esq_l2}{Cores.ENDC}║{celula_dir_l2}║
╚{'═' * LARGURA_COL_1}╩{'═' * LARGURA_COL_2}╝{Cores.ENDC}"""
        print(dashboard)

    def menu_principal(self):
        self.exibir_dashboard()
        print("\n--- MENU PRINCIPAL ---")
        print(f"{'[1] Adicionar Produto'.ljust(28)}{'[2] Editar Produto'.ljust(28)}{'[3] Movimentar Estoque'}")
        print(f"{'[4] Relatórios'.ljust(28)}{'[5] Remover Produto'.ljust(28)}{Cores.OKCYAN}{'[6] Buscar Produto'.ljust(28)}{Cores.ENDC}")
        print(f"{Cores.FAIL}{'[7] Sair'.ljust(28)}{Cores.ENDC}")
        return input(f"\n{Cores.BOLD}Escolha uma opção: {Cores.ENDC}")

    def iniciar(self):
        """Loop principal da aplicação que gerencia o menu."""
        acoes = {
            '1': self.adicionar_produto, '2': self.editar_produto,
            '3': self.registrar_movimentacao, '4': self._menu_relatorios,
            '5': self.remover_produto, '6': self.buscar_produto_dialogo,
        }
        while True:
            opcao = self.menu_principal()
            if opcao == '7':
                print(f"\n{Cores.OKCYAN}Saindo do sistema. Até logo!{Cores.ENDC}")
                sys.exit()
            acao = acoes.get(opcao)
            if acao:
                acao()
            else:
                self.exibir_erro("Opção inválida.")
                self._pressione_enter_para_continuar()

def main():
    """Função principal para inicializar e rodar o sistema."""
    gerenciador = GerenciadorEstoque(nome_arquivo='meu_estoque.json', estoque_minimo=10)
    ui = InterfaceUsuario(gerenciador)
    ui.iniciar()

if __name__ == "__main__":
    main()