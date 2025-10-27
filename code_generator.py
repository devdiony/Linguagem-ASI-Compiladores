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
        self.tamanho_texto_padrao = 256  # buffer padrão p/ 'texto'

    # ---------- infra ----------
    def escrever(self, texto):
        self.codigo_c += ("    " * self.indentacao) + texto

    def escrever_linha(self, linha=""):
        self.escrever(linha + "\n")

    # ---------- driver ----------
    def gerar_codigo(self):
        self.escrever_linha('#include <stdio.h>')
        self.escrever_linha('#include <string.h>')
        self.escrever_linha('#include <stdbool.h>')
        self.escrever_linha()
        self.escrever_linha('int main(void) {')
        self.indentacao += 1

        nos = self.ast_raiz.declaracoes if isinstance(self.ast_raiz, p.NoPrograma) else self.ast_raiz
        for no in nos:
            self.visitar(no)

        self.escrever_linha('return 0;')
        self.indentacao -= 1
        self.escrever_linha('}')
        return self.codigo_c

    # ---------- dispatcher ----------
    def visitar(self, no):
        if isinstance(no, p.DeclaracaoVariavel):   return self.visitar_DeclaracaoVariavel(no)
        if isinstance(no, p.DeclaracaoVetor):      return self.visitar_DeclaracaoVetor(no)
        if isinstance(no, p.AtribuicaoVariavel):   return self.visitar_AtribuicaoVariavel(no)
        if isinstance(no, p.AtribuicaoVetor):      return self.visitar_AtribuicaoVetor(no)
        if isinstance(no, p.DeclaracaoSe):         return self.visitar_DeclaracaoSe(no)
        if isinstance(no, p.DeclaracaoAteQue):     return self.visitar_DeclaracaoAteQue(no)
        if isinstance(no, p.DeclaracaoAte):        return self.visitar_DeclaracaoAte(no)
        if isinstance(no, p.ChamadaFuncao):        return self.visitar_ChamadaFuncao(no)
        if isinstance(no, p.ChamadaCopiaTexto):    return self.visitar_ChamadaCopiaTexto(no)
        if isinstance(no, p.ExpressaoBinaria):     return self.visitar_ExpressaoBinaria(no)
        if isinstance(no, p.NoVariavel):           return self.visitar_NoVariavel(no)
        if isinstance(no, p.NoAcessoVetor):        return self.visitar_NoAcessoVetor(no)
        if isinstance(no, p.NoLiteral):            return self.visitar_NoLiteral(no)
        raise Exception(f"Erro do Gerador: Nenhum método visitador encontrado para {type(no).__name__}")

    # ---------- tipos ----------
    def mapear_tipo_c(self, tipo_asi):
        mapa = {
            # tokens do lexer
            'TIPO_INTEIRO': 'int',
            'TIPO_DECIMAL': 'float',
            'TIPO_DUPLO': 'double',
            'TIPO_CARACTERE': 'char',
            'TIPO_BOOLEANO': 'bool',
            'TIPO_TEXTO': 'texto',  # tratado à parte

            # nomes normalizados
            'inteiro': 'int',
            'decimal': 'float',
            'duplo': 'double',
            'caractere': 'char',
            'booleano': 'bool',
            'texto': 'texto',       # tratado à parte
        }
        if tipo_asi not in mapa:
            raise Exception(f"Tipo ASI desconhecido: {tipo_asi}")
        return mapa[tipo_asi]

    # ---------- declarações ----------
    def visitar_DeclaracaoVariavel(self, no: 'p.DeclaracaoVariavel'):
        tipo_c = self.mapear_tipo_c(no.tipo_dado)

        if tipo_c == 'texto':
            nome = no.nome
            if isinstance(no.valor_inicial, p.NoLiteral) and no.valor_inicial.tipo_literal == 'TEXTO':
                self.escrever_linha(f'char {nome}[{self.tamanho_texto_padrao}] = {self.visitar(no.valor_inicial)};')
            elif no.valor_inicial is not None:
                self.escrever_linha(f'char {nome}[{self.tamanho_texto_padrao}] = {{0}};')
                self.escrever_linha(f'strcpy({nome}, {self.visitar(no.valor_inicial)});')
            else:
                self.escrever_linha(f'char {nome}[{self.tamanho_texto_padrao}] = {{0}};')
            return

        valor_c = self.visitar(no.valor_inicial) if no.valor_inicial is not None else None
        if valor_c is not None:
            self.escrever_linha(f'{tipo_c} {no.nome} = {valor_c};')
        else:
            self.escrever_linha(f'{tipo_c} {no.nome};')

    def visitar_DeclaracaoVetor(self, no: 'p.DeclaracaoVetor'):
        tipo_c = self.mapear_tipo_c(no.tipo_dado)
        if tipo_c == 'texto':
            raise Exception("Vetor de texto não suportado no gerador atual.")
        dims = []
        for dim in no.dimensoes:
            if isinstance(dim, p.NoLiteral) and dim.tipo_literal == 'INTEIRO':
                dims.append(str(dim.valor))
            else:
                raise Exception("Declaração de vetor exige tamanhos literais inteiros.")
        self.escrever_linha(f'{tipo_c} {no.nome}' + ''.join(f'[{d}]' for d in dims) + ';')

    # ---------- atribuições ----------
    def visitar_AtribuicaoVariavel(self, no: 'p.AtribuicaoVariavel'):
        self.escrever_linha(f'{no.nome} = {self.visitar(no.valor)};')

    def visitar_AtribuicaoVetor(self, no: 'p.AtribuicaoVetor'):
        indices = ''.join(f'[{self.visitar(idx)}]' for idx in no.indices)
        self.escrever_linha(f'{no.nome}{indices} = {self.visitar(no.valor)};')

    # ---------- controle ----------
    def visitar_DeclaracaoSe(self, no: 'p.DeclaracaoSe'):
        self.escrever_linha(f'if ({self.visitar(no.condicao)}) {{')
        self.indentacao += 1
        for instr in no.corpo_se:
            self.visitar(instr)
        self.indentacao -= 1
        self.escrever_linha('}')
        if no.corpo_ese is not None:
            self.escrever_linha('else {')
            self.indentacao += 1
            for instr in no.corpo_ese:
                self.visitar(instr)
            self.indentacao -= 1
            self.escrever_linha('}')

    def visitar_DeclaracaoAteQue(self, no: 'p.DeclaracaoAteQue'):
        self.escrever_linha(f'while ({self.visitar(no.condicao)}) {{')
        self.indentacao += 1
        for instr in no.corpo:
            self.visitar(instr)
        self.indentacao -= 1
        self.escrever_linha('}')

    # helpers para render inline sem imprimir linha
    def _render_expr(self, no):
        if no is None: return ''
        if isinstance(no, p.NoLiteral):        return self.visitar_NoLiteral(no)
        if isinstance(no, p.NoVariavel):       return self.visitar_NoVariavel(no)
        if isinstance(no, p.NoAcessoVetor):    return self.visitar_NoAcessoVetor(no)
        if isinstance(no, p.ExpressaoBinaria): return self.visitar_ExpressaoBinaria(no)
        if isinstance(no, p.AtribuicaoVariavel):
            return f'{no.nome} = {self._render_expr(no.valor)}'
        if isinstance(no, p.AtribuicaoVetor):
            idxs = ''.join(f'[{self._render_expr(i)}]' for i in no.indices)
            return f'{no.nome}{idxs} = {self._render_expr(no.valor)}'
        return None

    def visitar_DeclaracaoAte(self, no: 'p.DeclaracaoAte'):
        # init
        if no.inicializacao is not None and isinstance(no.inicializacao, p.DeclaracaoVariavel):
            self.visitar(no.inicializacao)  # fora do cabeçalho
            init_str = ''
        else:
            init_str = self._render_expr(no.inicializacao) or ''

        cond_str = self._render_expr(no.condicao) or ''
        inc_str  = self._render_expr(no.incremento) or ''

        self.escrever_linha(f'for ({init_str}; {cond_str}; {inc_str}) {{')
        self.indentacao += 1
        for instr in no.corpo:
            self.visitar(instr)
        self.indentacao -= 1
        self.escrever_linha('}')

    # ---------- funções embutidas ----------
    def visitar_ChamadaFuncao(self, no: 'p.ChamadaFuncao'):
        if no.nome != 'escreva':
            raise Exception(f"Função desconhecida: {no.nome}")
        for arg in no.argumentos:
            if isinstance(arg, p.NoLiteral) and arg.tipo_literal == 'BOOLEANO':
                expr = self._render_expr(arg)
                self.escrever_linha(f'printf("%s", ({expr}) ? "true" : "false");')
            elif isinstance(arg, p.NoLiteral) and arg.tipo_literal == 'TEXTO':
                self.escrever_linha(f'printf("%s", {self.visitar(arg)});')
            elif isinstance(arg, p.NoLiteral) and arg.tipo_literal == 'CARACTERE':
                self.escrever_linha(f'printf("%c", {self.visitar(arg)});')
            elif isinstance(arg, p.NoLiteral) and arg.tipo_literal == 'INTEIRO':
                self.escrever_linha(f'printf("%d", {self.visitar(arg)});')
            elif isinstance(arg, p.NoLiteral) and arg.tipo_literal == 'DECIMAL':
                self.escrever_linha(f'printf("%f", {self.visitar(arg)});')
            else:
                # Sem tipos estáticos, assumimos inteiro
                self.escrever_linha(f'printf("%d", {self._render_expr(arg)});')

    def visitar_ChamadaCopiaTexto(self, no: 'p.ChamadaCopiaTexto'):
        self.escrever_linha(f'strcpy({self._render_expr(no.destino)}, {self._render_expr(no.origem)});')

    # ---------- expressões ----------
    def visitar_NoVariavel(self, no: 'p.NoVariavel'):
        return no.nome

    def visitar_NoAcessoVetor(self, no: 'p.NoAcessoVetor'):
        return f"{no.nome}" + "".join(f'[{self.visitar(i)}]' for i in no.indices)

    def visitar_NoLiteral(self, no: 'p.NoLiteral'):
        if no.tipo_literal == 'BOOLEANO':
            return 'true' if no.valor else 'false'
        if no.tipo_literal == 'CARACTERE':
            return f"'{no.valor}'"
        if no.tipo_literal == 'TEXTO':
            return f"\"{no.valor}\""
        if no.tipo_literal in ('DECIMAL', 'INTEIRO'):
            return str(no.valor)
        raise Exception(f"Literal de tipo desconhecido: {no.tipo_literal}")

    def visitar_ExpressaoBinaria(self, no: 'p.ExpressaoBinaria'):
        return f'({self._render_expr(no.esquerda)} {no.operador} {self._render_expr(no.direita)})'