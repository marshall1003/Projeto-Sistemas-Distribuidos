from random import randint, random, randrange
#import time
import paho.mqtt.client as mqtt
import pandas
#import json

LIST_CLASS = ["A", "B", "C"]
QTD_PRODUTOS = 200
QTD_LOJAS_MAX = 20
LIMITE_PROD_A = 100
LIMITE_PROD_B = 60
LIMITE_PROD_C = 20
MAX_CAPACITY = {"A":LIMITE_PROD_A*QTD_LOJAS_MAX, "B":LIMITE_PROD_B*QTD_LOJAS_MAX, "C":LIMITE_PROD_C*QTD_LOJAS_MAX}
DIA = 1
START_REQUEST = ["0" for i in range(QTD_PRODUTOS)]
SOLICITACAO_THRESHOLD = 0.25
DESNECESSARIO = "recebi produto que não deveria!"
WHOAMI_LOJA = 1
TOPICO_DEFAULT = "Loja - CDD"
lojas_conhecidas = []
produtos = {}
produtos["ID"] = {}
produtos["CLASS"] = {}
produtos["QTD"] = {}
dia = 0

def on_message(client, userdata, message):
    
    if(message.topic == TOPICO_DEFAULT):
        global lojas_conhecidas
        #if message.payload.decode() == "Oi Fredy!":
        if len(lojas_conhecidas) < QTD_LOJAS_MAX:
            new_loja = "Loja "+str(len(lojas_conhecidas)+1)+" - CDD"
            lojas_conhecidas.append(new_loja)
            client.publish("CDD - Loja",str(len(lojas_conhecidas)), qos = 1)
            client.subscribe(new_loja, qos = 1)
                
    if(len(lojas_conhecidas) > 0):
        for i in lojas_conhecidas:
            if(message.topic == i):
                dia = str.split(message.payload.decode(), " - ")[0]
                dia = int(str.split(dia, ":")[1])
                reposicoes = str.split(message.payload.decode(), " - ")[2]
                loja = str.split(i, " - ")[0]
                print("recebi pedido da", loja, " do dia", str(dia))
                reabastecer_cliente(client, reposicoes, loja)
    
def reabastecer_cliente(client, reabastecimento, loja):
    global lista_requests
    
    for i in range(QTD_PRODUTOS):
        if reabastecimento[i] == "1":
            produtos["QTD"][i] -= MAX_CAPACITY[produtos["CLASS"][i]]/QTD_LOJAS_MAX * (1-SOLICITACAO_THRESHOLD)
            print("Reabasteci o produto", produtos["ID"][i], "para a", loja)
    
    topico = "CDD -"+loja
    client.publish(topico,reabastecimento, qos = 1)

def CDD():
    today = 0
    lista_requests = START_REQUEST
    id_request = 1

    for i in range(1, QTD_PRODUTOS+1):
        with open("Produtos.csv", "r") as file:
            df = pandas.read_csv(file, sep=";")
            produtos["ID"][i] = i
            produtos["CLASS"][i] = (df.loc[df['Produto ID'] == produtos["ID"][i], ['Classe']]).values[0][0]
            produtos["QTD"][i] = MAX_CAPACITY[produtos["CLASS"][i]]

    client = mqtt.Client()
    client.on_message = on_message
    client.connect("broker.hivemq.com", 1883)
    client.subscribe (TOPICO_DEFAULT, qos=1)
    for i in lojas_conhecidas:
        client.subscribe (i, qos=1)
    client.loop_forever()


def valida_reposicao(produtos, lista_antiga):
    soma = START_REQUEST
    for i in range(QTD_PRODUTOS):
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



#def passa_tempo(produtos):
#    for prod_index in PROD_ID:
#        produtos["QTD"][prod_index] -= randint(0,5)
#        if produtos["QTD"][prod_index] < 0:
#            produtos["QTD"][prod_index] = 0
#    time.sleep(DIA)
#    return produtos

if __name__ == '__main__':
    CDD()