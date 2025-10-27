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
# lexer.py
# ------------------------------
# Lexer (tokenizador) da linguagem ASI
# ------------------------------

import re

class Token:
    def __init__(self, tipo, valor, linha=None, coluna=None):
        self.tipo = tipo
        self.valor = valor
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"Token({self.tipo!r}, {self.valor!r}, L{self.linha} C{self.coluna})"

class Lexer:
    def __init__(self, codigo_fonte):
        self.codigo_fonte = codigo_fonte
        self.tokens = []
        self.linha_atual = 1
        self.coluna_atual = 1

    def criar_tokens(self):
        # Ordem importa: padrões mais específicos/longos primeiro
        token_especificacoes = [
            # --- Ignorados ---
            ('NOVA_LINHA', r'\r\n|\n|\r'),      # suporta CRLF e LF
            ('ESPACO_OU_TAB', r'[ \t]+'),
            ('COMENTARIO', r'//.*'),

            # --- Palavras-chave ---
            ('PALAVRA_CHAVE_SE', r'se\b'),
            # aceita 'eSe' (compatível com seu teste), e também 'senao' e 'else'
            ('PALAVRA_CHAVE_ELSE', r'(?:eSe|senao|else)\b'),
            ('PALAVRA_CHAVE_FOR', r'ate\b'),
            ('PALAVRA_CHAVE_WHILE', r'ateQue\b'),
            ('PALAVRA_CHAVE_ESCREVA', r'escreva\b'),
            ('PALAVRA_CHAVE_COPIAR_TEXTO', r'copiar_texto\b'),
            ('LITERAL_BOOLEANO', r'verdadeiro\b|falso\b'),

            # --- Tipos ---
            ('TIPO_INTEIRO', r'inteiro\b'),
            ('TIPO_DECIMAL', r'decimal\b'),
            ('TIPO_DUPLO', r'duplo\b'),
            ('TIPO_CARACTERE', r'caractere\b'),
            ('TIPO_BOOLEANO', r'booleano\b'),
            ('TIPO_TEXTO', r'texto\b'),

            # --- Operadores e Delimitadores ---
            ('OPERADOR_RELACIONAL', r'<=|>=|==|!=|>|<'),
            ('OPERADOR_ARITMETICO', r'\+|-|\*|/'),
            ('OPERADOR_ATRIBUICAO', r'='),
            ('PONTO_VIRGULA', r';'),
            ('PONTO', r'\.'),
            ('VIRGULA', r','),
            ('PARENTESE_ABRE', r'\('),
            ('PARENTESE_FECHA', r'\)'),
            ('CHAVE_ABRE', r'\{'),
            ('CHAVE_FECHA', r'\}'),
            ('COLCHETE_ABRE', r'\['),
            ('COLCHETE_FECHA', r'\]'),

            # --- Literais ---
            ('NUMERO_DECIMAL', r'\d+\.\d+'),
            ('NUMERO_INTEIRO', r'\d+'),
            ('LITERAL_CARACTERE', r"'([^'\\]|\\.)'"),
            ('LITERAL_TEXTO', r'"([^"\\]|\\.)*"'),

            # --- Identificadores ---
            ('IDENTIFICADOR', r'[a-zA-Z_][a-zA-Z0-9_]*'),

            # --- Erro ---
            ('ERRO', r'.'),
        ]

        # Compila regex de todos os tokens (grupos nomeados)
        regex_tokens = '|'.join(f'(?P<{nome}>{padrao})' for (nome, padrao) in token_especificacoes)
        padrao_compilado = re.compile(regex_tokens)

        self.linha_atual = 1
        posicao_linha = 0  # índice do início da linha atual no texto total

        for match in padrao_compilado.finditer(self.codigo_fonte):
            tipo = match.lastgroup
            valor = match.group(tipo)
            coluna = match.start() - posicao_linha + 1

            if tipo == 'NOVA_LINHA':
                self.linha_atual += 1
                posicao_linha = match.end()
                continue
            elif tipo in ('ESPACO_OU_TAB', 'COMENTARIO'):
                continue
            elif tipo == 'LITERAL_CARACTERE':
                valor = valor[1:-1].encode().decode('unicode_escape')
            elif tipo == 'LITERAL_TEXTO':
                valor = valor[1:-1].encode().decode('unicode_escape')
            elif tipo == 'ERRO':
                raise Exception(f"Erro Léxico: Caractere inesperado '{valor}' "
                                f"na linha {self.linha_atual}, coluna {coluna}")

            self.tokens.append(Token(tipo, valor, self.linha_atual, coluna))

        return self.tokens

# Bloco de Teste (opcional)
if __name__ == "__main__":
    codigo_teste = r"""
// Exemplo ASI
velocidade.decimal = 99.5;
nome.texto = "Teste\nCom\tEscapes";
letra.caractere = 'B';
ativo.booleano = falso;

se (velocidade > 100.0) {
    ativo = verdadeiro;
} eSe {
    ativo = falso;
}
"""
    try:
        lexer = Lexer(codigo_teste)
        tokens_gerados = lexer.criar_tokens()
        print("--- Tokens Gerados (Teste Interno) ---")
        for token in tokens_gerados:
            print(token)
    except Exception as e:
        print(f"--- ERRO NO LEXER (Teste Interno) ---")
        print(e)
