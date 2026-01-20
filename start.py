from paho.mqtt import client as mqtt_client
from secret import pc_topic, pri_key, screen_topic
import subprocess


broker = 'bemfa.com'
port = 9501
pc_topic = pc_topic
client_id = pri_key
lock_screen_command = '''powershell -WindowStyle Hidden -command "Add-Type -MemberDefinition '[DllImport(\\"user32.dll\\")] public static extern int SendMessage(int hWnd, int hMsg, int wParam, int lParam);' -Name Win32 -Namespace Windows; [Windows.Win32]::SendMessage(-1, 0x0112, 0xF170, 2)"'''


def connect_mqtt():
    # For paho-mqtt 2.0.0, you need to add the properties parameter.
    def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, client_id)

    # For paho-mqtt 2.0.0, you need to set callback_api_version.
    # client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)

    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        data = msg.payload.decode()
        print(f"Received `{data}` from `{msg.topic}` topic")
        if msg.topic == pc_topic:
            if data == 'off':
                subprocess.run("shutdown /s /t 1", shell=True, capture_output=True)
        elif msg.topic == screen_topic:
            if data == 'off':
                subprocess.run(lock_screen_command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


    client.subscribe(pc_topic)
    client.subscribe(screen_topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()



if __name__ == '__main__':
    run()


