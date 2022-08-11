from http import client
from pydoc import cli
#from telnetlib import IP
import time
from paho.mqtt import paho.mqtt.client as mqtt

AVAILABLE_PORTS = [7000, 7001, 7002, 7003]
IP_MAQUINA = '192.168.0.1'

def whoami():
    nome = input("Digite seu nome: ")
    return nome

def on_publish(client, message, message_id):
    print("message_id:", str(message_id))

def publisher_thread():
    client = mqtt.Client()
    client.on_publish = on_publish
    client.connect("broker.hivemq.com", 1883)
    client.loop_start()

    name = whoami()
    
    while True:

        topico = input("Digite o tópico que deseja publicar\nSe deseja sair, digite 'Bye'\n")

        print("Você está publicando no tópico",topico,"\nPara fechar o tópico digite 'EOT'\n")
        while True:
            mensagem = input()
            if(str.upper(mensagem) == "EOT"):
                print("Você saiu do tópico", topico)
                break
            rcode, message_id = client.publish(topico, mensagem)
            time.sleep(0.5)
            
if __name__ == '__main__':
    publisher_thread()         