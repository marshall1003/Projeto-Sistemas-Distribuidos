from posixpath import split
from socket import socketpair
import zmq
import time
import paho.mqtt.client as mqtt

def on_subs(client, userdata, message_id, granted_qos):
    print("Subscrição:", str(message_id), str(granted_qos))

def on_mess(client, userdata, message):
    print("["+str(time.asctime(time.localtime()))+"]:", message.topic, str(message.qos), str(message.payload))

def subscriber_thread():
    
    client = mqtt.Client()
    client.on_subscribe = on_subs
    client.on_message = on_mess
    client.connect("broker.hivemq.com", 1883)
    
    topico = input("Qual tópico gostaria de conversar?\n")
    print("Você está acompanhando o tópico",topico,"\nPara fechar o tópico digite 'EOT'")
    while True:
        client.subscribe(topico, qos=1)
        
        client.loop_forever()
if __name__ == '__main__':
    subscriber_thread()