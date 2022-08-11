import paho.mqtt.client as mqtt
import Subscriber


TESTE_SUBS = 5

def main ():

    for i in range(TESTE_SUBS):
        Subscriber.subscriber_thread(i)
        
