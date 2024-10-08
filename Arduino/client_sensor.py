''' ------ IMPORT ------ '''
import serial
import requests
from datetime import datetime


''' ------ CONFIGURA CONNESSIONE SERIALE ------ '''
arduino = serial.Serial("COM5", 9600)


''' ------ URL BASE ------ '''
#base_url = 'http://127.0.0.1:80'
base_url = 'https://coldar-436310.ew.r.appspot.com'

i = 0
''' ------ MAIN ------ '''
while True:
    if arduino.in_waiting > 0:
        data = arduino.readline().decode('utf-8').strip()
        if len(data) == 1:
            continue
        else:
            temperatura, sportello = data.split(',')
            timestamp = datetime.now()

            rilevazione = {
                'dataora': timestamp,
                'temperatura': float(temperatura),
                'sportello': int(sportello)
            }
            print("rilevazione: ", rilevazione)
            response = requests.post(f'{base_url}/dati', rilevazione) #timeout=100)

            i +=1
            if response.status_code == 200:
                message = response.text.strip()
                print('messaggio',i,': ', message)

                if message == "LEDandBUZZER_ON":
                    arduino.write(b"O")
                elif message == "LEDandBUZZER_OFF":
                    arduino.write(b"F")
                elif message == "LED_ON":
                    arduino.write(b"L")
                elif message == "LED_OFF":
                    arduino.write(b"M")
                elif message == "BUZZER_ON":
                    arduino.write(b"B")
                elif message == "BUZZER_OFF":
                    arduino.write(b"C")