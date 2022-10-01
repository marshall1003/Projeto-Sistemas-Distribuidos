from random import randint, random, randrange
import time
import paho.mqtt.client as mqtt


LIST_CLASS = ["A", "B", "C"]
MAX_CAPACITY = {"A":100, "B":60, "C":20}
QTD_PRODUTOS = 200
DIA = 1
PROD_ID = [i+1 for i in range(10)]
START_REQUEST = ["0" for i in range(QTD_PRODUTOS)]
SOLICITACAO_THRESHOLD = 0.25
DESNECESSARIO = "recebi produto que não deveria!"

#def on_publish(client, userdata, message_id):
#    print("", client, "message_id:", str(message_id))

def Cliente_Lojas():
    today = 0
    lista_requests = START_REQUEST
    id_request = 1
    topico_pedir = "Loja 1 - CDD"
    topico_receber = "CDD - Loja 1"#+str(1)#str(randint(1,10))
    produtos = {}
    produtos["ID"] = {}
    produtos["CLASS"] = {}
    produtos["QTD"] = {}

    client = mqtt.Client()
    client.connect("broker.hivemq.com", 1883)
    client.subscribe (topico_receber, qos=1)
    client.loop_start()

    for i in PROD_ID:
        produtos["ID"][i] = randint(1,QTD_PRODUTOS)
        produtos["CLASS"][i] = LIST_CLASS[randrange(0,3)]
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

def reabastecer(produtos, reabastecimento, lista_antiga):
    for i in range(QTD_PRODUTOS):
        if reabastecimento[i] == "1":
            produtos["QTD"][i] += MAX_CAPACITY[produtos["CLASS"][i]] * (1-SOLICITACAO_THRESHOLD)
    lista_atual = ""
    for i in range(len(reabastecimento)):
        if lista_antiga[i] == "0" and reabastecimento[i] == "1":
            raise DESNECESSARIO
        if lista_antiga[i] == "1" and reabastecimento[i] == "1":
            lista_atual += "0"
        else:
            lista_atual += lista_antiga[i]

    return lista_atual

if __name__ == '__main__':
    Cliente_Lojas()