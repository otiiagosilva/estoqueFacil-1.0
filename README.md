Manual Técnico – Sistema de Gerenciamento de Estoque
1. Visão Geral
Esta aplicação é um sistema de gerenciamento de estoque simples, desenvolvido com o micro-framework web Flask em Python. Ele permite que o usuário realize as operações básicas de um CRUD (Criar, Ler, Atualizar e Excluir) para produtos, além de funcionalidades para movimentar o estoque, buscar itens e filtrar produtos com baixo volume.

Todos os dados são armazenados localmente em um arquivo JSON (estoque_v2.json), tornando a aplicação leve e sem a necessidade de um banco de dados complexo.

2. Bibliotecas e Tecnologias Utilizadas
2.1. Flask
Descrição: É o coração da aplicação. Flask é um micro-framework para desenvolvimento web em Python. Ele é responsável por gerenciar as rotas (URLs), processar as requisições dos usuários (como cliques em botões e preenchimento de formulários) e renderizar as páginas HTML que são exibidas no navegador.

Uso no Código:

app = Flask(__name__): Inicializa a aplicação Flask.

@app.route(...): Decoradores que definem qual função Python será executada para uma determinada URL.

render_template(): Renderiza um arquivo HTML, permitindo passar variáveis do Python para a página web.

request: Objeto global do Flask que contém todas as informações da requisição atual do usuário (dados de formulários, parâmetros de URL, etc.).

redirect(), url_for(): Funções para redirecionar o usuário para outras páginas da aplicação.

flash(): Cria mensagens de alerta temporárias para dar feedback ao usuário (ex: "Produto adicionado com sucesso!"). Requer a configuração de uma app.secret_key.

2.2. JSON (JavaScript Object Notation)
Descrição: É uma biblioteca padrão do Python para trabalhar com o formato de dados JSON. Neste projeto, ela é usada como um sistema de banco de dados simples para persistir os dados dos produtos.

Uso no Código:

json.load(f): Lê os dados de um arquivo JSON e os converte em um dicionário Python.

json.dump(dados, f, ...): Pega um dicionário Python e o escreve em um arquivo no formato JSON. O argumento indent=4 formata o arquivo para que seja legível por humanos.

2.3. OS
Descrição: Biblioteca padrão do Python que fornece uma maneira de interagir com o sistema operacional.

Uso no Código:

os.path.exists(NOME_ARQUIVO): Verifica se o arquivo de banco de dados (estoque_v2.json) já existe. Isso é crucial para evitar erros na primeira vez que a aplicação é executada.

3. Funções de Gerenciamento de Dados
Estas são as funções que lidam diretamente com a leitura e escrita no arquivo estoque_v2.json.

3.1. carregar_dados()
Propósito: Ler os dados do arquivo JSON.

Lógica:

Verifica se o arquivo estoque_v2.json existe.

Se não existir, retorna uma estrutura de dados padrão (um dicionário com um contador proximo_id e uma lista vazia de produtos). Isso garante que a aplicação não quebre na primeira execução.

Se o arquivo existir, ele é aberto em modo de leitura ('r'), e seu conteúdo é carregado e retornado como um dicionário Python.

3.2. salvar_dados(dados)
Propósito: Gravar os dados (modificados) de volta no arquivo JSON.

Lógica:

Abre o arquivo estoque_v2.json em modo de escrita ('w'). O modo 'w' apaga o conteúdo anterior do arquivo antes de escrever o novo.

Usa json.dump() para converter o dicionário Python dados para o formato JSON e salvá-lo no arquivo.

4. Rotas da Aplicação (Endpoints)
As rotas são as URLs que o usuário pode acessar. Cada uma está associada a uma função Python.

@app.route('/') -> index()

Descrição: É a página principal (dashboard). Exibe a lista de todos os produtos.

Funcionalidades:

Carrega todos os produtos usando carregar_dados().

Implementa a lógica de busca: filtra os produtos cujo nome ou categoria contenham o termo digitado pelo usuário.

Implementa a lógica de filtro: mostra apenas os produtos com quantidade abaixo do ESTOQUE_MINIMO se essa opção for selecionada.

Renderiza o template index.html, passando a lista de produtos filtrados para exibição.

@app.route('/produto/novo', methods=['GET', 'POST']) -> adicionar_produto()

Descrição: Rota para criar um novo produto.

Métodos:

GET: Simplesmente exibe o formulário (form_produto.html) para o usuário preencher os dados do novo produto.

POST: É acionado quando o usuário envia o formulário. A função coleta os dados (request.form), cria um novo registro de produto com um ID único, salva no arquivo JSON e redireciona o usuário de volta para a página principal.

@app.route('/produto/editar/<produto_id>', methods=['GET', 'POST']) -> editar_produto(produto_id)

Descrição: Rota para modificar um produto existente, identificado pelo seu produto_id.

Métodos:

GET: Busca o produto pelo ID, preenche o formulário (form_produto.html) com os dados atuais do produto e o exibe para o usuário.

POST: Coleta os dados modificados do formulário, atualiza o dicionário do produto correspondente, salva os dados e redireciona para a página principal.

@app.route('/produto/remover/<produto_id>', methods=['POST']) -> remover_produto(produto_id)

Descrição: Rota para excluir um produto.

Lógica: Recebe o ID do produto a ser removido, encontra-o no dicionário de produtos, remove o item (del dados['produtos'][produto_id]), salva a alteração e redireciona para a página principal.

@app.route('/produto/estoque/<produto_id>', methods=['POST']) -> movimentar_estoque(produto_id)

Descrição: Rota para adicionar ou remover unidades do estoque de um produto.

Lógica: Recebe o ID do produto e a quantidade a ser movimentada (positiva para entrada, negativa para saída). Atualiza o campo quantidade do produto, garantindo que o estoque nunca fique negativo. Salva os dados e exibe alertas de feedback, incluindo um aviso se o estoque ficar baixo.

5. Execução da Aplicação
A seção if __name__ == '__main__': garante que o servidor de desenvolvimento do Flask (app.run()) só seja iniciado quando o script app.py for executado diretamente.

debug=True ativa o modo de depuração, que reinicia o servidor automaticamente a cada alteração no código e fornece páginas de erro detalhadas. Importante: este modo nunca deve ser usado em um ambiente de produção.
