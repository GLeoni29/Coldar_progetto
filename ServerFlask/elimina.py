''' ------ IMPORT ------ '''
from flask import Flask, render_template, request
from google.cloud import firestore
import time
from datetime import datetime

''' ------ AVVIO ISTANZA FLASK ------ '''
app = Flask(__name__)

''' ------ APERTURA CONNESSIONE FIRESTORE ------ '''
db = 'coldar'
coll = 'Arduino1'
db = firestore.Client.from_service_account_json('credentials.json', database=db)

''' ------ VARIABILI GLOBALI ------ '''
sportello_aperto_da = None  # Variabile per tenere traccia del tempo di apertura dello sportello
stato_allarme = False  # variabile per segnalare che il sistema è in stato di allarme
lista_messaggi = []  # lista per inviare comandi ad arduino
comando = False

''' ------ RECUPERO DATI DA ARDUINO ------ '''


def controlla_condizioni(temperatura, sportello_aperto):
    global lista_messaggi
    global sportello_aperto_da
    global stato_allarme
    global comando

    # Controllo temperatura prioritario
    if temperatura < 10 or temperatura > 25:  # se temperatura fuori range
        allarme_temperatura = True

    else:  # se temperaura ok, controllo stato sportello
        allarme_temperatura = False

        if sportello_aperto == 1:  # 1=sportello aperto, 0=sportello chiuso
            if sportello_aperto_da is None:
                sportello_aperto_da = time.time()
                allarme_sportello = False
            elif time.time() - sportello_aperto_da > 30:
                allarme_sportello = True
            else:
                allarme_sportello = False
        else:
            sportello_aperto_da = None
            allarme_sportello = False

    if (allarme_temperatura or allarme_sportello) and not stato_allarme:
        stato_allarme = True
        lista_messaggi.append("LEDandBUZZER_ON")
        comando = True
    elif (not allarme_temperatura and not allarme_sportello) and stato_allarme:
        stato_allarme = False
        lista_messaggi.append("LEDandBUZZER_OFF")
        comando = True
    elif (allarme_temperatura or allarme_sportello) and stato_allarme:
        pass  # mantieni lo stato di allarme
    elif (not allarme_temperatura and not allarme_sportello) and not stato_allarme:
        pass  # mantieni lo stato di non allarme


@app.route('/dati', methods=['POST'])
def ricevi_dati():
    try:
        # Ricevi i dati dal client_sensor
        dataora = str(request.form.get('dataora'))
        temperatura = float(request.form.get('temperatura'))
        sportello = int(request.form.get('sportello'))
        # !!!!!!

        # Controlla le condizioni temperatura e sportello
        controlla_condizioni(float(temperatura), int(sportello))

        # Salva i dati su Firestore
        doc_ref = db.collection(coll).document()  # id di default
        doc_ref.set({"dataora": dataora, "temperatura": temperatura, "sportello": sportello})  # imposto documeto
        print(f"Dati inseriri: [dataora: {dataora}, temperatura: {temperatura}, sportello: {sportello}]")

        global comando
        ## ## ## ## ## ## ##
        # if len(lista_messaggi) > 0:
        if comando:
            comando = False
            messaggio = lista_messaggi[0]
            lista_messaggi.pop()
        else:
            messaggio = ''

        return messaggio, 200  # "Dati salvati", 200

    except Exception as e:
        print(f"Errore: {e}")
        return "Errore interno del server", 500


''' ------ HOME ------ '''


@app.route('/')
def home():
    return render_template('index.html')


''' ----- AREA TEST ----- '''


@app.route('/area_test')
def area_test():
    return render_template('area_test.html')


@app.route('/test_led_on')
def test_led_on():
    global lista_messaggi
    global comando
    lista_messaggi.append("LED_ON")
    comando = True
    return render_template('area_test.html')


@app.route('/test_led_off')
def test_led_off():
    global lista_messaggi
    global comando
    lista_messaggi.append("LED_OFF")
    comando = True
    return render_template('area_test.html')


@app.route('/test_buzzer_on')
def test_buzzer_on():
    global lista_messaggi
    global comando
    lista_messaggi.append("BUZZER_ON")
    comando = True
    return render_template('area_test.html')


@app.route('/test_buzzer_off')
def test_buzzer_off():
    global lista_messaggi
    global comando
    lista_messaggi.append("BUZZER_OFF")
    comando = True
    return render_template('area_test.html')


@app.route('/test_led_e_buzzer_on')
def test_led_e_buzzer_on():
    global lista_messaggi
    global comando
    lista_messaggi.append("LEDandBUZZER_ON")
    comando = True
    return render_template('area_test.html')


@app.route('/test_led_e_buzzer_off')
def test_led_e_buzzer_off():
    global lista_messaggi
    global comando
    lista_messaggi.append("LEDandBUZZER_OFF")
    comando = True
    return render_template('area_test.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
