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
# main.py

try:
    from lexer import Lexer, Token
except ImportError:
    print("Erro: Arquivo 'lexer.py' não encontrado.")
    exit(1)

try:
    from parser import Parser
except ImportError:
    print("Erro: Arquivo 'parser.py' não encontrado.")
    exit(1)

try:
    from code_generator import CodeGenerator
except ImportError:
    print("Erro: Arquivo 'code_generator.py' não encontrado.")
    exit(1)


def compilar(nome_arquivo_fonte):
    """Função principal que executa todas as etapas do compilador."""

    nome_arquivo_saida = nome_arquivo_fonte.replace('.asi', '.c')

    print(f"--- Iniciando compilação de '{nome_arquivo_fonte}' ---")

    try:
        # Lê o código fonte
        with open(nome_arquivo_fonte, 'r', encoding='utf-8') as f:
            codigo_fonte = f.read()

        # 1. Análise Léxica
        print("Etapa 1: Análise Léxica...")
        lexer = Lexer(codigo_fonte)
        tokens = lexer.criar_tokens()

        # Descomente para debug
        # print("--- Tokens Gerados ---")
        # for t in tokens: print(t)

        # 2. Análise Sintática
        print("Etapa 2: Análise Sintática...")
        parser = Parser(tokens)
        ast = parser.parse()

        # Descomente para debug
        # print("\n--- AST Gerada ---")
        # for no in ast: print(no)

        # 3. Geração de Código
        print("Etapa 3: Geração de Código...")
        gerador = CodeGenerator(ast)
        codigo_c = gerador.gerar_codigo()

        # 4. Salvar arquivo C
        with open(nome_arquivo_saida, 'w', encoding='utf-8') as f:
            f.write(codigo_c)

        print(f"\n--- Compilação concluída com sucesso! ---")
        print(f"Código C gerado em: '{nome_arquivo_saida}'")

        # Exibe o código C gerado
        print("\n--- Código C Gerado ---")
        print(codigo_c)

    except FileNotFoundError:
        print(f"ERRO: O arquivo '{nome_arquivo_fonte}' não foi encontrado.")
    except Exception as e:
        print(f"\n--- ERRO DURANTE A COMPILAÇÃO ---")
        print(f"Detalhe: {e}")
        # (Em um compilador real, imprimiríamos a pilha de erro)
        # import traceback
        # traceback.print_exc()


# --- Execução ---
if __name__ == "__main__":
    # Certifique-se de ter um arquivo 'teste.asi' no mesmo diretório
    compilar('teste.asi')
