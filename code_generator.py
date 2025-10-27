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
#code_generator.py

try:
    import parser as p
except ImportError:
    print("Erro crítico: Não foi possível encontrar 'parser.py'.")
    exit(1)

class CodeGenerator:
    def __init__(self, ast_raiz):
        self.ast_raiz = ast_raiz
        self.codigo_c = ""
        self.indentacao = 0

    def gerar_codigo(self):
        """Método principal para iniciar a geração de código."""
        self.escrever_linha('#include <stdio.h>')
        self.escrever_linha('#include <string.h>')  # Para operações de string
        self.escrever_linha('#include <stdbool.h>')  # Para 'true' e 'false' em C
        self.escrever_linha('\nint main() {')

        self.indentacao += 1

        # Visita cada nó na raiz da AST (o corpo principal do programa)
        for no in self.ast_raiz:
            self.visitar(no)

        self.escrever_linha('return 0;')
        self.indentacao -= 1
        self.escrever_linha('}')

        return self.codigo_c

    def escrever(self, texto):
        """Escreve texto sem nova linha, mas com indentação."""
        self.codigo_c += ("    " * self.indentacao) + texto

    def escrever_linha(self, linha):
        """Escreve uma linha de código completa com indentação e nova linha."""
        self.escrever(linha + '\n')

    def visitar(self, no):
        """Método "visitador" principal (dispatcher) que roteia para o método correto."""

        # Alterado de type(no).__name__ para isinstance para funcionar com classes importadas
        # Usando isinstance para despacho (mais robusto)
        if isinstance(no, p.DeclaracaoVariavel):
            return self.visitar_DeclaracaoVariavel(no)
        elif isinstance(no, p.DeclaracaoVetor):
            return self.visitar_DeclaracaoVetor(no)
        elif isinstance(no, p.Atribuicao):
            return self.visitar_Atribuicao(no)
        elif isinstance(no, p.NoVariavel):
            return self.visitar_NoVariavel(no)
        elif isinstance(no, p.NoAcessoVetor):
            return self.visitar_NoAcessoVetor(no)
        elif isinstance(no, p.NoLiteral):
            return self.visitar_NoLiteral(no)
        # --- NOVA ADIÇÃO (Etapa 5) ---
        elif isinstance(no, p.ExpressaoBinaria):
            return self.visitar_ExpressaoBinaria(no)
            # Fallback (método antigo)
        elif isinstance(no, p.ChamadaCopiaTexto):
            return self.visitar_ChamadaCopiaTexto(no)

        nome_metodo = f'visitar_{type(no).__name__}'
        metodo = getattr(self, nome_metodo, self.metodo_nao_encontrado)
        return metodo(no)

    def metodo_nao_encontrado(self, no):
        """Chamado se um nó da AST não tem um método visitador."""
        raise Exception(f"Erro do Gerador: Nenhum método visitador encontrado para {type(no).__name__}")

    # --- Mapeamento de Tipos ---

    def mapear_tipo_c(self, tipo_asi):
        """Converte tipos da ASI para tipos C."""
        if tipo_asi == 'TIPO_INTEIRO':
            return 'int'
        elif tipo_asi == 'TIPO_DECIMAL':
            return 'float'
        elif tipo_asi == 'TIPO_DUPLO':
            return 'double'
        elif tipo_asi == 'TIPO_CARACTERE':
            return 'char'
        elif tipo_asi == 'TIPO_BOOLEANO':
            return 'booleano'  # C usa int (0 ou 1) para bool
        elif tipo_asi == 'TIPO_TEXTO':
            return 'const char*'  # String em C é um ponteiro para char
        else:
            raise Exception(f"Tipo ASI desconhecido: {tipo_asi}")

    # --- Visitadores da AST ---

    def visitar_DeclaracaoVariavel(self, no):
        """Visita nó de declaração de variável: nome.tipo = valor;"""
        tipo_c = self.mapear_tipo_c(no.tipo_dado)
        valor_c = self.visitar(no.valor_inicial)
        self.escrever_linha(f'{tipo_c} {no.nome} = {valor_c};')

    def visitar_DeclaracaoVetor(self, no):
        """Visita nó de declaração de vetor/matriz: nome.tipo[tam1][tam2];"""
        tipo_c = self.mapear_tipo_c(no.tipo_dado)

        # Constrói as dimensões (ex: [10], [5][5])
        dimensoes_c = ""
        for dimensao_no in no.dimensoes:
            # Espera-se que a dimensão seja um NoLiteral(int)
            if isinstance(dimensao_no, p.NoLiteral) and dimensao_no.tipo_literal == 'INTEIRO':
                dimensoes_c += f'[{dimensao_no.valor}]'
            else:
                raise Exception("Declaração de vetor deve usar literais inteiros para tamanho.")

        self.escrever_linha(f'{tipo_c} {no.nome}{dimensoes_c};')

    def visitar_Atribuicao(self, no):
        """Visita nó de atribuição: var = valor; ou var[idx] = valor;"""
        variavel_c = self.visitar(no.variavel)
        valor_c = self.visitar(no.valor)
        # Lógica especial para strings (char*)
        # Em C, não podemos atribuir strings com '=', usamos strcpy
        # Mas o parser não sabe o tipo, só o code_generator
        # Por enquanto, deixaremos a atribuição direta, o que só funciona
        # para ponteiros (nome.texto = "outro"), não para buffers.
        # A função copiar_texto é a forma "correta" na ASI.
        self.escrever_linha(f'{variavel_c} = {valor_c};')

    def visitar_NoVariavel(self, no):
        """Visita um nó de uso de variável. Retorna o nome."""
        return no.nome

    def visitar_NoAcessoVetor(self, no):
        """Visita um acesso a vetor/matriz. Retorna nome[idx1][idx2]."""
        indices_c = ""
        for indice_no in no.indices:
            indice_str = self.visitar(indice_no)
            indices_c += f'[{indice_str}]'
        return f'{no.nome}{indices_c}'

    def visitar_NoLiteral(self, no):
        """Visita um literal e o formata corretamente para C."""
        if no.tipo_literal == 'BOOLEANO':
            # Usa 'true' e 'false' do stdbool.h
            return 'true' if no.valor else 'false'
        elif no.tipo_literal == 'CARACTERE':
            return f"'{no.valor}'"  # Adiciona aspas simples
        elif no.tipo_literal == 'TEXTO':
            return f'"{no.valor}"'  # Adiciona aspas duplas
        elif no.tipo_literal in ['DECIMAL', 'INTEIRO']:
            return str(no.valor)  # Números são diretos
        else:
            raise Exception(f"Literal de tipo desconhecido: {no.tipo_literal}")

    def visitar_ExpressaoBinaria(self, no):
        """Visita um nó de expressão binária: esquerda OPERADOR direita."""

        # Visita recursivamente os lados esquerdo e direito
        lado_esquerdo = self.visitar(no.esquerda)
        lado_direito = self.visitar(no.direita)

        # Retorna a string da operação C (ex: "5 + 1" ou "var1 * var2")
        # Adicionamos parênteses para garantir a precedência correta em C
        return f'({lado_esquerdo} {no.operador} {lado_direito})'

    def visitar_ChamadaCopiaTexto(self, no):
        """Visita nó de cópia de texto: copiar_texto(destino, origem);"""

        # Visita os nós filhos para obter as strings C
        destino_c = self.visitar(no.destino)
        origem_c = self.visitar(no.origem)

        # Gera o código C usando strcpy (a função insegura)
        self.escrever_linha(f'strcpy({destino_c}, {origem_c});')

