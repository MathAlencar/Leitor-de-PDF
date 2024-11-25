import tabula
import PyPDF2
import pandas as pd
import csv
import re
import os
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_text
from datetime import date

# Funções auxiliares para uso dentro da biblioteca;

def extraindo_texto(self, pdf, position, indice):
        try:
            reader = PyPDF2.PdfReader(pdf)
            page = reader.pages[indice]
            text = page.extract_text()

        except:
            text = extract_text(pdf)
        
        # alguns extratos estão com a data localizada em pontos diferentes.
        if position == 1:
            return text[:150]
        if position == 2:
            return text[600:]
        if position == 3:
            return text

class Linha:
    def __init__(self, banco, data, descricao, valores, saldo_extrato, saldo_calculado, mes, ano, primeiro_dia_mes):
        self.banco = banco
        self.data = data
        self.descricao = descricao
        self.saldo_extrato = saldo_extrato
        self.saldo_calculado = saldo_calculado
        self.mes = mes
        self.ano = ano
        self.primeiro_dia_mes = primeiro_dia_mes

        pattern_letter = r"^[a-zA-Z\W]+$"
        validando_valores = f'{valores}'

        teste01 = re.match(pattern_letter, validando_valores)

        if validando_valores == '' or teste01:
            self.valores = 0
        else:
            self.valores = valores

def decodificando_csv(lista, arquivo_csv):

    success = False

    encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-15', 'ascii']

    for encoding in encodings:
        try:
            with open(arquivo_csv, 'r', encoding=encoding) as file:
                reader = csv.reader(file)
                for row in reader:
                    lista.append(row)
            success = True
            break
        except UnicodeDecodeError:
            print('continuando...')
        except Exception as e:
            print(f'Demais erro de codificação')  

    if not success:
        print('Não foi possível realizar a codificação deste CSV') 

data_atual = date.today()

# Todos esses 3 foram feitos no formato antigo, por tanto não funcionam da maneira correta, sendo assim necessário a sua manutenção futuramente.

class leitor_pdf_santander:
    
    def __init__(self):
        pass

    def lendo_pdf_santander_v1(self, pdf):

            data_pattern = r"\d{2}/\d{2}/\d{4}"
            texto = r"[a-zA-Z]\w*"

            fim_page = True

            def eh_valor_valido(valor):

                padrao = r"^-?\d{1,3}(?:\.\d{3})*,\d{2}$"
                match = re.match(padrao, valor)

                if valor == '':
                    return True

                return bool(match)

            try:
                with open(pdf, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    num_pages = len(pdf_reader.pages)
            except:
                return num_pages

            area_page01_satander = [[174,0,568,818]]
            area_restPages_santander = [[28,0,568,818]]
            lista_formatada = []
            area_analisada = area_page01_satander
            valores = 0

            indice_teste = 0

            for i in range(num_pages):
                credito = ''
                debito = ''
                saldo = ''

                indice = i+1

                dfs = tabula.read_pdf(pdf, pages=indice, area = area_analisada)
                lista = []

                for table in dfs:
                    table.to_csv("Santander_page.csv")

                    with open('Santander_page.csv', 'r') as file:
                        reader = csv.reader(file)
                        for row in reader:
                            lista.append(row)

                if fim_page == True:

                    for row in lista:
                        credito_validando, debito_validando, saldo_validando = row[-3:]

                        teste_01 = eh_valor_valido(credito_validando)
                        teste_02 = eh_valor_valido(debito_validando)
                        teste_03 = eh_valor_valido(saldo_validando) 

                        if teste_01 and teste_02 and teste_03:
                            credito, debito, saldo = row[-3:]

                        data =  ''
                        descricao = ''

                        for value in row:
                            match = re.match(data_pattern, value)
                            match_texto = re.match(texto, value)

                            teste_01 = eh_valor_valido(value)

                            if match:
                                data = value
                            if match_texto and teste_01 is False:
                                descricao = value

                        if data and descricao:
                                
                            if credito:
                                valores = credito
                            if debito:
                                valores = debito
                            

                            linha = Linha('Banco Santander', data, descricao, valores)
                            lista_formatada.append(linha)
                        
                        if descricao == '' and saldo:

                            if descricao == '' and credito == '' and debito == '' and saldo:
                                descricao = data[10:]
                                data = data[0:10]
                                
                                if credito:
                                    valores = credito
                                if debito:
                                    valores = debito

                                linha = Linha('Banco Santander', data, descricao, valores)
                                lista_formatada.append(linha)

                                indice_teste = indice + 2
                                fim_page = False

                                break

                            descricao = data[10:]
                            data = data[0:10]

                            if credito:
                                valores = credito
                            if debito:
                                valores = debito

                            linha = Linha('Banco Santander', data, descricao, valores)
                            lista_formatada.append(linha)

                        if data is False and descricao is False:
                            
                            descricao = ''
                            data = ''
                            
                            if credito:
                                valores = credito
                            if debito:
                                valores = debito
                            
                            linha = Linha('Banco Santander', data, descricao, valores)
                            lista_formatada.append(linha)

                area_analisada = area_restPages_santander

                if indice == indice_teste:
                    fim_page = True
                    area_analisada = area_page01_satander
            
            return lista_formatada

class leitor_pdf_bradesco:

    def __init__(self):
        pass

    def lendo_bradesco_celular_v1(self, pdf):
        dados = {}

        lista_formatada = []

        with open(pdf, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
        
        area_analisada = [[141,35,558+242,725+35]]

        # Regex:
        data_pattern = r"\d{2}/\d{2}/\d{4}"
        pattern_letter = r"^[a-zA-Z\W]+$"

        def eh_valor_valido(valor):

                padrao = r"^-?\d{1,3}(?:\.\d{3})*,\d{2}$"
                match = re.match(padrao, valor)

                if valor == '':
                    return True

                return bool(match)

        for i in range(num_pages):

            indice = i+1

            dfs = tabula.read_pdf(pdf, pages=indice, area=area_analisada)

            lista = []

            for table in dfs:
                # Aqui você abre o documento e acrescenta o valor:
                table.to_csv("Banco_bradesco_csv", mode='a', header=False, index=False)

            with open('Banco_bradesco_csv', 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    lista.append(row)
        
        os.remove("Banco_bradesco_csv")

        # Variaveis de dados

        # Array para armazenar a descrição, e mesclar depois.
        descricao = []

        # Armazenar a variável de Data no valor.
        data = ''

        # Variável que irá realizar o controle da descrição, onde assim que atingir três, ele reconhece que é uma linha completa.
        k = 0

        # Variáveis de valores, que irá armazenar e caso Debito(True) ou se caso Credito(True)
        valores = 0

        # Variável que irá receber a descrição, transformando ela em string, e assim adicionando na Classe.
        descricaoWord = ''
        
        for row in lista:

            # Buscando datas no PDF;
            buscando_data = re.match(data_pattern, row[0])
            # buscando_descricao = re.match(pattern_letter, row[1])

            # Os valores de credito, debito e saldo, sempre estão localizados nos 3 últimos indices.
            if row[-1]:
                credito, debito, saldo = row[-3:]

            # Se buscando_data for verdadeiro, a variável data é preenchida.
            if buscando_data:
                data = row[0]

            # O código abaixo foi feito e estruturado para pegar toda a descrição da linha, a qual era separada em 3 partes, e mescla-la em uma só.
            # Caso a descrição for SALDO, ela só tem somente uma linha, portanto ela zera o contador K, e retorna o laço ao inicio, dando seguimento na proxima linha.
            if 'SALDO' in row[1]:
                # Se saldo verdadeiro, ele irá aplicar a lógica para encontrar qual o valor válido na linha, sendo ele ou Debito(Caso verdadeiro) ou Crédito(Caso verdadeiro);
                if saldo:
                    valores = '0'
                    if credito:
                        valores = credito
                    if debito:

                        # Por questões de versões diversas, alguns vem com o '-' já declarado no valor, porém caso não, ele será adicionado automaticamente pela condição a baixo.
                        if '-' in debito:
                            valores = debito
                        else:
                            valores = f'-{debito}'
                        
                    if credito and debito:
                        valores = '0'
                
                # Usando a classe Linha, para repassar os dados corretamente.
                row_value = Linha('Bradesco', data, row[1], valores)
                lista_formatada.append(row_value)
                
                # Resetando a variável K
                k = 0
                continue
            
            # Adicionando a descrição no array.
            descricao.append(row[1])

            k+=1 

            if row[1] and row[2]:
                # Se saldo verdadeiro, ele irá aplicar a lógica para encontrar qual o valor válido na linha, sendo ele ou Debito(Caso verdadeiro) ou Crédito(Caso verdadeiro);
                if saldo:
                    valores = '0'
                    if credito:
                        valores = credito
                    if debito:
                        
                        # Por questões de versões diversas, alguns vem com o '-' já declarado no valor, porém caso não, ele será adicionado automaticamente pela condição a baixo.
                        if '-' in debito:
                            valores = debito
                        else:
                            valores = f'-{debito}'
                        
                    if credito and debito:
                        valores = '0'
                
                # Resetando a variável K
                k = 0

                # O Array criado para armazenar a descrição completa da linha, é desmembrado, sendo transformado em uma string.
                for words in descricao:
                    descricaoWord += f' {words}'

                # Usando a classe Linha, para repassar os dados corretamente.
                row_value = Linha('Bradesco', data, descricaoWord, valores)
                lista_formatada.append(row_value)

                # Resetando as variáveis para amabas não acumularem valores.
                descricao = []
                descricaoWord = ''

                continue
            
            if k == 3:
                # Se saldo verdadeiro, ele irá aplicar a lógica para encontrar qual o valor válido na linha, sendo ele ou Debito(Caso verdadeiro) ou Crédito(Caso verdadeiro);
                if saldo:
                    valores = '0'
                    if credito:
                        valores = credito
                    if debito:

                        # Por questões de versões diversas, alguns vem com o '-' já declarado no valor, porém caso não, ele será adicionado automaticamente pela condição a baixo.
                        if '-' in debito:
                            valores = debito
                        else:
                            valores = f'-{debito}'

                    if credito and debito:
                        valores = '0'

                # Resetando a variável K
                k = 0

                # O Array criado para armazenar a descrição completa da linha, é desmembrado, sendo transformado em uma string.
                for words in descricao:
                    descricaoWord += f' {words}'
                
                # Usando a classe Linha, para repassar os dados corretamente.
                row_value = Linha('Bradesco', data, descricaoWord, valores)
                lista_formatada.append(row_value)

                # Resetando as variáveis para amabas não acumularem valores.
                descricaoWord = ''
                descricao = []

                continue
    
        return lista_formatada

class leitor_pdf_banco_itau:

    def __init__(self):
        pass
    
    def lendo_pdf_banco_itau_v1(self, pdf):

        # regex auxiliares
        data_pattern = r"\d{2}/\d{2}"
        texto_pattern = r".*[a-zA-Z]+.*"
        value_pattern = r"^\d{1,3}(?:\.\d{3})*,\d{2}-?$"
         
        # Código para pegar o número de páginas do PDF.
        with open(pdf, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
        
        # Extraindo a tabela de dados:

        area_analisada = [[121,17,757,560]]
        indice = 0
        lista = []
        lista_formatada = []

        # Variaveis de valores;
        mes = ''
        ano = ''
        primeiro_dia_mes = ''
        data = ''
        descricao = ''
        valores = ''

        for i in range(num_pages):

            indice+=1

            dfs = tabula.read_pdf(pdf, pages=indice, stream=True, area=area_analisada)

            for table in dfs:
                table.to_csv("Banco_itau_csv", mode='a', header=False, index=False)
            
        with open('Banco_itau_csv', 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    lista.append(row)    
        
        os.remove('Banco_itau_csv')

        for row in lista:
            
            # capturando data
            for value in row:
                validando_data = re.match(data_pattern, value)
                if validando_data:
                    
                    data = validando_data[0]
                    mes = data[4:5]

                    # Alguns extratos não tem o ano ao lado do mês e dia da transferência, então para ajustar isso apenas valido se o Mês é igual ou menor ao mês capturado, caso sim, se trata de um extrato de 2024, se não é um extrato do ano anterior.
                    mes_atual = data_atual.month

                    if(int(mes) <= mes_atual):
                        ano = data_atual.year
                    else:
                        ano = data_atual.year - 1

                    mes = data[3:5]
                    data = f'{validando_data[0]}/{ano}'

                    primeiro_dia_mes = f'01/{mes}/{ano}'
            
            for value in row:
                validando_texto = re.match(texto_pattern, value)
                if validando_texto:
                    descricao = value
                    break
            
            for value in row:
                validando_valor = re.match(value_pattern, value)
               
                if validando_valor:
                    valores_limpar = value

                    if '-' in valores_limpar:

                        valores_limpar = valores_limpar.replace('-', '')

                        valores = float(f'-{valores_limpar.replace(".", "").replace(",", ".")}') 
                        break
                    else:
                        valores = valores_limpar
                        valores = float(valores.replace(".", "").replace(",", "."))
                        break
            
            if row[-2]:
                row_value = Linha('Banco Itau', data, descricao, valores, '','', mes, ano, primeiro_dia_mes)
                lista_formatada.append(row_value)

        return lista_formatada

    def leitor_pdf_itau_empresas_grafico(self, pdf):

        lista = []
        lista_formatada = []

        pageUm = [[354, 141, 821, 561]]
        AllPage = [[0, 82, 826, 563]]
        indice = 0

        area_analisada = AllPage

        with open(pdf, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
        
        for i in range(num_pages):
            indice+=1

            reader = PyPDF2.PdfReader(pdf)
            page = reader.pages[i]
            text = page.extract_text()

            flag_pagina_um = False
            flag_pagina_dois = False
            contador = 0

            if '01. Conta Corrente e Aplicações Automáticas' in text:
                area_analisada = pageUm
                flag_pagina_um = True
            
            lista_valido = ['data', 'descrição', 'entradas', 'saídas', 'saldo']

            for texto_valido in lista_valido:
                if texto_valido in text:
                    contador = contador + 1

            if contador == 5:
                flag_pagina_dois = True
                print(f'indice: {indice} foi lido')

            if 'Conta Corrente | Saques efetuados' in text or 'Conta Corrente | Débitos automáticos efetuados' in text or '02. Investimentos' in text or 'Notas explicativa' in text or '03. Crédito' in text or 'Débitos automáticos efetuados' in text or 'Pacote de serviços' in text:
                if flag_pagina_um is False and flag_pagina_dois is False:
                    continue
                else:
                    nada = ''

            if flag_pagina_um is False:
                area_analisada = AllPage
            
            dfs = tabula.read_pdf(pdf, pages=indice, area=area_analisada)

            for table in dfs:
                table.to_csv("Banco_bradesco_csv", mode='a', header=False, index=False)
            
        with open('Banco_bradesco_csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                lista.append(row)

        os.remove("Banco_bradesco_csv")

        mes = ''
        ano = ''
        primeiro_dia_mes = ''
        data = ''
        descricao = ''
        valores = ''

        for row in lista:

            descricao = ''
            valores = ''
            valores_validando = '' # Usada para criar uma cópia do valor, e ve se ele contém letras.

            validando_data_final = bool(re.match(r"\d{2}/\d{2}/\d{2}", row[0]))

            validando_data_personnalite = r"\b\d{2}/\d{2}\b"
            
            for value in row:
                buscando_data = re.findall(validando_data_personnalite, value)
                if len(value) <= 6:
                    if buscando_data:
                        data = buscando_data[0]
                        mes = data[4:5]

                        # Alguns extratos não tem o ano ao lado do mês e dia da transferência, então para ajustar isso apenas valido se o Mês é igual ou menor ao mês capturado, caso sim, se trata de um extrato de 2024, se não é um extrato do ano anterior.
                        mes_atual = data_atual.month

                        if(int(mes) <= mes_atual):
                            ano = data_atual.year
                        else:
                            ano = data_atual.year - 1

                        mes = data[3:5]

                        data = f'{buscando_data[0]}/{ano}'

                        primeiro_dia_mes = f'01/{mes}/{ano}'
                        break
                else:
                    nada = ''

            # Validando data pois se caso os meses for acima de 12, se trata de uma informação invalida
            valid_mes = False
            if data != '':
                validando_mes = data[4:5]

                if int(validando_mes) > 12:
                    valid_mes = True

            # Caso as duas buscas por data for falso, aqui ele irá realizar uma nova busca dentro da Linha.
            
            for value in row:
                tem_letras_01 = bool(re.search(r"[a-zA-Z]", value))
                if tem_letras_01 and len(value) > 2:
                    descricao = value

            # Validando/encontrando valores positivos e negativos, onde os mesmo podem estar localizados nos indices do row.
            # validando_valor = r"\d+,\d{2}"

            validando_valor = r"^(?:\d{1,3}(?:\.\d{3})*,\d{2}(?:[-+])?)$"

            for value in row:
                match = re.match(validando_valor, value)

                if match:
                    valores = value
                    valores_validando = value
                    if '-' in valores:
                        valores = valores.replace('-', '')
                        valores = valores.replace(".","").replace(",", '.')
                        valores = float(f'-{valores}')
                    else:
                        valores_validando = value
                        valores = valores.replace(".","").replace(",", '.')
                        valores = float(valores)
                    break

            # Valida se o valor encontrado contém texto, caso sim, ele irá retornar True.

            tem_letras_valores = bool(re.search(r"[a-zA-Z]", valores_validando))

            descricao_invalida = ['na conta corrente (1)','principal',
            'l√≠quido','A Fechamento', 'bruto','do DI', 'líquido', 'Depósitos e recebimentos','DOCs e TEDs'
            'Outras entradas','Saques efetuados','Débitos automáticos efetuados','Outras saídas','Saldo anterior', 'Saldo final', 'Saldo anterior', 'Saldo em C/C']

            # Flag para verificar se a descrição é invalida
            desc_invalida = False

            for validando in descricao_invalida:
                if validando in descricao:
                    desc_invalida = True

            if descricao and valores and desc_invalida is False and valid_mes is False and data != '':
                # Caso validar a data inicial, assim evitando duplicatas, e tbm se há valores inválidos nos números, ele irá adicionar o valor no array.
                if validando_data_final is False and tem_letras_valores is False:
                    # na última verificação eu tiro os valores invalidos com base no mês, já que ele está pegando valores acima de 12.
                    if int(mes) <= 12:
                        rowValue = Linha('Banco Itau Empresa - Personnalite/PJ', data, descricao, valores, '', '',mes, ano, primeiro_dia_mes)
                        lista_formatada.append(rowValue)
                    else:
                        nada = ''

        return lista_formatada

    def leitor_pdf_itau_uniclass(self, pdf):

        with open(pdf, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)

        areaPageUm = [[259, 23, 825, 572]]
        areaPageAll = [[19, 19, 828, 570]]

        # regex para buscar valores padrões:
        data_pattern = r"\d{2}/\d{2}/\d{4}"
        texto = r".*[a-zA-Z]+.*"
        validando_valor = r"^-?\d{1,3}(?:\.\d{3})*,\d{2}$"
        teste_valor = r"-?\d{1,3}(?:\.\d{3})*,\d{2}"

        # Variaveis de validação.
        data = ''
        descricao = ''
        indice = 0

        splitando = []

        lista = []
        lista_formatada = []

        area_analisada = ''
        
        for i in range(num_pages):
            indice+=1

            if indice == 1:
                area_analisada = areaPageUm
            else:
                area_analisada = areaPageAll
            
            dfs = tabula.read_pdf(pdf, pages=indice, area=area_analisada, stream=True)

            for table in dfs:
                table.to_csv('Banco_itau_extrato_simples.csv', mode='a', index=False)

        with open('Banco_itau_extrato_simples.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                lista.append(row)
        
        os.remove('Banco_itau_extrato_simples.csv')

        mes = ''
        ano = ''
        primeiro_dia_mes = ''
        data = ''
        descricao = ''
        
        for row in lista:

            valores = ''

            for value in row:
                match_data = re.match(data_pattern, value)
                match_valor = re.match(validando_valor, value)

                if match_data:
                    data = value[:10]
                    ano = data[6:]
                    mes = data[3:5]
                    primeiro_dia_mes = f'01/{mes}/{ano}'
                if match_valor:
                    valores_verificacao = value
                    
                    valores_verificacao = valores_verificacao.replace(".","").replace(",", ".")
                    valores = float(valores_verificacao)
                    break

                if len(row) >= 2:
                    splitando = row[1].split()

                # Separando o valor da descrição, já que em algumas colunas ambos vem grudados.
                for value in splitando:
                    match = re.search(validando_valor, value)
                    if match:
                        valores = match.group(0)
                
            for value in row:
                    match_descricao = re.match(texto, value)

                    if match_descricao:
                        
                        # Aqui você encontra uma gambiarra para solucionar a vinda de descrição com valores.
                        descricao = value
                        
                        valindaod_data_descricao = re.match(data_pattern, value)

                        if valindaod_data_descricao:
                            data_desc = valindaod_data_descricao[0]
                            descricao = descricao.replace(data_desc, '')
                        break

            # última tentativa de capturar o valor:
            if valores == '':
                for value in row:
                    match_valor = re.findall(teste_valor, value)
                    if len(match_valor) >= 1:
                        valores_verificacao = match_valor[0]
                        valores_verificacao = valores_verificacao.replace(".","").replace(",", ".")
                        valores = float(valores_verificacao)
            
            valores_desc_indesejados = [
                'SALDO FINAL',
                '(=) LIMITE DA CONTA DISPONÍVEL',
                '(+) LIMITE DA CONTA TOTAL',
                '(-) LIMITE DA CONTA UTILIZADO',
                '(=) LIMITE DA CONTA DISPONÕVEL',
                'saldo disponível sem investimentos automáticos',
                '(+) saldo em aplicação automática - aplic aut mais',
                '(+) rendimentos de aplicações automáticas',
                '(+) rendimentos de aplicações automáticas',
                 '(+) saldo em aplicação automática - poup aut',
                 '(=) saldo total disponível',
                 '(+) saldo bloqueado - dep. cheques',
                 '(+) saldo em aplicação automática - poup aut',
                 'LIMITE DA CONTA CONTRATADO',
                 'JUROS DO LIMITE DA CONTA ',
                 'IOF',
                 'detalhamento valor',
                 'TAXA EFETIVA MENSAL',
                 'CUSTO EFETIVO TOTAL (CET) MENSAL',
                 'CUSTO EFETIVO TOTAL (CET) ANUAL ',
                 'Unnamed: 0'
                ]

            flag_verificar_desc = False

            for desc in valores_desc_indesejados:
                if desc in descricao:
                    flag_verificar_desc = True
                    break
            
            if valores and descricao and flag_verificar_desc is False:
                rowValue = Linha('banco itaú - uniclass', data, descricao, valores,'', '', mes, ano, primeiro_dia_mes)
                lista_formatada.append(rowValue)

        return lista_formatada

    def leitor_pdf_itau_empresas(self, pdf):

        with open(pdf, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)

        # regex para buscar valores padrões:
        data_pattern = r"\d{2}/\d{2}"
        texto = r".*[a-zA-Z]+.*"
        validando_valor = r"^-?\d{1,3}(?:\.\d{3})*,\d{2}$"
        teste_valor = r"-?\d{1,3}(?:\.\d{3})*,\d{2}"

        # Variaveis de validação.
        areaPageUm = [[150, 7, 836, 583]]
        areaPageAll = [[19, 19, 828, 570]]

        # variaveis auxiliares
        lista = []
        lista_formatada = []
        areaAnalisada = ''
        indice = 0
        nada = ''
        
        for i in range(num_pages):
            indice+=1

            if indice == 1:
                areaAnalisada = areaPageUm
            else:
                areaAnalisada = areaPageAll
                
            dfs = tabula.read_pdf(pdf, pages=indice, area=areaAnalisada)
                
            for table in dfs:
                table.to_csv('Banco_itau_extrato_empresas.csv', mode='a', index=False)

        with open('Banco_itau_extrato_empresas.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                lista.append(row)
        
        os.remove('Banco_itau_extrato_empresas.csv')

        # Variaveis de busca de valores.
        mes = ''
        ano = ''
        primeiro_dia_mes = ''
        data = ''
        descricao = ''

        for row in lista:
            
            valores = ''

            for value in row:
                match_data = re.match(data_pattern, value)
                match_valor = re.match(validando_valor, value)

                if match_data:
                    data = value
                    mes = data[4:5]
                    
                    mes_atual = data_atual.month

                    if(int(mes) <= mes_atual):
                        ano = data_atual.year
                    else:
                        ano = data_atual.year - 1

                    mes = data[3:5]

                    data = f'{data}/{ano}'

                    primeiro_dia_mes = f'01/{mes}/{ano}'

                if match_valor:
                    valores_verificacao = value
                    
                    valores_verificacao = valores_verificacao.replace(".","").replace(",", ".")
                    valores = float(valores_verificacao)
                    break
                
            for value in row:
                    match_descricao = re.match(texto, value)

                    if match_descricao:
                        
                        # Aqui você encontra uma gambiarra para solucionar a vinda de descrição com valores.
                        descricao = value
                        
                        valindaod_data_descricao = re.match(data_pattern, value)

                        if valindaod_data_descricao:
                            data_desc = valindaod_data_descricao[0]
                            descricao = descricao.replace(data_desc, '')
                        break

            if descricao and valores:
                if int(mes) <= 12:
                    rowValue = Linha('Banco Itau Empresas - itaú empresas', data, descricao, valores, '', '',mes, ano, primeiro_dia_mes)
                    lista_formatada.append(rowValue)
                else:
                    nada = ''
            
        return lista_formatada
    
# Resolvido com o novo formato (CHECK);

class lendo_pdf_brasil:

    def __init__(self):
        pass

    def lendo_pdf_brasil_v1(self, pdf):

        try:
            with open(pdf, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                num_pages = len(pdf_reader.pages)
        except:
            return print("número invalido")

        lista_formatada = []

        # Variaveis de uso;
        indice = 0
        area_analisada = [[85,20,820,580]]

        # Regex para capturar dados:
        data_pattern = r'\d{2}/\d{2}/\d{4}'
        value_pattern = r'\d{1,3}(?:\.\d{3})*,\d{2} \(\+\)|\d{1,3}(?:\.\d{3})*,\d{2} \(-\)'
        retirando_desc = r'\d+,\d{2} \(\+\)|\d+,\d{2} \(-\)|\d{2}:\d{2}|\d{2}/\d{2}/\d{4}|\d{2}/\d{2}'
    
        for i in range(num_pages):
            indice+=1
            dfs = tabula.read_pdf(pdf, pages=indice,  lattice=True, area=area_analisada)

            lista = []

            for table in dfs:
                table.to_csv("Banco_brasil.csv", header=False, index=False)

            with open('Banco_brasil.csv', 'r', encoding="charmap") as file:
                reader = csv.reader(file)
                for row in reader:
                    lista.append(row)
            
            # Variáveis de valores:

            for row in lista:
                
                data = ''
                valores = ''
                descricao = ''
                mes = ''
                ano = ''
                primeiro_dia_mes = ''

                # Aqui estou limpando os dados da descrição, deixando ela limpa, apenas com informações do remetente/destinatário;
                
                for value in row:
                    if value:
                        descricao = value
                        break

                descricao = re.sub(retirando_desc, '', descricao)
                descricao = descricao.replace("\n", "")

                for value in row:
                    buscando_data = re.findall(data_pattern, value)
                    if buscando_data:
                        data = buscando_data[0]
                        mes = data[3:5]
                        ano = data[6:]
                        primeiro_dia_mes = f'01/{mes}/{ano}'

                for value in row:
                    buscando_valores = re.findall(value_pattern, value)
                    if buscando_valores:
                        valores = buscando_valores[0]
                        if '(-)' in valores:
                            
                            valores = valores.replace('(-)', '')
                            valores = float(f'-{valores.replace(".", "").replace(",", ".")}')
                        else:
                            valores = valores.replace('(+)', '')
                            valores = float(f'{valores.replace(".", "").replace(",", ".")}') 


                if data and valores and descricao:

                    row_value = Linha('Banco do Brasil', data, descricao, valores,'','', mes, ano, primeiro_dia_mes)
                    lista_formatada.append(row_value)

        os.remove('Banco_brasil.csv')
        return lista_formatada

# Resolvido com o novo formato (CHECK);

class leitor_pdf_mercado_pago:

    def __init__(self):
        pass

    def leitor_pdf_mercado_pago_v1(self, pdf):
        
        # Variáveis de Indice:
        indice = 0

        # Variaveis para captura de dados
        lista = []
        areaPageUm = [[174, 22, 543, 421]]
        areaPageAll = [[33, 17, 558, 424]]
        area_analisada = areaPageAll
        lista_formatada = []

        # Regex para capturar dados:
        data_pattern = r'\b\d{2}-\d{2}-\d{4}\b'
        valor_pattern = r"^R\$ ?-?\d{1,3}(?:\.\d{3})*,\d{2}$"
        texto_pattern = r".*[a-zA-Z]+.*"

        # Variaveis de valores:
        data = ''
        valores = ''
        mes = ''
        ano = ''
        primeiro_dia_mes = ''
        texto_pattern = r".*[a-zA-Z]+.*"
        contador_ocorrencia = 0
        descricao_adicional = ''
        descricao = ''
        data_pattern = r'\b\d{2}-\d{2}-\d{4}\b'
        valor_pattern = r"^R\$ ?-?\d{1,3}(?:\.\d{3})*,\d{2}$"

        with open(pdf, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
        
        for i in range(num_pages):

            indice+=1

            reader = PyPDF2.PdfReader(pdf)
            page = reader.pages[i]
            text = page.extract_text()

            if 'EXTRATO DE CONTA' in text:
                area_analisada = areaPageUm
            else:
                area_analisada = areaPageAll
        
            dfs = tabula.read_pdf(pdf, pages=indice, area=area_analisada)

            for table in dfs:
                table.to_csv("mercado_pago_csv", mode='a', header=False, index=False)
            
        decodificando_csv(lista, 'mercado_pago_csv');   
        
        os.remove('mercado_pago_csv')

        for row in lista:

            # Pegando data
            for value in row:
                validando_data = re.findall(data_pattern, value)
                if validando_data:
                    data = validando_data[0]
                    mes = data[3:5]
                    ano = data[6:]
                    primeiro_dia_mes = f'01/{mes}/{ano}'
            
            for value in row:
                validando_valores = re.findall(valor_pattern, value)
                if validando_valores:
                    valores_limpar = validando_valores[0]
                    
                    # Arrumando valores pego na tabela, pois os mesmo estão em formato invalido.
                    if '-' in valores_limpar:

                        valores_limpar = valores_limpar.replace('R$', '')

                        valores_limpar = valores_limpar.replace('R$', '')
                        valores = valores_limpar
                        valores = float(valores.replace(".", "").replace(",", ".")) 

                        valores = float(valores)
                        break
                    else:
                        valores_limpar = valores_limpar.replace('R$', '')
                        valores = valores_limpar
                        valores = float(valores.replace(".", "").replace(",", "."))
                        break

            contador = 0

            # Contando quantos valores verdadeiros tem no array, se for igual a 1, significa que a descrição está picada;
            for value in row:
                if value:
                    contador+=1

            # Com a descrição picada, eu procuro o valor verdadeiro e realizo o incremento na variavel de descrição adicional, e incrementando no contador_ocorrencia;
            if contador == 1:
                for value in row:
                    if value:
                        descricao_adicional+=' '+value
                        contador_ocorrencia+=1

            # Caso o contador_ocorrencia for incrementado, ele irá rodar o loop mais uma vez para encontrar o segundo valor.
            if contador_ocorrencia == 1:
                continue
            
            # Porém se a descriçaõ vim completa, ele irá apenas procurar normalmente um padrão de texto.
            if contador_ocorrencia == 0 and contador > 1:
                for value in row:
                    validando_texto = re.findall(texto_pattern, value)
                    if validando_texto:
                        descricao = validando_texto[0]
                        break
            
            # Quando a descrição picada ficar completa, o contador_ocorrencia será dois, sendo assim adicionado na variavel descrição;
            if contador_ocorrencia == 2:
                descricao = descricao_adicional
                contador_ocorrencia = 0
                descricao_adicional = ''
            
            # A linha só será adicionada caso o contador de ocorrencia for zerado(Significa que ou ele achou e completou a descrição picada ou não foi necessário o processo.)
            # Aqui ele irá verificar de todosos valores foram preenchidos, e por fim validar se o último valor do indice é diferente de '', pois se sim, ele não é contabilizado
            # porque somente a sua descrição foi capturada.
            
            # Validando descrição, pois ela está pegando valores(reais) como descrição.
            validando_descricao = re.findall(valor_pattern, descricao)

            if contador_ocorrencia == 0 and data and valores and len(validando_descricao) < 1:
                rowValue = Linha('Mercado Pago', data, descricao, valores,'','', mes, ano, primeiro_dia_mes)
                lista_formatada.append(rowValue)
        
        return lista_formatada

# Resolvido com o novo formato (CHECK);

class leitor_pdf_inter:

    def __init__(self):
        pass

    def leitor_pdf_inter_v1(self, pdf):

        # Variaveis para armazenar dados
        lista = []
        lista_formatada = []

        # Regex para captura de valores:
        data_pattern = r'(\d{1,2})\s+de\s+(Janeiro|Fevereiro|Março|Abril|Maio|Junho|Julho|Agosto|Setembro|Outubro|Novembro|Dezembro)\s+de\s+(\d{4})'
        valores_pattern = r'(-?R\$\s*\d{1,3}(?:\.\d{3})*,\d{2})'
        texto_pattern = r'[A-Za-zÀ-ÖØ-öù-ÿ]+(?:\s+[A-Za-zÀ-ÖØ-öù-ÿ]+)*'

        # funções e vriáveis auxiliares
        meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        data = ''
        
        with open(pdf, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)

        indice = 0

        for i in range(num_pages):
            indice+=1
            dfs = tabula.read_pdf(pdf, pages=indice, area=[180, 39, 743, 555])

            for table in dfs:
                table.to_csv("inter_csv", mode='a', index=False)
        

        with open('inter_csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                lista.append(row)
        
        os.remove('inter_csv')

        for row in lista:

            valores = ''
            descricao = ''

            # capturando data.
            for value in row:
                matches = re.findall(data_pattern, value)

                if matches:
                    trabalhando_data = matches[0]

                    dia = trabalhando_data[0]
                    mes = trabalhando_data[1]
                    ano = trabalhando_data[2]

                    # Aqui estou alterando o valor do mes para um valor númerico equivalente.
                    for i in range(len(meses)):
                        if mes == meses[i]:
                            if i+1 >= 10:
                                mes = i+1
                                break  
                            mes = f'0{i+1}'
                            break

                    # Agora aqui estou apenas adicionando um 0 a mais para valores abaixo de 9
                    dia = int(dia)
                    if dia <= 9:
                        dia = f'0{dia}'

                    primeiro_dia_mes = f'01/{mes}/{ano}'
                    data = f'{dia}/{mes}/{ano}'

            # capturando valores.
            for value in row:
                matches_valor = re.findall(valores_pattern, value)

                if matches_valor:
                    valores_limpar = matches_valor[0]

                    if '-' in valores_limpar:
                        valores_limpar = valores_limpar.replace('-R$', '').replace(" ", "")
                        valores_limpar = valores_limpar.replace(".", "").replace(",", ".")
                        valores = float(f'-{valores_limpar}')
                    else:
                        valores_limpar = valores_limpar.replace('R$', '').replace(" ", "")
                        valores_limpar = valores_limpar.replace(".", "").replace(",", ".")
                        valores = float(valores_limpar)
                    
            # capturando decrição.
            for value in row:
                matches_texto = re.findall(texto_pattern, value)
                matches_valor_texto = re.findall(valores_pattern, value)
                
                if matches_texto and matches_valor_texto:
                    descricao = f'{row[0]} {row[1]}'
                    break

            if valores:
                rowValue = Linha('Banco - inter', data, descricao, valores,'','', mes, ano, primeiro_dia_mes)
                lista_formatada.append(rowValue)
                descricao = ''
        
        return lista_formatada

    def leitor_pdf_inter_v2(self, pdf):

        # Regex para captura de dados
        data_pattern = r'(\d{1,2})\s+de\s+(Janeiro|Fevereiro|Março|Abril|Maio|Junho|Julho|Agosto|Setembro|Outubro|Novembro|Dezembro)\s+de\s+(\d{4})'
        valores_pattern = r'(-?R\$\s*\d{1,3}(?:\.\d{3})*,\d{2})'
        texto_pattern = r'[A-Za-zÀ-ÖØ-öù-ÿ]+(?:\s+[A-Za-zÀ-ÖØ-öù-ÿ]+)*'

        # variaveis de armazenamento de dados:
        lista = []
        lista_formatada = []

        # variaveis e funções auxiliares:
        meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        data = ''

        with open(pdf, 'rb') as file_path:
            reader = PyPDF2.PdfReader(file_path)
            num_pages = len(reader.pages)
        
        page_um = [194, 36, 783, 560]
        page_any = [38, 33, 780, 592]
    
        indice = 0

        for i in range(num_pages):
            
            indice+=1

            reader = PyPDF2.PdfReader(pdf)
            page = reader.pages[i]
            text = page.extract_text()

            if 'Instituição: Banco Inter' in text:
                area_analisada = page_um
            else:
                area_analisada = page_any

            dfs = tabula.read_pdf(pdf, pages=indice, area=area_analisada, stream=True)
        
            for table in dfs:
                table.to_csv('banco_inter_csv', mode='a', index=False)

        with open('banco_inter_csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                lista.append(row)
        
        os.remove('banco_inter_csv')

        for row in lista:
            # capturando a data
            for value in row:
                matches_data = re.findall(data_pattern, value)

                if matches_data:
                    trabalhando_data = matches_data[0]

                    dia = trabalhando_data[0]
                    mes = trabalhando_data[1]
                    ano = trabalhando_data[2]

                    # Aqui estou alterando o valor do mes para um valor númerico equivalente.
                    for i in range(len(meses)):
                        if mes == meses[i]:
                            if i+1 >= 10:
                                mes = i+1
                                break  
                            mes = f'0{i+1}'
                            break

                    # Agora aqui estou apenas adicionando um 0 a mais para valores abaixo de 9
                    dia = int(dia)
                    if dia <= 9:
                        dia = f'0{dia}'

                    primeiro_dia_mes = f'01/{mes}/{ano}'
                    data = f'{dia}/{mes}/{ano}'
            
            # capturando valores monetários
            for value in row:
                matches_valor = re.findall(valores_pattern, value)

                if matches_valor:
                    valores_limpar = matches_valor[0]

                    if '-' in valores_limpar:
                        valores_limpar = valores_limpar.replace('-R$', '').replace(" ", "")
                        valores_limpar = valores_limpar.replace(".", "").replace(",", ".")
                        valores = float(f'-{valores_limpar}')
                    else:
                        valores_limpar = valores_limpar.replace('R$', '').replace(" ", "")
                        valores_limpar = valores_limpar.replace(".", "").replace(",", ".")
                        valores = float(valores_limpar)

                    break
            
            # capturando descrições.
            for value in row:
                matches_texto = re.findall(texto_pattern, value)

                if matches_texto:
                    descricao = value
                    break
            
            if 'Saldo do dia' in descricao:
                continue

            if valores and descricao:
                rowValue = Linha('Banco - inter', data, descricao, valores,'','', mes, ano, primeiro_dia_mes)
                lista_formatada.append(rowValue)
        
        return lista_formatada

class leitor_pdf_PicPay:

    def __init__(self):
        pass

    def leitor_pdf_PicPay_v1(self, pdf):


        # Variáveis de Indice:
        indice = 0

        # Variaveis para captura de dados
        lista = []
        areaPageUm = [[239, 6, 717, 583]]
        areaPageAll = [[33, 17, 558, 424]]
        area_analisada = areaPageUm
        lista_formatada = []

        # Regex para capturar dados:
        data_pattern = r"\b\d{2}/\d{2}/\d{4}\b"
        valor_pattern = r"-? ?R\$ ?\d{1,3}(?:\.\d{3})*,\d{2}"
        texto_pattern = r".*[a-zA-Z]+.*"

        # Variaveis de valores:
        data = ''
        mes = ''
        ano = ''
        primeiro_dia_mes = ''

        # Pegando o número de páginas:
        with open(pdf, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)

        for i in range(num_pages):
            indice+=1

            dfs = tabula.read_pdf(pdf, pages=indice, area=area_analisada)

            for table in dfs:
                table.to_csv("PicPay_csv", mode='a', header=False, index=False)
                
        with open('PicPay_csv', 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    lista.append(row) 

        os.remove('PicPay_csv')

        for row in lista:

            valores = ''
            descricao = ''
            
            # Capturando Data:
            for value in row:
                validando_data = re.findall(data_pattern, value)
                if validando_data:
                    data = validando_data[0]
                    mes = data[3:5]
                    ano = data[6:]
                    primeiro_dia_mes = f'01/{mes}/{ano}'

            # Capturando Valores:
            for value in row:
                validando_valores = re.findall(valor_pattern, value)
                if validando_valores:
                    valores_limpar = validando_valores[0]
                    
                    # Arrumando valores pego na tabela, pois os mesmo estão em formato invalido.
                    if '-' in valores_limpar:
                        # Formatando o valor para deixar no padrão do python para números de ponto flutuante.
                        valores_limpar = valores_limpar.replace('R$', '').replace('-', '').replace(".", "").replace(",", ".").replace(" ", "")

                        valores = float(f'-{valores_limpar}') 
                    else:
                        valores_limpar = valores_limpar.replace('R$', '')
                        valores = valores_limpar
                        valores = float(valores.replace(".", "").replace(",", ".")) 
                    break
            
            for value in row:
                validando_texto = re.findall(texto_pattern, value)
                if validando_texto:
                    descricao = validando_texto[0]
                    break

            if data and valores and descricao:
                rowValue = Linha('PicPay', data, descricao, valores,'','', mes, ano, primeiro_dia_mes)
                lista_formatada.append(rowValue)
        
        return lista_formatada

class PdfReaderVersion:
    
    def __init__(self):
        pass
    
    def extraindo_texto(self, pdf):
        try:
            reader = PyPDF2.PdfReader(pdf)
            page = reader.pages[0]
            text = page.extract_text()

        except:
            text = extract_text(pdf)
        
        return text

class to_excel:

    def transformando_excel(self, lista, codificacao):

        with open('extrato_lido.csv', 'w', newline='', encoding=codificacao) as arquivo_csv:
            escritor_csv = csv.writer(arquivo_csv)

            escritor_csv.writerow(["banco", "data", "desc", 'Movimentacao', "valor", 'saldo_extrato', 'saldo_calculado', 'mes', 'ano', 'primeiro_dia_mes'])

            for row in lista:
                escritor_csv.writerow([row.banco, row.data, row.descricao, row.descricao, row.valores, row.saldo_extrato, row.saldo_calculado, row.mes, row.ano, row.primeiro_dia_mes])

        try:
            df = pd.read_csv('extrato_lido.csv', encoding='mac_roman')
        except:
            return print("Formatação incorreta")

        os.remove('extrato_lido.csv');
        df.to_excel('Extrato.xlsx', index=False, sheet_name="Extratos")
