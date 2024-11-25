from leitor_all import lendo_pdf_brasil, PdfReaderVersion, to_excel, leitor_pdf_santander, leitor_pdf_bradesco, leitor_pdf_banco_itau, leitor_pdf_mercado_pago, leitor_pdf_PicPay, leitor_pdf_inter
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import os
import csv
from io import StringIO
import tempfile # Lida com arquivoe stemporávios, validar ainda ()
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pandas as pd
from openpyxl import load_workbook

# Classes do meu código (FrameWork)

versao_pdf = PdfReaderVersion()
banco_brasil = lendo_pdf_brasil()
Santander_banco = leitor_pdf_santander()
Bradesco_banco = leitor_pdf_bradesco()
banco_itau = leitor_pdf_banco_itau()
transform_excel = to_excel()
mercado_pago = leitor_pdf_mercado_pago()
PicPay = leitor_pdf_PicPay()
banco_inter = leitor_pdf_inter()

global lista_valores

lista_valores = []

EXPIRATION_TIME = 300 # Aqui defini 5 min, mas e será uma constante.
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def removendo_arquivos():
    now = datetime.now()
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(file_path):
            file_criacao_arquivo = datetime.fromtimestamp(os.path.getmtime(file_path))
            # Aqui após ele pegar o tempo de criação do arquivo, ele irá comparar com o tempo definido, no timedelta(5 minutos)
            if now - file_criacao_arquivo > timedelta(seconds=EXPIRATION_TIME):
                os.remove(file_path)

def transformando_excel(lista):
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx', dir=UPLOAD_FOLDER)

        with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='', suffix='.csv', errors='replace') as arquivo_csv:
            escritor_csv = csv.writer(arquivo_csv)

            escritor_csv.writerow(["banco", "data", "desc", 'Movimentacao', "valor", 'saldo_extrato', 'saldo_calculado', 'mes', 'ano', 'primeiro_dia_mes'])

            for row in lista:

                verificando_tipo = type(row.valores) # pegando o tipo para validar se o erro se aplica a este extrato.

                if verificando_tipo is str: # caso for str, ele irá realizar a formatação.
                    if ',' in row.valores: # alguns vem com ',' ainda, po tanto reforço para tirar o valor invalido.
                        try:
                            row.valores = row.valores.replace('.', '').replace(',', '.') # replace dos valores.
                            row.valores = float(row.valores) # formatando em float.
                        except:
                            print('não é um valor válido!')
                    else:
                        row.valores = float(row.valores) # formatando em float.

                escritor_csv.writerow([row.banco, row.data, row.descricao, row.descricao, row.valores, row.saldo_extrato, row.saldo_calculado, row.mes, row.ano, row.primeiro_dia_mes])
            
            # Aqui você está pegando o nome do proprio arquivo CSV
            csv_temp_filename = arquivo_csv.name
        try:
            # Lê o arquivo CSV e converte para dataFrame
            df = pd.read_csv(csv_temp_filename, encoding='mac_roman')
        except:
            return print("Formatação incorreta")
        
        df.to_excel(temp_file.name, index=False, sheet_name="Extratos")

        os.remove(csv_temp_filename)

        return temp_file.name

# Inicializa o agendador para verificar arquivos expirados a cada minuto
scheduler = BackgroundScheduler()
scheduler.add_job(func=removendo_arquivos, trigger="interval", seconds=60)
scheduler.start()

# Modelos de PDF para leitura

leitor_mercado_pago = [
    'Data Descrição ID da operação Valor Saldo'
]
leitor_picPay = [
    'Cliente desde:'
]
leitor_pdf_banco_brasil = [
    'Extrato de Conta Corrente'
]
leitor_pdf_itau_pj_personnalite = [
    '01. Conta Corrente e Aplicações Automáticas', '01.ContaCorrente'
]
leitor_pdf_banco_itau_simples = [
    'Agência:                Conta:                              Nome:'
]
leitor_pdf_itau_uniclass = [
    '* Total contratado. O uso do Limite da Conta e Limite da Conta adicional poderá ter cobrança de juros + IOF.'
]
leitor_pdf_itauEmpresas = [
    'ItaúEmpresas'
]
leitor_pdf_inter_v1 = [
    'Ouvidoria:0800 940 7772'
]
leitor_pdf_inter_v2 = [
    'Instituição: Banco Inter'
]

app = Flask(__name__)
CORS(app)

# Classe para armazenar os dados das linhas (se necessário para algum processamento adicional)
class Linha:
    def __init__(self, data, descricao, valor):
        self.data = data
        self.descricao = descricao
        self.valor = valor

# Rota para fazer upload dos PDFs e processar os dados
@app.route('/upload/pdfs', methods=['POST'])
def upload_pdfs():

    # Sempre definida como falso, flag que irá alterar o seu valor para True, caso encontrar o modelo de PDF para ser lido.
    status = False

    if 'arquivos[]' not in request.files:
        return jsonify({"menssage": "Nenhum arquivo foi enviado!"}), 400
    
    arquivos = request.files.getlist('arquivos[]')

    if not arquivos:
        return jsonify({'menssage': "Nenhum arquivo selecionado!"}), 400
    
    arquivos_nao_lidos = []

    for arquivo in arquivos:

        if arquivo.filename == '':
            continue

        if not arquivo.filename.endswith('.pdf'):
            continue

        arquivo.save(arquivo.filename)

        # Extrair o texto do PDF
        texto = versao_pdf.extraindo_texto(arquivo)

        # Verificar se o texto corresponde a algum padrão conhecido

        global lista_valores # Declarada de forma global pois irá receber todos os dados puxados de todos os PDF's independe de sua versão.
        status_capturando_nao_lido = True # Capturar o nome do PDF que nao foi lido

        # Banco Inter
        for texto_padrao in leitor_pdf_inter_v2:

            if texto_padrao in texto:
                lista_dados = banco_inter.leitor_pdf_inter_v2(arquivo.filename)

                codificacao = 'utf-8'

                status = True
                status_capturando_nao_lido = False

                for row in lista_dados:
                    lista_valores.append(row)

        for texto_padrao in leitor_pdf_inter_v1:
            
            if texto_padrao in texto:
                lista_dados = banco_inter.leitor_pdf_inter_v1(arquivo.filename)

                codificacao = 'utf-8'

                status = True
                status_capturando_nao_lido = False

                for row in lista_dados:
                    lista_valores.append(row)

        # Leitor Itaú
        for texto_padrao in leitor_pdf_itau_pj_personnalite:

            if texto_padrao in texto:
                lista_dados = banco_itau.leitor_pdf_itau_empresas_grafico(arquivo.filename)

                codificacao = 'utf-8'

                status = True
                status_capturando_nao_lido = False

                for row in lista_dados:
                    lista_valores.append(row)

        for texto_padrao in leitor_pdf_banco_itau_simples:

            if texto_padrao in texto:
                lista_dados = banco_itau.lendo_pdf_banco_itau_v1(arquivo.filename)

                codificacao = 'utf-8'

                status = True
                status_capturando_nao_lido = False

                for row in lista_dados:
                    lista_valores.append(row)

        for texto_padrao in leitor_pdf_itau_uniclass:

            if texto_padrao in texto:
                lista_dados = banco_itau.leitor_pdf_itau_uniclass(arquivo.filename)

                codificacao = 'utf-8'

                status = True
                status_capturando_nao_lido = False

                for row in lista_dados:
                    lista_valores.append(row)

        for texto_padrao in leitor_pdf_itauEmpresas:

            if texto_padrao in texto:
                lista_dados = banco_itau.leitor_pdf_itau_empresas(arquivo.filename)

                status = True
                status_capturando_nao_lido = False

                for row in lista_dados:
                    lista_valores.append(row)

        # Leitor picPay
        for texto_padrao in leitor_picPay:

            if texto_padrao in texto:

                lista_dados = PicPay.leitor_pdf_PicPay_v1(arquivo.filename)

                status = True
                status_capturando_nao_lido = False

                for row in lista_dados:
                   lista_valores.append(row)
        
        # Leitor Banco do Brasil
        for texto_padrao in leitor_pdf_banco_brasil:
            if texto_padrao in texto:
                lista_dados = banco_brasil.lendo_pdf_brasil_v1(arquivo.filename)

                status = True
                status_capturando_nao_lido = False

                for row in lista_dados:
                    lista_valores.append(row)
                
        # Leitor Mercado pago 
        for texto_padrao in leitor_mercado_pago:
            if texto_padrao in texto:
                
                lista_dados = mercado_pago.leitor_pdf_mercado_pago_v1(arquivo.filename)

                status = True
                status_capturando_nao_lido = False

                for row in lista_dados:
                    lista_valores.append(row)

        if status_capturando_nao_lido is True:
            arquivos_nao_lidos.append(arquivo.filename)

        os.remove(arquivo.filename)

    # Lógica feita para validar e retornar algum valor caso o PDF não for encontrado na base para leitura.
    if status == True:
        excel_temp_nome = transformando_excel(lista_valores)
        lista_valores = []
        if len(arquivos_nao_lidos) == 0:
            return jsonify({'temp_file': excel_temp_nome, 'menssage': f'Arquivos processados com sucesso.'})
        if len(arquivos_nao_lidos) >= 1:

            arquivos_nao_lidos_string = ''

            for texto in arquivos_nao_lidos:
                arquivos_nao_lidos_string+=f'{texto} \n'
            
            return jsonify({'temp_file': excel_temp_nome, 'menssage': f'Arquivos processados com sucesso, com exceção desse/s arquivos {arquivos_nao_lidos_string} pois o código não foi capaz de identificar a sua versão'})
    
    if status == False:
        lista_valores = []
        return jsonify({'menssage': 'Não sei ler esse não'})

#API para realizar o download do arquivo em formato xlsx    
@app.route('/download_xlsx')
def download_xlsx():

    temp_file_path = request.args.get('file')

    if not temp_file_path or not os.path.exists(temp_file_path):
        return jsonify({'error': 'Arquivo não encontrado!'}), 404
    
    with open(temp_file_path, 'rb') as temp_file:
        excel_content = temp_file.read()

    response = make_response(excel_content)
    response.headers['Content-Disposition'] = f'attachment; filename=arquivo.xlsx'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    os.remove(temp_file_path)

    return response

app.run()
