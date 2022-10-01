from random import randint, random, randrange
import time
import paho.mqtt.client as mqtt
import pandas


LIST_CLASS = ["A", "B", "C"]
QTD_PRODUTOS = 200
QTD_LOJAS_MAX = 20
LIMITE_PROD_A = 100
LIMITE_PROD_B = 60
LIMITE_PROD_C = 20
MAX_CAPACITY = {"A":LIMITE_PROD_A, "B":LIMITE_PROD_B, "C":LIMITE_PROD_C}
DIA = 1
QTD_PROD_NA_LOJA = randint(15,25)
PROD_ID = [i+1 for i in range(QTD_PROD_NA_LOJA)]
START_REQUEST = ["0" for i in range(QTD_PRODUTOS)]
SOLICITACAO_THRESHOLD = 0.25
DESNECESSARIO = "recebi produto que não deveria!"

first_contact = True
topico_pedir = "Loja - CDD"
topico_receber = "CDD - Loja"
whoami = 0
produtos = {}
produtos["ID"] = {}
produtos["CLASS"] = {}
produtos["QTD"] = {}
lista_requests = START_REQUEST
    
#def on_publish(client, userdata, message_id):
#    print("", client, "message_id:", str(message_id))


def criar_conexao(client):
    client.publish(topico_pedir, "Oi Fredy!", qos = 1)
    client.subscribe (topico_receber, qos=1)

def on_message(client, userdata, message):
    global whoami
    global topico_pedir
    global topico_receber
    global first_contact

    if first_contact:
        whoami = int(message.payload.decode())
        first_contact = False
        topico_pedir = "Loja "+str(whoami)+" - CDD"
        topico_receber = "CDD - Loja "+str(whoami)
        print("Agora estou conectado nos canais '"+topico_receber+"' e '"+topico_pedir+"'!")
    else:
        reabastecer(str.split(message.payload.decode(), " - ")[2])

def Cliente_Lojas():
    global produtos
    global lista_requests
    today = 0
    id_request = 1
    
    client = mqtt.Client()
    client.connect("broker.hivemq.com", 1883)
    client.on_message = on_message
    criar_conexao(client=client)


    client.subscribe (topico_receber, qos=1)
    client.loop_start()

    for i in PROD_ID:
        with open("Produtos.csv", "r") as file:
            df = pandas.read_csv(file, sep = ";")
            produtos["ID"][i] = randint(1,QTD_PRODUTOS)
            produtos["CLASS"][i] = (df.loc[df['Produto ID'] == produtos["ID"][i], ['Classe']]).values[0][0]
            produtos["QTD"][i] = MAX_CAPACITY[produtos["CLASS"][i]]

    while True:
        produtos = passa_tempo(produtos)
        today += 1
        lista_requests, reposicoes = valida_reposicao(produtos, lista_requests)
        message = "Dia: "+ str(today) + " - REQUEST " + str(id_request) + " - " + str(reposicoes)
        if int(reposicoes) > 0:
            print(message)
            id_request += 1
            client.publish(topico_pedir, message, qos = 1)

def valida_reposicao(produtos, lista_antiga):
    soma = START_REQUEST
    for i in PROD_ID:
        if produtos["QTD"][i] <= SOLICITACAO_THRESHOLD * MAX_CAPACITY[produtos["CLASS"][i]]:
            soma[produtos["ID"][i]] = "1"
    lista_atual = ""
    new_requests = ""
    for i in range(len(soma)):
        lista_atual = lista_atual + soma[i]
        if lista_antiga[i] == "1" and lista_atual[i] == "1":
            new_requests += "0"
        else:
            new_requests += lista_atual[i]
    return lista_atual, new_requests


def passa_tempo(produtos):
    for prod_index in PROD_ID:
        produtos["QTD"][prod_index] -= randint(0,5)
        if produtos["QTD"][prod_index] < 0:
            produtos["QTD"][prod_index] = 0
    time.sleep(DIA)
    return produtos

def reabastecer(reabastecimento):
    global lista_requests
    
    for i in range(QTD_PRODUTOS):
        if reabastecimento[i] == "1":
            produtos["QTD"][i] += MAX_CAPACITY[produtos["CLASS"][i]] * (1-SOLICITACAO_THRESHOLD)
    lista_atual = ""
    for i in range(len(reabastecimento)):
        if lista_requests[i] == "0" and reabastecimento[i] == "1":
            raise DESNECESSARIO
        if lista_requests[i] == "1" and reabastecimento[i] == "1":
            lista_atual += "0"
            print("Reabasteci o produto", produtos["ID"][i])
        else:
            lista_atual += lista_requests[i]

    lista_requests = lista_atual

if __name__ == '__main__':
    Cliente_Lojas()