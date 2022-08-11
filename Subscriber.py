from random import randint, random, randrange
import time
import paho.mqtt.client as mqtt

def on_subs(client, userdata, message_id, granted_qos):
    print("Subscrição:", str(message_id), str(granted_qos))

def on_mess(client, userdata, message):
    print("["+str(time.asctime(time.localtime()))+"]:", message.topic, str(message.qos), str(message.payload))

def subscriber_thread(id):
    
    quantidade_topics = randint(1, 10)
    client = mqtt.Client(id)
    client.on_subscribe = on_subs
    client.on_message = on_mess
    client.connect("broker.hivemq.com", 1883)
    
    for i in range(quantidade_topics):
    topico = 
    print("Você está acompanhando o tópico",topico,"\nPara fechar o tópico digite 'EOT'")
    while True:
        client.subscribe(topico, qos=1)
        
        client.loop_forever()
if __name__ == '__main__':
    subscriber_thread(1)