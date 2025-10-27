"""
Disciplina: Compiladores.
Professor: Maurício Rodrigues Lima.
Linguagem: Python.
Nome da Linguagem Desenvolvida: ASI.
Alunos: Carlos Eduardo,
        Diony Tarso Ferreira Filho,
        Gabriel Jonas Lucio,
        Manel,
        Sergio Filho.
"""
# parser.py
# Importa o Lexer e Token
try:
    # Tenta importar do lexer (que deve se chamar lexer.py)
    from lexer import Lexer, Token, TIPOS_DE_DADOS, LITERAIS
except ImportError:
    # Fallback para os nomes antigos se 'lexer.py' não definir as constantes
    print("Erro crítico: Não foi possível encontrar 'lexer.py' ou as constantes de token.")
    print("Verifique se 'lexer.py' está no mesmo diretório.")
    exit(1)

# --- Definição dos Nós da Árvore Sintática (AST) ---
class No:
    """Classe base para todos os nós da AST."""
    pass

class DeclaracaoVariavel(No):
    def __init__(self, nome, tipo_dado, valor_inicial):
        self.nome = nome
        self.tipo_dado = tipo_dado
        self.valor_inicial = valor_inicial

    def __repr__(self):
        return f"DeclaracaoVariavel(nome={self.nome}, tipo={self.tipo_dado}, valor={self.valor_inicial})"

class DeclaracaoVetor(No):
    def __init__(self, nome, tipo_dado, dimensoes):
        self.nome = nome
        self.tipo_dado = tipo_dado
        self.dimensoes = dimensoes
    def __repr__(self):
        return f"DeclaracaoVetor(nome={self.nome}, tipo={self.tipo_dado}, dimensoes={self.dimensoes})"

class Atribuicao(No):
    def __init__(self, variavel, valor):
        self.variavel = variavel
        self.valor = valor

    def __repr__(self):
        return f"Atribuicao(variavel={self.variavel}, valor={self.valor})"

class NoVariavel(No):
    def __init__(self, nome):
        self.nome = nome

    def __repr__(self):
        return f"Variavel(nome={self.nome})"

class NoAcessoVetor(No):
    def __init__(self, nome, indices):
        self.nome = nome
        self.indices = indices

    def __repr__(self):
        return f"AcessoVetor(nome={self.nome}, indices={self.indices})"

class NoLiteral(No):
    def __init__(self, valor, tipo_literal):
        self.valor = valor
        self.tipo_literal = tipo_literal

    def __repr__(self):
        return f"Literal(valor={self.valor}, tipo={self.tipo_literal})"

class ExpressaoBinaria(No):
    """Representa uma operação binária (ex: a + b)."""

    def __init__(self, esquerda, operador, direita):
        self.esquerda = esquerda
        self.operador = operador
        self.direita = direita

    def __repr__(self):
        return f"ExpressaoBinaria(esquerda={self.esquerda}, op={self.operador}, direita={self.direita})"


# (Nós de if, for, while, etc. podem ser adicionados aqui)

class ChamadaCopiaTexto(No):
    """Representa a chamada: copiar_texto(destino, origem);"""
    def __init__(self, destino, origem):
        self.destino = destino # Deve ser um NoVariavel ou NoAcessoVetor
        self.origem = origem   # Deve ser uma Expressao (ex: NoLiteral de TEXTO)
    def __repr__(self):
        return f"ChamadaCopiaTexto(destino={self.destino}, origem={self.origem})"

# --- Classe do Parser ---

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicao_atual = 0

    def token_atual(self):
        return self.tokens[self.posicao_atual]

    def consumir(self, tipo_esperado):
        token = self.token_atual()
        if token.tipo == tipo_esperado:
            self.posicao_atual += 1
            return token
        else:
            raise Exception(
                f"Erro de sintaxe: Esperado {tipo_esperado}, mas encontrado {token.tipo} (valor: {token.valor}) na posição {self.posicao_atual}"
            )

    def parse(self):
        """Inicia a análise sintática."""
        arvore_sintatica = []
        while self.token_atual().tipo != 'FIM_DE_ARQUIVO':
            # (Aqui podemos adicionar 'parse_se', 'parse_while', etc. no futuro)
            token_atual = self.token_atual()
            # Roteamento baseado no primeiro token
            if token_atual.tipo == 'IDENTIFICADOR':
                arvore_sintatica.append(self.parse_declaracao_ou_atribuicao())
            # --- NOVA REGRA (Etapa 6) ---
            elif token_atual.tipo == 'PALAVRA_CHAVE_COPIAR_TEXTO':
                arvore_sintatica.append(self.parse_chamada_copia_texto())
            # (Adicione aqui PALAVRA_CHAVE_SE, _WHILE, _FOR, _ESCREVA se/quando os implementar)
            else:
                raise Exception(f"Erro de sintaxe: Instrução inesperada iniciada com {token_atual.tipo}")
        return arvore_sintatica

    def parse_declaracao_ou_atribuicao(self):
        nome_token = self.consumir('IDENTIFICADOR')

        if self.token_atual().tipo == 'PONTO':
            # --- DECLARAÇÃO (nome.tipo ...) ---
            self.consumir('PONTO')
            tipo_token = None
            if self.token_atual().tipo in TIPOS_DE_DADOS:
                tipo_token = self.consumir(self.token_atual().tipo)
            else:
                raise Exception(f"Erro de sintaxe: Esperado um TIPO DE DADO após '{nome_token.valor}.'")

            if self.token_atual().tipo == 'COLCHETE_ABRE':
                # --- DECLARAÇÃO DE VETOR/MATRIZ (nome.tipo[...]) ---
                dimensoes = self.parse_dimensoes_declaracao()
                self.consumir('PONTO_VIRGULA')
                return DeclaracaoVetor(nome=nome_token.valor, tipo_dado=tipo_token.tipo, dimensoes=dimensoes)

            elif self.token_atual().tipo == 'OP_ATRIBUICAO':
                # --- DECLARAÇÃO DE VARIÁVEL SIMPLES (nome.tipo = valor) ---
                self.consumir('OP_ATRIBUICAO')
                valor = self.parse_expressao()  # ATUALIZADO
                self.consumir('PONTO_VIRGULA')
                return DeclaracaoVariavel(nome=nome_token.valor, tipo_dado=tipo_token.tipo, valor_inicial=valor)
            else:
                raise Exception(f"Erro de sintaxe: Esperado '[' ou '=' após '{nome_token.valor}.{tipo_token.valor}'")

        elif self.token_atual().tipo == 'OP_ATRIBUICAO' or self.token_atual().tipo == 'COLCHETE_ABRE':
            # --- ATRIBUIÇÃO (nome = ... ou nome[...] = ...) ---
            self.posicao_atual -= 1
            variavel_alvo = self.parse_variavel_ou_acesso_vetor()

            self.consumir('OP_ATRIBUICAO')
            valor = self.parse_expressao()  # ATUALIZADO
            self.consumir('PONTO_VIRGULA')
            return Atribuicao(variavel=variavel_alvo, valor=valor)

        else:
            raise Exception(
                f"Erro de sintaxe: Inesperado token {self.token_atual().tipo} após o identificador {nome_token.valor}")

    def parse_chamada_copia_texto(self):
        """Analisa: copiar_texto(destino, origem);"""
        self.consumir('PALAVRA_CHAVE_COPIAR_TEXTO')
        self.consumir('PARENTESE_ABRE')

        # 1. Analisa o destino (deve ser uma variável ou acesso a vetor)
        destino = self.parse_variavel_ou_acesso_vetor()

        self.consumir('VIRGULA')

        # 2. Analisa a origem (pode ser qualquer expressão, ex: "texto" ou outra var)
        origem = self.parse_expressao()

        self.consumir('PARENTESE_FECHA')
        self.consumir('PONTO_VIRGULA')

        return ChamadaCopiaTexto(destino=destino, origem=origem)

    def parse_dimensoes_declaracao(self):
        dimensoes = []
        while self.token_atual().tipo == 'COLCHETE_ABRE':
            self.consumir('COLCHETE_ABRE')
            # A dimensão PODE ser uma expressão (ex: 10 + 5)
            # Mas vamos manter simples por agora: apenas números
            tamanho_dimensao = self.parse_primario()
            dimensoes.append(tamanho_dimensao)
            self.consumir('COLCHETE_FECHA')

        if not dimensoes:
            raise Exception("Erro de sintaxe: Esperado pelo menos uma dimensão para declaração de vetor.")

        return dimensoes

    def parse_variavel_ou_acesso_vetor(self):
        nome_token = self.consumir('IDENTIFICADOR')

        if self.token_atual().tipo == 'COLCHETE_ABRE':
            indices = []
            while self.token_atual().tipo == 'COLCHETE_ABRE':
                self.consumir('COLCHETE_ABRE')
                indices.append(self.parse_expressao())  # ATUALIZADO
                self.consumir('COLCHETE_FECHA')
            return NoAcessoVetor(nome=nome_token.valor, indices=indices)
        else:
            return NoVariavel(nome=nome_token.valor)

    # --- LÓGICA DE EXPRESSÃO ---
    # Implementação de um parser de precedência de operadores
    # parse_expressao -> parse_comparacao -> parse_termo -> parse_fator -> parse_primario

    def parse_expressao(self):
        """Ponto de entrada para expressões (atribuição, etc. - não implementado ainda)."""
        # Por enquanto, expressões são comparações
        return self.parse_comparacao()

    def parse_comparacao(self):
        """Analisa operadores de comparação (prioridade baixa): >, <, ==, !="""
        no = self.parse_termo()

        while self.token_atual().tipo == 'OP_RELACIONAL':
            token_op = self.consumir('OP_RELACIONAL')
            no_direito = self.parse_termo()
            no = ExpressaoBinaria(esquerda=no, operador=token_op.valor, direita=no_direito)

        return no

    def parse_termo(self):
        """Analisa adição e subtração (prioridade média): + -"""
        no = self.parse_fator()

        while self.token_atual().tipo == 'OP_ARITMETICO' and self.token_atual().valor in ('+', '-'):
            token_op = self.consumir('OP_ARITMETICO')
            no_direito = self.parse_fator()
            no = ExpressaoBinaria(esquerda=no, operador=token_op.valor, direita=no_direito)

        return no

    def parse_fator(self):
        """Analisa multiplicação e divisão (prioridade alta): * /"""
        no = self.parse_primario()

        while self.token_atual().tipo == 'OP_ARITMETICO' and self.token_atual().valor in ('*', '/'):
            token_op = self.consumir('OP_ARITMETICO')
            no_direito = self.parse_primario()
            no = ExpressaoBinaria(esquerda=no, operador=token_op.valor, direita=no_direito)

        return no

    def parse_primario(self):
        """Analisa literais, variáveis, e expressões entre parênteses (prioridade máxima)."""
        token = self.token_atual()

        if token.tipo in LITERAIS:
            self.posicao_atual += 1  # Consome o token literal
            if token.tipo == 'LITERAL_BOOLEANO':
                return NoLiteral(valor=(token.valor == 'verdadeiro'), tipo_literal='BOOLEANO')
            elif token.tipo == 'LITERAL_CARACTERE':
                # O lexer já removeu as aspas simples
                return NoLiteral(valor=token.valor, tipo_literal='CARACTERE')
            elif token.tipo == 'LITERAL_TEXTO':
                # O lexer já removeu as aspas duplas
                return NoLiteral(valor=token.valor, tipo_literal='TEXTO')
            elif token.tipo == 'NUMERO_DECIMAL':
                return NoLiteral(valor=float(token.valor), tipo_literal='DECIMAL')
            elif token.tipo == 'NUMERO_INTEIRO':
                return NoLiteral(valor=int(token.valor), tipo_literal='INTEIRO')

        elif token.tipo == 'IDENTIFICADOR':
            # Se encontrar um identificador, pode ser uma variável simples
            # ou um acesso a vetor/matriz. Delegamos a análise.
            return self.parse_variavel_ou_acesso_vetor()

        elif token.tipo == 'PARENTESE_ABRE':
            # Se encontrar um parêntese abrindo, analisamos a expressão dentro dele
            self.consumir('PARENTESE_ABRE')
            no_expressao_interna = self.parse_expressao()  # Chama recursivamente para analisar o conteúdo
            self.consumir('PARENTESE_FECHA')
            return no_expressao_interna  # Retorna a sub-árvore da expressão interna

        else:
            # Se não for nenhum dos casos acima, é um erro de sintaxe
            raise Exception(
                f"Erro de sintaxe: Token inesperado '{token.valor}' (tipo: {token.tipo}) encontrado durante a análise de expressão primária.")


# --- Bloco de Teste ---
if __name__ == "__main__":
    codigo_teste = """
// Arquivo de teste v2 - Parser
contador.inteiro = 10 + 5 * 2;
ativo.booleano = verdadeiro;
mapa.caractere[5][(10 + 1)];
mapa[0][0] = 'X';
contador = contador + (falso + 1); // Teste de booleano (falso = 0)
"""

    print("--- Testando Parser v2 (com Expressões) ---")

    try:
        lexer = Lexer(codigo_teste)
        tokens = lexer.criar_tokens()

        print("\n--- Árvore Sintática (AST) ---")
        parser = Parser(tokens)
        ast = parser.parse()

        for no in ast:
            print(no)

    except Exception as e:
        print(f"Erro durante o parsing: {e}")
