Claro, aqui está a versão atualizada do `README.md` com as alterações solicitadas.

-----

# EstoqueFácil - Sistema de Gerenciamento de Estoque em Console

**Linguagem:** Python 3.10+

## Sobre o Projeto

**EstoqueFácil** é um sistema de gerenciamento de estoque robusto e interativo, desenvolvido em Python, que opera diretamente no terminal. Ele foi projetado para ser uma ferramenta simples e eficiente para o controle completo sobre produtos, categorias e movimentações de estoque.

O sistema persiste os dados em um arquivo `json`, garantindo que as informações não sejam perdidas entre as sessões. A interface é colorida e organizada para facilitar a visualização e a interação do usuário. **Este projeto foi desenvolvido como trabalho final para a disciplina de Lógica de Programação.**

-----

## Funcionalidades Principais

  * **Dashboard Inicial:** Visão geral e rápida do status do estoque.
  * **CRUD de Produtos Completo:** Crie, leia, atualize e remova produtos de forma intuitiva.
  * **Gerenciamento de Categorias:** Adicione novas categorias dinamicamente.
  * **Movimentação de Estoque:** Registre entradas e saídas de produtos.
  * **Relatórios Detalhados:**
      * Liste todos os produtos.
      * Filtre produtos com estoque baixo.
      * Visualize todos os detalhes de um produto específico.
  * **Busca Inteligente:** Encontre produtos por ID, nome ou categoria.
  * **Persistência de Dados:** Todo o estoque é salvo em um arquivo `estoque.json`.
  * **Interface de Usuário Amigável:** Menus claros e feedback visual com cores para facilitar o uso.
  * **Validação de Entradas:** Tratamento de erros para garantir que o usuário insira dados válidos.

-----

## Como Executar

Este projeto não requer a instalação de bibliotecas externas, pois utiliza apenas módulos padrão do Python.

1.  **Clone o repositório (ou baixe os arquivos):**

    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd seu-repositorio
    ```

2.  **Execute o script Python:**

    ```bash
    python nome_do_seu_arquivo.py
    ```

    > Ao ser executado pela primeira vez, o sistema criará um arquivo `meu_estoque.json` no mesmo diretório para armazenar os dados.

-----

## Arquitetura e Conceitos

O projeto foi estruturado em duas classes principais para separar a lógica de negócio da interface do usuário (Princípio da Separação de Responsabilidades):

  * `GerenciadorEstoque`: A classe "cérebro" do sistema. Ela é responsável por toda a manipulação de dados: carregar, salvar, adicionar, remover, atualizar produtos e calcular estatísticas. Não possui nenhum código de `print` ou `input`, tornando-a reutilizável.
  * `InterfaceUsuario`: Responsável por toda a interação com o usuário. Exibe menus, solicita dados, formata e exibe informações. Ela atua como a camada de "apresentação", consumindo os métodos da `GerenciadorEstoque`.

-----

## Bibliotecas Utilizadas

O projeto utiliza exclusivamente bibliotecas padrão do Python:

  * **`json`**: Essencial para a persistência dos dados. É usado para serializar (converter de objeto Python para string JSON) e desserializar (converter de string JSON para objeto Python) o estado do estoque, salvando e carregando as informações do arquivo `.json`.
  * **`os`**: Utilizado para interagir com o sistema operacional, especificamente para a função `os.system('cls' ou 'clear')`, que limpa a tela do console, melhorando a experiência do usuário.
  * **`sys`**: Usado para a função `sys.exit()`, que encerra a execução do programa de forma limpa quando o usuário escolhe a opção "Sair".
  * **`pathlib.Path`**: Oferece uma abordagem moderna e orientada a objetos para manipular caminhos de arquivos, tornando o código mais legível e compatível entre diferentes sistemas operacionais (Windows, Linux, macOS).
  * **`dataclasses`**: O decorador `@dataclass` é usado para criar a classe `Produto`. Ele gera automaticamente métodos especiais como `__init__`, `__repr__`, entre outros, a partir das anotações de tipo, reduzindo a quantidade de código boilerplate. A função `asdict` é usada para converter uma instância de `Produto` em um dicionário, facilitando a sua serialização para JSON.
  * **`enum.StrEnum`**: Utilizada para criar a enumeração `Cores`. Isso organiza os códigos de escape ANSI para cores do terminal, tornando o código mais legível e fácil de manter em vez de usar strings "mágicas" espalhadas pelo código.
  * **`typing`**: Fornece suporte para anotações de tipo (`Any`, `list`, `dict`, etc.), o que melhora a legibilidade, a manutenção e permite a verificação estática de tipos.

-----

## Detalhamento das Classes e Métodos

### `Produto(dataclass)`

É a estrutura de dados que representa um produto.

  * `id: int`: Identificador único.
  * `nome: str`: Nome do produto.
  * `categoria: str`: Categoria à qual o produto pertence.
  * `descricao: str`: Descrição detalhada do produto.
  * `quantidade: int`: Quantidade em estoque.
  * `preco: float`: Preço unitário.

### `GerenciadorEstoque`

Classe que encapsula toda a lógica de negócio e manipulação de dados.

  * `__init__(...)`: Inicializa o gerenciador, define o caminho do arquivo de estoque e carrega os dados existentes.
  * `_carregar_dados()`: Método privado que lê o arquivo JSON e popula as estruturas de dados em memória (`self.produtos`, `self.categorias`, `self.proximo_id`). Inclui tratamento de erro para arquivos corrompidos ou inexistentes.
  * `_salvar_dados()`: Método privado que escreve o estado atual dos dados em memória para o arquivo JSON. É chamado sempre que uma alteração é realizada.
  * `adicionar_produto(...)`: Cria uma nova instância de `Produto`, atribui um novo ID, adiciona ao dicionário de produtos e salva os dados.
  * `buscar_produto(id_produto)`: Retorna um objeto `Produto` pelo seu ID, ou `None` se não for encontrado.
  * `buscar_produtos_por_termo(termo)`: Realiza uma busca case-insensitive por ID (exato), nome ou categoria (parcial). Retorna uma lista de produtos encontrados.
  * `atualizar_produto(...)`: Modifica os atributos de um produto existente com base no seu ID.
  * `remover_produto(id_produto)`: Remove um produto do dicionário pelo ID.
  * `movimentar_estoque(id_produto, quantidade)`: Adiciona ou subtrai uma `quantidade` do estoque de um produto. Lança um `ValueError` se a retirada for maior que o estoque disponível.
  * `obter_estatisticas()`: Calcula e retorna um dicionário com as estatísticas do dashboard (total de produtos, total de itens, etc.).
  * `obter_categorias()`: Retorna uma lista ordenada das categorias disponíveis.
  * `adicionar_categoria(nova_categoria)`: Adiciona uma nova categoria ao conjunto de categorias.

### `InterfaceUsuario`

Classe responsável por toda a interação com o terminal.

  * `_limpar_tela()`: Limpa o console.
  * `_ler_texto()`, `_ler_inteiro_positivo()`, `_ler_float_positivo()`: Métodos privados de ajuda para capturar e validar as entradas do usuário, garantindo que os dados sejam do tipo e formato corretos.
  * `exibir_sucesso()`, `exibir_erro()`, `exibir_aviso()`: Exibem mensagens formatadas com cores para fornecer feedback claro ao usuário.
  * `_selecionar_ou_criar_categoria()`: Apresenta um menu para o usuário escolher uma categoria existente ou criar uma nova.
  * `adicionar_produto()`: Guia o usuário pelo processo de inserção dos dados de um novo produto.
  * `_selecionar_produto()`: Exibe uma lista de produtos e solicita que o usuário escolha um pelo ID. É a base para as operações de edição, remoção e visualização.
  * `editar_produto()`: Permite ao usuário alterar o nome, categoria e descrição de um produto selecionado.
  * `remover_produto()`: Pede confirmação e remove o produto selecionado.
  * `registrar_movimentacao()`: Controla o fluxo para registrar entrada ou saída de itens de um produto.
  * `_exibir_lista_produtos(...)`: Método genérico para formatar e exibir uma lista de produtos em formato de tabela.
  * `_menu_relatorios()`: Submenu que dá acesso às diferentes opções de visualização de dados.
  * `exibir_dashboard()`: Formata e exibe o painel inicial com as estatísticas do estoque.
  * `menu_principal()`: Exibe o menu principal de ações.
  * `iniciar()`: O loop principal da aplicação, que exibe o menu, captura a escolha do usuário e chama o método apropriado.

-----

## Funcionamento do CRUD

O termo **CRUD** refere-se às quatro operações fundamentais da persistência de dados: Criar (Create), Ler (Read), Atualizar (Update) e Excluir (Delete). Veja como elas são implementadas no projeto:

### **C**reate (Criar)

  * **Ação do Usuário:** Escolhe "Adicionar Produto" no menu.
  * **Métodos Envolvidos:**
      * `InterfaceUsuario.adicionar_produto()`: Coleta os dados do novo produto.
      * `GerenciadorEstoque.adicionar_produto()`: Cria a instância do produto, salva em memória e persiste no arquivo JSON.

### **R**ead (Ler/Consultar)

  * **Ação do Usuário:** Acessa relatórios, busca um produto ou visualiza o dashboard.
  * **Métodos Envolvidos:**
      * `InterfaceUsuario._relatorio_todos_produtos()`: Exibe todos os produtos.
      * `InterfaceUsuario.buscar_produto_dialogo()`: Permite a busca por um termo.
          * Usa `GerenciadorEstoque.buscar_produtos_por_termo()`.
      * `InterfaceUsuario._ver_detalhes_produto()`: Mostra todos os dados de um único produto.
          * Usa `GerenciadorEstoque.buscar_produto()`.
      * `InterfaceUsuario.exibir_dashboard()`: Mostra as estatísticas gerais.
          * Usa `GerenciadorEstoque.obter_estatisticas()`.

### **U**pdate (Atualizar)

  * **Ação do Usuário:** Escolhe "Editar Produto" ou "Movimentar Estoque".
  * **Métodos Envolvidos:**
      * `InterfaceUsuario.editar_produto()`: Coleta os novos dados para nome, categoria e descrição.
          * Usa `GerenciadorEstoque.atualizar_produto()`.
      * `InterfaceUsuario.registrar_movimentacao()`: Coleta a quantidade para entrada ou saída.
          * Usa `GerenciadorEstoque.movimentar_estoque()`.

### **D**elete (Excluir)

  * **Ação do Usuário:** Escolhe "Remover Produto" no menu.
  * **Métodos Envolvidos:**
      * `InterfaceUsuario.remover_produto()`: Pede a seleção do produto e a confirmação final.
      * `GerenciadorEstoque.remover_produto()`: Remove o produto do dicionário em memória e atualiza o arquivo JSON.
