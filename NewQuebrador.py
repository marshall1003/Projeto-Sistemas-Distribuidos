import paho.mqtt.client as mqtt
 
def on_connect(client, userdata, flags, rcode):
    print("Conectado a", str(rcode))

def broker():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect("broker.hivemq.com", 1883)
    client.loop_forever()

if __name__ == '__main__':
   broker()        