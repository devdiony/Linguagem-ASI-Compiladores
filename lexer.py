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
"""
Disciplina: Compiladores (Versão 2)
Projeto: Linguagem ASI
Lexer Final Corrigido
"""
import re

# --- Constantes de Tokens (Exportadas para o Parser) ---
TIPOS_DE_DADOS = [
    'TIPO_INTEIRO', 'TIPO_DECIMAL', 'TIPO_DUPLO',
    'TIPO_CARACTERE', 'TIPO_BOOLEANO', 'TIPO_TEXTO'
]

LITERAIS = [
    'LITERAL_BOOLEANO', 'LITERAL_CARACTERE', 'LITERAL_TEXTO',
    'NUMERO_DECIMAL', 'NUMERO_INTEIRO'
]

class Token:
    """Representa um token léxico."""
    def __init__(self, tipo, valor, linha=None, coluna=None): # Adicionado linha/coluna para depuração
        self.tipo = tipo
        self.valor = valor
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        # return f"Token({self.tipo!r}, {self.valor!r})"
        # Representação mais detalhada para depuração
         return f"Token({self.tipo}, '{self.valor}', Linha: {self.linha}, Col: {self.coluna})"

class Lexer:
    """Analisador Léxico para a linguagem ASI."""
    def __init__(self, codigo_fonte):
        self.codigo_fonte = codigo_fonte
        self.tokens = []
        self.linha_atual = 1
        self.coluna_atual = 1

        # --- Expressões Regulares dos Tokens ---
        # A ordem é importante para evitar ambiguidades
        self.token_specs = [
            # 1. Tokens a ignorar (Espaços, Tabs, Novas Linhas, Comentários)
            #    IMPORTANTE: A nova linha (\n) é tratada separadamente para contar linhas
            ('NOVA_LINHA',      r'\n'),
            ('ESPACO_OU_TAB',   r'[ \t\r\f]+'), # Ignora espaços e tabs
            ('COMENTARIO',      r'//.*'),       # Ignora comentários de linha

            # 2. Palavras-chave
            ('PALAVRA_CHAVE_SE',  r'se'),
            ('PALAVRA_CHAVE_ELSE',r'eSe'),
            ('PALAVRA_CHAVE_FOR', r'ate'),
            ('PALAVRA_CHAVE_WHILE',r'ateQue'),
            ('PALAVRA_CHAVE_ESCREVA',r'escreva'),
            ('PALAVRA_CHAVE_COPIAR_TEXTO', r'copiar_texto'),

            # 3. Tipos de Dados
            ('TIPO_INTEIRO',      r'inteiro'),
            ('TIPO_DECIMAL',      r'decimal'), # Nota: float não existe mais
            ('TIPO_DUPLO',        r'duplo'),   # Nota: double não existe mais
            ('TIPO_CARACTERE',    r'caractere'),
            ('TIPO_BOOLEANO',     r'booleano'),
            ('TIPO_TEXTO',        r'texto'),

            # 4. Literais
            ('LITERAL_BOOLEANO',  r'verdadeiro|falso'),
            ('LITERAL_CARACTERE', r"'(?:\\.|[^'\\])'"),
            ('LITERAL_TEXTO',     r'"(?:\\.|[^"\\])*"'),
            ('NUMERO_DECIMAL',    r'\d+\.\d+'), # Float/Double são tratados como decimal no lexer
            ('NUMERO_INTEIRO',    r'\d+'),

            # 5. Operadores e Delimitadores (Ordem: mais longos primeiro)
            ('OP_RELACIONAL',     r'<=|>=|==|!=|>|<'),
            ('OP_ARITMETICO',     r'\+|-|\*|/'),
            ('OP_ATRIBUICAO',     r'='),
            ('PONTO_VIRGULA',     r';'),
            ('PONTO',             r'\.'),
            ('VIRGULA',           r','),
            ('PARENTESE_ABRE',    r'\('),
            ('PARENTESE_FECHA',   r'\)'),
            ('COLCHETE_ABRE',     r'\['),
            ('COLCHETE_FECHA',    r'\]'),
            ('CHAVE_ABRE',        r'\{'),
            ('CHAVE_FECHA',       r'\}'),

            # 6. Identificador (sempre por último antes do erro)
            ('IDENTIFICADOR',     r'[a-zA-Z_][a-zA-Z0-9_]*'),

            # 7. Erro (qualquer outro caractere)
            ('ERRO',              r'.'),
        ]

        # Compila a regex
        self.regex_compilada = re.compile(
            '|'.join(f'(?P<{nome}>{padrao})' for nome, padrao in self.token_specs)
        )
        self.pos_atual_codigo = 0 # Posição no texto fonte

    def criar_tokens(self):
        """Gera a lista de tokens a partir do código fonte."""
        while self.pos_atual_codigo < len(self.codigo_fonte):
            match = self.regex_compilada.match(self.codigo_fonte, self.pos_atual_codigo)

            if not match:
                # Se não houver match, algo está muito errado (ERRO deveria pegar)
                raise RuntimeError(f"Erro léxico: caractere inesperado na linha {self.linha_atual}, coluna {self.coluna_atual}")

            tipo = match.lastgroup
            valor = match.group()
            inicio, fim = match.span()
            coluna_inicio_token = self.coluna_atual

            # --- LÓGICA CRÍTICA DE IGNORAR E CONTAR LINHAS ---
            if tipo == 'NOVA_LINHA':
                self.linha_atual += 1
                self.coluna_atual = 1
                self.pos_atual_codigo = fim
                continue # Pula para o próximo match, não adiciona token
            elif tipo in ['ESPACO_OU_TAB', 'COMENTARIO']:
                self.coluna_atual += (fim - inicio)
                self.pos_atual_codigo = fim
                continue # Pula para o próximo match, não adiciona token
            elif tipo == 'ERRO':
                 raise RuntimeError(f"Erro léxico: Caractere inesperado '{valor}' na linha {self.linha_atual}, coluna {self.coluna_atual}")
            # --- FIM DA LÓGICA CRÍTICA ---

            # Limpa o valor dos literais
            if tipo == 'LITERAL_TEXTO':
                valor = valor[1:-1].encode().decode('unicode_escape') # Processa escapes como \n
            elif tipo == 'LITERAL_CARACTERE':
                 valor = valor[1:-1].encode().decode('unicode_escape')

            # Cria e adiciona o token válido
            token = Token(tipo, valor, self.linha_atual, coluna_inicio_token)
            self.tokens.append(token)

            # Atualiza a posição e coluna
            self.coluna_atual += (fim - inicio)
            self.pos_atual_codigo = fim

        self.tokens.append(Token('FIM_DE_ARQUIVO', None, self.linha_atual, self.coluna_atual))
        return self.tokens

# --- Bloco de Teste ---
if __name__ == "__main__":
    codigo_teste = """
// Arquivo de teste v2 - Etapa 6
// Testa a cópia de strings (e o buffer overflow!)

// Um buffer (array) para armazenar texto
buffer_pequeno.caractere[10];

// Uma string literal (const char*)
origem.texto = "Ola\\nMundo"; // Teste com escape \\n

// 1. Cópia segura
copiar_texto(buffer_pequeno, origem); // OK

// 3. O PROBLEMA DO BUFFER OVERFLOW
copiar_texto(buffer_pequeno, "1234567890"); // Estouro!

outro.inteiro = 5 + /* Comentário de Bloco (Não Suportado!) */ 10; // Deve dar erro léxico

"""
    print("--- Testando Lexer Final ---")
    try:
        lexer = Lexer(codigo_teste)
        tokens_gerados = lexer.criar_tokens()
        print("\n--- Tokens Gerados ---")
        for token in tokens_gerados:
            print(token)
    except RuntimeError as e:
        print(f"\n--- Erro Léxico Detectado (Esperado) ---")
        print(e)

    codigo_teste_parser = """
// Arquivo de teste v2 - Etapa 6
buffer_pequeno.caractere[10];
origem.texto = "Ola";
copiar_texto(buffer_pequeno, origem);
copiar_texto(buffer_pequeno, "1234567890");
"""
    print("\n--- Testando Lexer para Parser ---")
    try:
        lexer = Lexer(codigo_teste_parser)
        tokens_gerados = lexer.criar_tokens()
        print("Tokens gerados com sucesso para o parser.")
        # Opcional: imprimir tokens para verificar
        # for token in tokens_gerados:
        #     print(token)
    except RuntimeError as e:
        print(f"Erro inesperado no lexer para parser: {e}")

