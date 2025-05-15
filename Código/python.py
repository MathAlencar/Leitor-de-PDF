from leitor_all import lendo_pdf_brasil, PdfReaderVersion, to_excel, leitor_pdf_santander, leitor_pdf_bradesco, leitor_pdf_banco_itau, leitor_pdf_mercado_pago, leitor_pdf_PicPay, leitor_pdf_sisprime, leitor_pdf_inter, leitor_pdf_sicredi, leitor_pdf_cSix, leitor_pdf_SICOOB, leitor_pdf_next, leitor_pdf_sofisa
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
sisprime = leitor_pdf_sisprime()
sicredi = leitor_pdf_sicredi()
next = leitor_pdf_next()
sofisa = leitor_pdf_sofisa()
csix = leitor_pdf_cSix()

global lista_valores

lista_valores = []

EXPIRATION_TIME = 300 # Aqui defini 5 min, mas e será uma constante.


UPLOAD_FOLDER = 'uploads'
NAO_LIDO_FOLDER = 'Nao_lidos'

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

def salvando_pdf_nao_lido(pdf):

    diretorio_atual = os.getcwd()

    diretorio_destino = f'{diretorio_atual}/Nao_lidos'

    os.makedirs(diretorio_destino, exist_ok=True)

    caminho_arquivo = os.path.join(diretorio_destino, pdf.filename)

    pdf.save(caminho_arquivo)

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

leitor_pdf_banco_brasil_v1 = [
    'Extrato de Conta Corrente'
]
leitor_pdf_banco_brasil_v2 = [
    'Serviço de Atendimento ao Consumidor - SAC 0800 729 0722', 'Consultas - Extrato de conta corrente'
]
leitor_pdf_banco_brasil_v3 = [
    'SISBB - Sistema de Informações Banco do Brasil'
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
leitor_pdf_itauEmpresasSimples = [
    'Saldo total Limite da conta Utilizado Disponível'
]
leitor_pdf_itauEmpresas2 = [
    'limite da conta utilizado limite da conta disponível'
]
leitor_pdf_itauDigital = [
    'dados geraisnome'
]



leitor_pdf_sicredi_text = [
    'Lançamentos futuros a partir de hoje,'
]
leitor_pdf_sicredi_text_v2 = [
    'Data Descrição Documento Valor (R$) Saldo (R$)'
]
leitor_pdf_sicredi_text_v3 = [
    'A s s o c i a d o :'
]

leitor_pdf_inter_v1 = [
    'Ouvidoria:0800 940 7772'
]
leitor_pdf_inter_v2 = [
    'Instituição: Banco Inter'
]

leitor_pdf_sisprimeText =  [
    'OS DADOS ACIMA SÃO BASEADOS NAS INFORMAÇÕES DISPONÍVEIS ATÉ ESTE INSTANTE E PODERÃO SER ALTERADOS A QUALQUER MOMENTO EM FUNÇÃO DE NOVOS LANÇAMENTOS'
]

leitor_pdf_c6_text_v1 = [
    'Extrato exportado no dia'
]

leitor_pdf_bradesco_text = [
    'Bradesco Celular'
]

leitor_pdf_sofisa_text = [
    'Banco Sofisa S.A.'
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

        # Juntando texto.
        texto = ' '.join(texto.split())  # Remove espaços extras e quebra de linhas)

        # Verificar se o texto corresponde a algum padrão conhecido

        global lista_valores # Declarada de forma global pois irá receber todos os dados puxados de todos os PDF's independe de sua versão.
        status_capturando_nao_lido = True # Capturar o nome do PDF que nao foi lido

        # Leitor PDF sofisa
        for texto_padrao in leitor_pdf_sofisa_text:
            if texto_padrao in texto:

                lista_dados =  sofisa.leitor_pdf_sofisa_v1(arquivo.filename)

                status = True
                status_capturando_nao_lido = False

                for row in lista_dados:
                    lista_valores.append(row)
        
        # Leitor PDF C6
        for texto_padrao in leitor_pdf_c6_text_v1:
            if texto_padrao in texto:

                lista_dados = csix.leitor_pdf_CSIX_v1(arquivo.filename)

                status = True
                status_capturando_nao_lido = False

                for row in lista_dados:
                    lista_valores.append(row)

        # Banco Sicredi
        for texto_padrao in leitor_pdf_sicredi_text:
            if texto_padrao in texto:

                lista_dados = sicredi.leitor_pdf_sicredi_v1(arquivo.filename)

                status = True
                status_capturando_nao_lido = False

                for row in lista_dados:
                    lista_valores.append(row)
        
        for texto_padrao in leitor_pdf_sicredi_text_v2:
            if texto_padrao in texto:

                lista_dados = sicredi.leitor_pdf_sicredi_v2(arquivo.filename)

                status = True
                status_capturando_nao_lido = False

                for row in lista_dados:
                    lista_valores.append(row)

        for texto_padrao in leitor_pdf_sicredi_text_v3:
            if texto_padrao in texto:

                lista_dados = sicredi.leitor_pdf_sicredi_v3(arquivo.filename)

                status = True
                status_capturando_nao_lido = False

                for row in lista_dados:
                    lista_valores.append(row)

        # Banco Sisprime

        for texto_padrao in leitor_pdf_sisprimeText:
            
            if texto_padrao in texto:
                lista_dados = sisprime.leitor_pdf_sisprime_v1(arquivo.filename)

                status = True
                status_capturando_nao_lido = False

                for row in lista_dados:
                    lista_valores.append(row)

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

        for texto_padrao in leitor_pdf_itauEmpresasSimples:
            if texto_padrao in texto:
                lista_dados = banco_itau.leitor_pdf_itau_empresasSimples(arquivo.filename)

                status = True
                status_capturando_nao_lido = False

                for row in lista_dados:
                    lista_valores.append(row)

        for texto_padrao in leitor_pdf_itauDigital:
            if texto_padrao in texto:
                lista_dados = banco_itau.leitor_pdf_itau_digital(arquivo.filename)

                status = True
                status_capturando_nao_lido = False

                for row in lista_dados:
                    lista_valores.append(row)

        for texto_padrao in leitor_pdf_itauEmpresas2:
            if texto_padrao in texto:
                lista_dados = banco_itau.leitor_pdf_itau_empresasSimples2(arquivo.filename)

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
        for texto_padrao in leitor_pdf_banco_brasil_v1:
            if texto_padrao in texto:
                lista_dados = banco_brasil.lendo_pdf_brasil_v1(arquivo.filename)

                status = True
                status_capturando_nao_lido = False

                for row in lista_dados:
                    lista_valores.append(row)

                print('Banco do brasil - v1')
        
        for texto_padrao in leitor_pdf_banco_brasil_v2:

            if texto_padrao in texto:

                lista_dados = banco_brasil.lendo_pdf_brasil_v2(arquivo.filename)

                status = True
                status_capturando_nao_lido = False

                for row in lista_dados:
                    lista_valores.append(row)

                print('Banco do brasil - v2')
        
        for texto_padrao in leitor_pdf_banco_brasil_v3:

            if texto_padrao in texto:

                lista_dados = banco_brasil.lendo_pdf_brasil_v3(arquivo.filename)

                status = True
                status_capturando_nao_lido = False

                for row in lista_dados:
                    lista_valores.append(row)

                print('Banco do brasil - v2')
        
        # Leitor Mercado pago 
        for texto_padrao in leitor_mercado_pago:
            if texto_padrao in texto:
                
                lista_dados = mercado_pago.leitor_pdf_mercado_pago_v1(arquivo.filename)

                status = True
                status_capturando_nao_lido = False

                for row in lista_dados:
                    lista_valores.append(row)

        # Leitor Bradesco 
        for texto_padrao in leitor_pdf_bradesco_text:
            if texto_padrao in texto:
                
                lista_dados = Bradesco_banco.lendo_bradesco_celular_v1(arquivo.filename)

                status = True
                status_capturando_nao_lido = False

                for row in lista_dados:
                    lista_valores.append(row)

        if status_capturando_nao_lido is True:
            arquivos_nao_lidos.append(arquivo.filename)
            salvando_pdf_nao_lido(arquivo)
            os.remove(arquivo.filename)
        else:
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4222, debug=True)

# app.run()
