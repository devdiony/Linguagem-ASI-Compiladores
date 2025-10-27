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
# ------------------------------
# Parser/AST da linguagem ASI
# ------------------------------

from lexer import Token, Lexer  # requer lexer.py no mesmo diretório

# ----------------------------------------------------------------------
# Nós da Árvore Sintática Abstrata (AST)
# ----------------------------------------------------------------------
class NoPrograma:
    def __init__(self, declaracoes):
        self.declaracoes = declaracoes

class DeclaracaoVariavel:
    def __init__(self, nome, tipo_dado, valor_inicial, linha, coluna):
        self.nome = nome
        self.tipo_dado = tipo_dado          # normalizado: 'inteiro', 'decimal', ...
        self.valor_inicial = valor_inicial
        self.linha = linha
        self.coluna = coluna

class DeclaracaoVetor:
    def __init__(self, nome, tipo_dado, dimensoes, linha, coluna):
        self.nome = nome
        self.tipo_dado = tipo_dado          # normalizado
        self.dimensoes = dimensoes          # lista de nós de expressão (idealmente literal inteiro)
        self.linha = linha
        self.coluna = coluna

class AtribuicaoVariavel:
    def __init__(self, nome, valor, linha, coluna):
        self.nome = nome
        self.valor = valor
        self.linha = linha
        self.coluna = coluna

class AtribuicaoVetor:
    def __init__(self, nome, indices, valor, linha, coluna):
        self.nome = nome
        self.indices = indices              # lista de nós de expressão
        self.valor = valor
        self.linha = linha
        self.coluna = coluna

class DeclaracaoSe:
    def __init__(self, condicao, corpo_se, corpo_ese, linha, coluna):
        self.condicao = condicao
        self.corpo_se = corpo_se            # lista de nós
        self.corpo_ese = corpo_ese          # lista de nós ou None
        self.linha = linha
        self.coluna = coluna

class DeclaracaoAteQue:
    def __init__(self, condicao, corpo, linha, coluna):
        self.condicao = condicao
        self.corpo = corpo
        self.linha = linha
        self.coluna = coluna

class DeclaracaoAte:
    def __init__(self, inicializacao, condicao, incremento, corpo, linha, coluna):
        self.inicializacao = inicializacao  # declaração, atribuição, expressão, ou None
        self.condicao = condicao            # expressão ou None
        self.incremento = incremento        # atribuição ou expressão ou None
        self.corpo = corpo                  # lista de nós
        self.linha = linha
        self.coluna = coluna

class ChamadaFuncao:
    def __init__(self, nome, argumentos, linha, coluna):
        self.nome = nome
        self.argumentos = argumentos
        self.linha = linha
        self.coluna = coluna

class ChamadaCopiaTexto:
    def __init__(self, destino, origem, linha, coluna):
        self.destino = destino              # NoVariavel ou NoAcessoVetor
        self.origem = origem                # expressão
        self.linha = linha
        self.coluna = coluna

class ExpressaoBinaria:
    def __init__(self, esquerda, operador, direita, linha, coluna):
        self.esquerda = esquerda
        self.operador = operador            # string do operador
        self.direita = direita
        self.linha = linha
        self.coluna = coluna

class NoLiteral:
    def __init__(self, valor, tipo_literal, linha, coluna):
        self.valor = valor
        self.tipo_literal = tipo_literal    # 'INTEIRO', 'DECIMAL', 'CARACTERE', 'BOOLEANO', 'TEXTO'
        self.linha = linha
        self.coluna = coluna

class NoVariavel:
    def __init__(self, nome, linha, coluna):
        self.nome = nome
        self.linha = linha
        self.coluna = coluna

class NoAcessoVetor:
    def __init__(self, nome, indices, linha, coluna):
        self.nome = nome
        self.indices = indices
        self.linha = linha
        self.coluna = coluna

# Conjuntos de tokens de literal e tipo (do lexer)
LITERAIS = {
    'NUMERO_INTEIRO', 'NUMERO_DECIMAL',
    'LITERAL_CARACTERE', 'LITERAL_BOOLEANO', 'LITERAL_TEXTO'
}
TIPOS_DE_DADO = {
    'TIPO_INTEIRO', 'TIPO_DECIMAL', 'TIPO_DUPLO',
    'TIPO_CARACTERE', 'TIPO_BOOLEANO', 'TIPO_TEXTO'
}

# Mapa para normalização de tipos na AST
TIPO_MAP = {
    'TIPO_INTEIRO': 'inteiro',
    'TIPO_DECIMAL': 'decimal',
    'TIPO_DUPLO': 'duplo',
    'TIPO_CARACTERE': 'caractere',
    'TIPO_BOOLEANO': 'booleano',
    'TIPO_TEXTO': 'texto',
}

# ----------------------------------------------------------------------
# Classe Principal do Parser
# ----------------------------------------------------------------------
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicao_atual = 0

    # ---------------- Helpers básicos ----------------
    def token_atual(self):
        return self.tokens[self.posicao_atual] if self.posicao_atual < len(self.tokens) else None

    def olhar(self, k=0):
        i = self.posicao_atual + k
        return self.tokens[i] if i < len(self.tokens) else None

    def ver(self, tipo):
        tok = self.token_atual()
        return (tok is not None) and (tok.tipo == tipo)

    def tentar_consumir(self, tipo):
        if self.ver(tipo):
            return self.consumir(tipo)
        return None

    def erro(self, msg, tok=None):
        tok = tok or self.token_atual()
        linha = tok.linha if tok else '?'
        coluna = tok.coluna if (tok and tok.coluna is not None) else '?'
        raise Exception(f"Erro de sintaxe na linha {linha}, coluna {coluna}: {msg}")

    def consumir(self, tipo_esperado=None):
        token = self.token_atual()
        if token is None:
            raise Exception("Erro de sintaxe: Fim inesperado do arquivo")
        if tipo_esperado and token.tipo != tipo_esperado:
            col = token.coluna if token.coluna is not None else '?'
            raise Exception(
                f"Erro de sintaxe na linha {token.linha}, coluna {col}: "
                f"Esperado {tipo_esperado}, mas encontrado {token.tipo} ('{token.valor}')")
        self.posicao_atual += 1
        return token

    def tipo_normalizado(self, token_tipo):
        if token_tipo not in TIPO_MAP:
            self.erro(f"Tipo de dado desconhecido: {token_tipo}")
        return TIPO_MAP[token_tipo]

    # ---------------- Entrada ----------------
    def parse(self):
        declaracoes = []
        while self.token_atual() is not None:
            declaracoes.append(self.parse_declaracao_ou_instrucao_de_topo())
        return NoPrograma(declaracoes)

    # ---------------- Topo: declarações/instruções ----------------
    def parse_declaracao_ou_instrucao_de_topo(self):
        token = self.token_atual()
        if token is None:
            raise Exception("Erro de sintaxe: Fim inesperado do arquivo após instrução")

        if token.tipo == 'IDENTIFICADOR':
            return self.parse_declaracao_atribuicao_ou_acesso()
        elif token.tipo == 'PALAVRA_CHAVE_SE':
            return self.parse_se_e_se()
        elif token.tipo == 'PALAVRA_CHAVE_WHILE':
            return self.parse_ateQue()
        elif token.tipo == 'PALAVRA_CHAVE_FOR':
            return self.parse_ate()
        elif token.tipo == 'PALAVRA_CHAVE_ESCREVA':
            return self.parse_escreva()
        elif token.tipo == 'PALAVRA_CHAVE_COPIAR_TEXTO':
            return self.parse_copiar_texto()
        else:
            col = token.coluna if token.coluna is not None else '?'
            raise Exception(f"Erro de sintaxe na linha {token.linha}, coluna {col}: "
                            f"Instrução inesperada iniciada com {token.tipo}")

    def parse_declaracao_atribuicao_ou_acesso(self):
        identificador_token = self.token_atual()
        if identificador_token is None:
            raise Exception("Erro de sintaxe: Identificador esperado, mas fim do arquivo encontrado")

        # Lookahead sem consumir
        if self.posicao_atual + 1 < len(self.tokens):
            token_seguinte = self.tokens[self.posicao_atual + 1]

            if token_seguinte.tipo == 'PONTO':
                # Declaração: nome.tipo ...
                return self.parse_declaracao_variavel_ou_vetor()


            elif token_seguinte.tipo == 'COLCHETE_ABRE':

                # Lookahead robusto: consome todos os grupos consecutivos de colchetes

                pos_scan = self.posicao_atual + 1  # aponta para o primeiro '['

                def consumir_um_grupo_de_colchetes(pos):

                    bal = 0

                    iniciou = (pos < len(self.tokens) and self.tokens[pos].tipo == 'COLCHETE_ABRE')

                    if not iniciou:
                        return None  # não começa com '['

                    while pos < len(self.tokens):

                        t = self.tokens[pos]

                        if t.tipo == 'COLCHETE_ABRE':

                            bal += 1

                        elif t.tipo == 'COLCHETE_FECHA':

                            bal -= 1

                        pos += 1

                        if bal == 0:
                            return pos  # retorna posição imediatamente após o ']'

                    return -1  # terminou sem fechar

                # consome [ ... ] [ ... ] [ ... ] ...

                while pos_scan < len(self.tokens) and self.tokens[pos_scan].tipo == 'COLCHETE_ABRE':

                    novo_pos = consumir_um_grupo_de_colchetes(pos_scan)

                    if novo_pos is None:
                        break

                    if novo_pos == -1:
                        linha_erro = self.tokens[pos_scan].linha

                        raise Exception(
                            f"Erro de sintaxe na linha {linha_erro}: Colchetes desbalanceados para '{identificador_token.valor}'")

                    pos_scan = novo_pos  # agora está logo após um ']'

                # neste ponto, pos_scan está após TODOS os colchetes consecutivos

                if pos_scan < len(self.tokens) and self.tokens[pos_scan].tipo == 'OPERADOR_ATRIBUICAO':

                    return self.parse_atribuicao_vetor()

                else:

                    col = identificador_token.coluna if identificador_token.coluna is not None else '?'

                    raise Exception(f"Erro de sintaxe na linha {identificador_token.linha}, coluna {col}: "

                                    f"Acesso a vetor '{identificador_token.valor}[...]' não pode ser uma instrução sozinha.")

            elif token_seguinte.tipo == 'OPERADOR_ATRIBUICAO':
                return self.parse_atribuicao_variavel_simples()

            else:
                col = token_seguinte.coluna if token_seguinte.coluna is not None else '?'
                raise Exception(f"Erro de sintaxe na linha {token_seguinte.linha}, coluna {col}: "
                                f"Esperado '.', '[' ou '=' após identificador '{identificador_token.valor}', mas encontrado {token_seguinte.tipo}")
        else:
            col = identificador_token.coluna if identificador_token.coluna is not None else '?'
            raise Exception(f"Erro de sintaxe na linha {identificador_token.linha}, coluna {col}: "
                            f"Fim inesperado após identificador '{identificador_token.valor}'")

    # ---------------- Declarações e Atribuições ----------------
    def parse_declaracao_variavel_ou_vetor(self):
        nome_token = self.consumir('IDENTIFICADOR')
        self.consumir('PONTO')
        tipo_token = self.consumir_tipo_dado()
        tipo_norm = self.tipo_normalizado(tipo_token.tipo)

        token_depois_tipo = self.token_atual()

        if token_depois_tipo is not None and token_depois_tipo.tipo == 'COLCHETE_ABRE':
            dimensoes = []
            while self.token_atual() is not None and self.token_atual().tipo == 'COLCHETE_ABRE':
                self.consumir('COLCHETE_ABRE')
                tamanho = self.parse_expressao()
                dimensoes.append(tamanho)
                self.consumir('COLCHETE_FECHA')
            self.consumir('PONTO_VIRGULA')
            return DeclaracaoVetor(nome_token.valor, tipo_norm, dimensoes, nome_token.linha, nome_token.coluna)

        elif token_depois_tipo is not None and token_depois_tipo.tipo == 'OPERADOR_ATRIBUICAO':
            self.consumir('OPERADOR_ATRIBUICAO')
            valor = self.parse_expressao()
            self.consumir('PONTO_VIRGULA')
            return DeclaracaoVariavel(nome_token.valor, tipo_norm, valor, nome_token.linha, nome_token.coluna)

        else:
            tok = token_depois_tipo
            col = tok.coluna if tok and tok.coluna is not None else '?'
            tipo_tok = tok.tipo if tok else 'FIM'
            raise Exception(f"Erro de sintaxe na linha {tipo_token.linha}, coluna {col}: "
                            f"Esperado '[' ou '=' após tipo '{tipo_token.valor}', mas encontrado {tipo_tok}")

    def parse_atribuicao_vetor(self):
        nome_token = self.consumir('IDENTIFICADOR')
        indices = []
        while self.token_atual() is not None and self.token_atual().tipo == 'COLCHETE_ABRE':
            self.consumir('COLCHETE_ABRE')
            indice = self.parse_expressao()
            indices.append(indice)
            self.consumir('COLCHETE_FECHA')
        self.consumir('OPERADOR_ATRIBUICAO')
        valor = self.parse_expressao()
        self.consumir('PONTO_VIRGULA')
        return AtribuicaoVetor(nome_token.valor, indices, valor, nome_token.linha, nome_token.coluna)

    def parse_atribuicao_variavel_simples(self):
        nome_token = self.consumir('IDENTIFICADOR')
        self.consumir('OPERADOR_ATRIBUICAO')
        valor = self.parse_expressao()
        self.consumir('PONTO_VIRGULA')
        return AtribuicaoVariavel(nome_token.valor, valor, nome_token.linha, nome_token.coluna)

    # versões “sem ponto e vírgula” (para cabeçalho do 'ate')
    def parse_atribuicao_variavel_simples_sem_pv(self):
        nome_token = self.consumir('IDENTIFICADOR')
        self.consumir('OPERADOR_ATRIBUICAO')
        valor = self.parse_expressao()
        return AtribuicaoVariavel(nome_token.valor, valor, nome_token.linha, nome_token.coluna)

    def parse_declaracao_ou_atribuicao_sem_pv(self):
        identificador = self.consumir('IDENTIFICADOR')
        proximo_token = self.token_atual()
        if proximo_token is None:
            self.erro("Esperado '.' ou '=' após identificador na inicialização do 'ate'", identificador)
        if proximo_token.tipo == 'PONTO':
            self.consumir('PONTO')
            tipo_tok = self.consumir_tipo_dado()
            tipo_norm = self.tipo_normalizado(tipo_tok.tipo)
            self.consumir('OPERADOR_ATRIBUICAO')
            valor = self.parse_expressao()
            return DeclaracaoVariavel(identificador.valor, tipo_norm, valor, identificador.linha, identificador.coluna)
        elif proximo_token.tipo == 'OPERADOR_ATRIBUICAO':
            self.posicao_atual -= 1  # devolve o identificador
            return self.parse_atribuicao_variavel_simples_sem_pv()
        else:
            # Não é declaração nem atribuição -> tratar como expressão
            self.posicao_atual -= 1  # devolve o identificador
            return self.parse_expressao()

    # ---------------- Estruturas de controle ----------------
    def parse_se_e_se(self):
        se_token = self.consumir('PALAVRA_CHAVE_SE')
        self.consumir('PARENTESE_ABRE')
        condicao = self.parse_expressao()
        self.consumir('PARENTESE_FECHA')
        self.consumir('CHAVE_ABRE')
        corpo_se = self.parse_bloco()
        self.consumir('CHAVE_FECHA')

        corpo_ese = None
        if self.token_atual() is not None and self.token_atual().tipo == 'PALAVRA_CHAVE_ELSE':
            self.consumir('PALAVRA_CHAVE_ELSE')
            self.consumir('CHAVE_ABRE')
            corpo_ese = self.parse_bloco()
            self.consumir('CHAVE_FECHA')

        return DeclaracaoSe(condicao, corpo_se, corpo_ese, se_token.linha, se_token.coluna)

    def parse_ateQue(self):
        while_token = self.consumir('PALAVRA_CHAVE_WHILE')
        self.consumir('PARENTESE_ABRE')
        condicao = self.parse_expressao()
        self.consumir('PARENTESE_FECHA')
        self.consumir('CHAVE_ABRE')
        corpo = self.parse_bloco()
        self.consumir('CHAVE_FECHA')
        return DeclaracaoAteQue(condicao, corpo, while_token.linha, while_token.coluna)

    def parse_ate(self):
        """Analisa a estrutura: ate ( inicializacao ; condicao ; incremento ) { corpo }"""
        for_token = self.consumir('PALAVRA_CHAVE_FOR')
        self.consumir('PARENTESE_ABRE')

        # --- Inicialização ---
        inicializacao = None
        tok0 = self.token_atual()
        if tok0 is not None and tok0.tipo != 'PONTO_VIRGULA':
            if tok0.tipo == 'IDENTIFICADOR' and (self.posicao_atual + 1) < len(self.tokens):
                tok_seguinte = self.tokens[self.posicao_atual + 1]
                if tok_seguinte.tipo in ('PONTO', 'OPERADOR_ATRIBUICAO'):
                    inicializacao = self.parse_declaracao_ou_atribuicao_sem_pv()
                else:
                    inicializacao = self.parse_expressao()
            else:
                inicializacao = self.parse_expressao()
        self.consumir('PONTO_VIRGULA')

        # --- Condição ---
        condicao = None
        tok1 = self.token_atual()
        if tok1 is not None and tok1.tipo != 'PONTO_VIRGULA':
            condicao = self.parse_expressao()
        else:
            condicao = NoLiteral(True, 'BOOLEANO', for_token.linha, for_token.coluna)
        self.consumir('PONTO_VIRGULA')

        # --- Incremento ---
        incremento = None
        tok2 = self.token_atual()
        if tok2 is not None and tok2.tipo != 'PARENTESE_FECHA':
            # Tentar atribuição simples sem ';' primeiro
            posicao_guardada = self.posicao_atual
            try:
                incremento = self.parse_atribuicao_variavel_simples_sem_pv()
            except Exception:
                self.posicao_atual = posicao_guardada
                incremento = self.parse_expressao()
        self.consumir('PARENTESE_FECHA')

        # --- Corpo ---
        self.consumir('CHAVE_ABRE')
        corpo = self.parse_bloco()
        self.consumir('CHAVE_FECHA')

        return DeclaracaoAte(inicializacao, condicao, incremento, corpo, for_token.linha, for_token.coluna)

    # ---------------- Funções embutidas ----------------
    def parse_escreva(self):
        escreva_token = self.consumir('PALAVRA_CHAVE_ESCREVA')
        self.consumir('PARENTESE_ABRE')
        argumentos = []
        tok = self.token_atual()
        if tok is not None and tok.tipo != 'PARENTESE_FECHA':
            argumentos.append(self.parse_expressao())
        while self.token_atual() is not None and self.token_atual().tipo == 'VIRGULA':
            self.consumir('VIRGULA')
            argumentos.append(self.parse_expressao())
        self.consumir('PARENTESE_FECHA')
        self.consumir('PONTO_VIRGULA')
        return ChamadaFuncao('escreva', argumentos, escreva_token.linha, escreva_token.coluna)

    def parse_copiar_texto(self):
        copiar_token = self.consumir('PALAVRA_CHAVE_COPIAR_TEXTO')
        self.consumir('PARENTESE_ABRE')
        destino_no = self.parse_primario()
        if not isinstance(destino_no, (NoVariavel, NoAcessoVetor)):
            col = self.token_atual().coluna if self.token_atual() else '?'
            raise Exception(f"Erro de sintaxe na linha {copiar_token.linha}, coluna {col}: "
                            f"Destino inválido para copiar_texto. Deve ser uma variável ou vetor.")
        if self.token_atual() is None or self.token_atual().tipo != 'VIRGULA':
            tok = self.token_atual()
            linha = tok.linha if tok else copiar_token.linha
            col = tok.coluna if (tok and tok.coluna is not None) else '?'
            encontrado = tok.tipo if tok else 'FIM'
            raise Exception(f"Erro de sintaxe na linha {linha}, coluna {col}: "
                            f"Esperado ',' após destino em copiar_texto, mas encontrado {encontrado}")
        self.consumir('VIRGULA')
        origem_no = self.parse_expressao()
        self.consumir('PARENTESE_FECHA')
        self.consumir('PONTO_VIRGULA')
        return ChamadaCopiaTexto(destino_no, origem_no, copiar_token.linha, copiar_token.coluna)

    # ---------------- Blocos e tipos ----------------
    def parse_bloco(self):
        declaracoes = []
        while self.token_atual() is not None and self.token_atual().tipo != 'CHAVE_FECHA':
            declaracoes.append(self.parse_declaracao_ou_instrucao_de_topo())
        return declaracoes

    def consumir_tipo_dado(self):
        token = self.token_atual()
        if token is None or token.tipo not in TIPOS_DE_DADO:
            linha = token.linha if token else '?'
            col = token.coluna if (token and token.coluna is not None) else '?'
            tipo_tok = token.tipo if token else 'FIM'
            raise Exception(f"Erro de sintaxe na linha {linha}, coluna {col}: "
                            f"Esperado um tipo de dado (TIPO_INTEIRO, TIPO_DECIMAL, etc.), mas encontrado {tipo_tok}")
        self.posicao_atual += 1
        return token

    # ----------------------------------------------------------------------
    # Expressões (precedência): comparação > + - > * / > primário
    # ----------------------------------------------------------------------
    def parse_expressao(self):
        return self.parse_comparacao()

    def parse_comparacao(self):
        esquerda = self.parse_termo()
        while self.token_atual() is not None and self.token_atual().tipo == 'OPERADOR_RELACIONAL':
            op_token = self.consumir('OPERADOR_RELACIONAL')
            direita = self.parse_termo()
            esquerda = ExpressaoBinaria(esquerda, op_token.valor, direita, op_token.linha, op_token.coluna)
        return esquerda

    def parse_termo(self):
        esquerda = self.parse_fator()
        while (self.token_atual() is not None and
               self.token_atual().tipo == 'OPERADOR_ARITMETICO' and
               self.token_atual().valor in ['+', '-']):
            op_token = self.consumir('OPERADOR_ARITMETICO')
            direita = self.parse_fator()
            esquerda = ExpressaoBinaria(esquerda, op_token.valor, direita, op_token.linha, op_token.coluna)
        return esquerda

    def parse_fator(self):
        esquerda = self.parse_primario()
        while (self.token_atual() is not None and
               self.token_atual().tipo == 'OPERADOR_ARITMETICO' and
               self.token_atual().valor in ['*', '/']):
            op_token = self.consumir('OPERADOR_ARITMETICO')
            direita = self.parse_primario()
            esquerda = ExpressaoBinaria(esquerda, op_token.valor, direita, op_token.linha, op_token.coluna)
        return esquerda

    def parse_primario(self):
        token = self.token_atual()
        if token is None:
            raise Exception("Erro de sintaxe: Fim inesperado durante análise de expressão primária")

        if token.tipo in LITERAIS:
            token_literal = self.consumir()
            valor = token_literal.valor
            tipo_lit = 'DESCONHECIDO'
            if token_literal.tipo == 'NUMERO_INTEIRO':
                valor = int(valor)
                tipo_lit = 'INTEIRO'
            elif token_literal.tipo == 'NUMERO_DECIMAL':
                valor = float(valor)
                tipo_lit = 'DECIMAL'
            elif token_literal.tipo == 'LITERAL_BOOLEANO':
                valor = (valor == 'verdadeiro')
                tipo_lit = 'BOOLEANO'
            elif token_literal.tipo == 'LITERAL_CARACTERE':
                tipo_lit = 'CARACTERE'
            elif token_literal.tipo == 'LITERAL_TEXTO':
                tipo_lit = 'TEXTO'
            return NoLiteral(valor, tipo_lit, token_literal.linha, token_literal.coluna)

        elif token.tipo == 'IDENTIFICADOR':
            nome_token = self.consumir('IDENTIFICADOR')
            if self.token_atual() is not None and self.token_atual().tipo == 'COLCHETE_ABRE':
                indices = []
                while self.token_atual() is not None and self.token_atual().tipo == 'COLCHETE_ABRE':
                    self.consumir('COLCHETE_ABRE')
                    indice = self.parse_expressao()
                    indices.append(indice)
                    self.consumir('COLCHETE_FECHA')
                return NoAcessoVetor(nome_token.valor, indices, nome_token.linha, nome_token.coluna)
            else:
                return NoVariavel(nome_token.valor, nome_token.linha, nome_token.coluna)

        elif token.tipo == 'PARENTESE_ABRE':
            self.consumir('PARENTESE_ABRE')
            expressao = self.parse_expressao()
            self.consumir('PARENTESE_FECHA')
            return expressao

        else:
            col = token.coluna if token.coluna is not None else '?'
            raise Exception(f"Erro de sintaxe na linha {token.linha}, coluna {col}: "
                            f"Token inesperado '{token.valor}' ({token.tipo}) em expressão primária")

# ----------------------------------------------------------------------
# Bloco de Teste (opcional)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    try:
        with open('teste.asi', 'r', encoding='utf-8') as f:
            codigo_real = f.read()
        print("--- Testando parser com teste.asi ---")
        lexer_real = Lexer(codigo_real)
        tokens_real = lexer_real.criar_tokens()
        parser_real = Parser(tokens_real)
        ast_real = parser_real.parse()
        print("Análise Sintática concluída com sucesso para teste.asi!")
    except FileNotFoundError:
        print("Arquivo teste.asi não encontrado.")
    except Exception as e:
        print("\n--- ERRO NA ANÁLISE SINTÁTICA ---")
        print(f"Detalhe: {e}")

