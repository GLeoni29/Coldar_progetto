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
    elif (not allarme_temperatura and not allarme_sportello) and stato_allarme:
        stato_allarme = False
        lista_messaggi.append("LEDandBUZZER_OFF")
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
        #if len(lista_messaggi) > 0:
        if comando:
            comando = False
            messaggio = lista_messaggi[0]
            lista_messaggi.pop()

        else:
            messaggio = ''
        return messaggio, 200 #"Dati salvati", 200

    except Exception as e:
        print(f"Errore: {e}")
        return "Errore interno del server", 500


''' ------ HOME ------ '''
@app.route('/')
def home():
    return render_template('index.html')


''' ------ AREA MONITOR ------ '''
@app.route('/area_monitor')
def area_monitor():
   global sportello_aperto_da

   # Ottieni l'ultima rilevazione inserita nel database
   collection_ref = db.collection(coll)
   docs = collection_ref.order_by('dataora', direction=firestore.Query.DESCENDING).limit(1).stream()

   row = None
   for doc in docs:
       row = doc.to_dict()
       break  # Prendi solo il primo documento

   if row is None:
       print("Nessun dato disponibile.")
       return render_template('area_monitor.html', stato="ERRORE - Nessun dato", temperatura=None, sportello=None,
                              orario=None)

   # Imposta messaggio di stato (area monitor)
   stato = "ok con sportello chiuso"
   if float(row['temperatura']) < 10 or float(row['temperatura']) > 25:
       # if float(row['temperatura']) < 2 or float(row['temperatura']) > 8: # Range GDO
       stato = "allarme temperatura"
   elif int(row['sportello']) == 1:
       if sportello_aperto_da is None:
           sportello_aperto_da = time.time()
       tempo_apertura = time.time() - sportello_aperto_da
       if tempo_apertura > 30:
           stato = "sportello aperto da più di 30 sec"
       else:
           stato = f"ok con sportello aperto da {int(tempo_apertura)} secondi"
   else:
       sportello_aperto_da = None

   # Ottieni orario rilevazione
   dataora = datetime.strptime(row['dataora'], '%Y-%m-%d %H:%M:%S.%f')
   orario = dataora.strftime('%H:%M:%S')

   return render_template('area_monitor.html', stato=stato, temperatura=row['temperatura'], sportello=row['sportello'],
                          orario=orario)


''' ------ AREA ANALISI ------ '''
@app.route('/area_analisi')
def area_analisi():
    # Prepara strutture dati per creare grafici
    dati_temperatura = [['DataOra', 'Temperatura']]
    dati_sportello = [['DataOra', 'Sportello']]

    # Ottieni tutti i dati relativi alla data odierna
    oggi = datetime.now().date()
    dataora = str(datetime(oggi.year, oggi.month, oggi.day))

    collection_ref = db.collection(coll)
    docs = collection_ref.where('dataora', '>=', dataora).order_by('dataora',
                                                                   direction=firestore.Query.ASCENDING).stream()
    for doc in docs:
        row = doc.to_dict()
        dataora = datetime.strptime(row['dataora'], '%Y-%m-%d %H:%M:%S.%f')
        dataora = dataora.strftime('%H:%M:%S')
        dati_temperatura.append([dataora, float(row['temperatura'])])
        dati_sportello.append([dataora, int(row['sportello'])])
    # print("dati temperatura: ", dati_temperatura)
    # print("dati sportello: ", dati_sportello)

    return render_template('area_analisi.html', dati_temperatura=dati_temperatura, dati_sportello=dati_sportello)

@app.route('/filtra_dati', methods=['POST'])
def filtra_dati():
    # Recupera i dati dalla form
    data = request.form.get('data')
    orario_inizio = request.form.get('orario_inizio')
    orario_fine = request.form.get('orario_fine')

    # Prepara strutture dati per creare grafici
    dati_temperatura = [['DataOra', 'Temperatura']]
    dati_sportello = [['DataOra', 'Sportello']]

    # Estrai i dati del periodo selezionato
    collection_ref = db.collection(coll)

    if data == "":  # se data omessa considerare quella odierna
        data = str(datetime.now().date())

    dataora_inizio = str(datetime.strptime(f"{data} {orario_inizio}:00.0", '%Y-%m-%d %H:%M:%S.%f'))
    dataora_fine = str(datetime.strptime(f"{data} {orario_fine}:59.0", '%Y-%m-%d %H:%M:%S.%f'))

    docs = (collection_ref.where('dataora', '>=', dataora_inizio) \
            .where('dataora', '<=', dataora_fine) \
            .order_by('dataora', direction=firestore.Query.ASCENDING)).stream()

    docs_list = list(docs)
    if not docs_list:
        # print("Nessun documento trovato.")
        dati_temperatura.append(["", 0])
        dati_sportello.append(["", 0.5])
        messaggio = "errore"

        return render_template('area_analisi.html', dati_temperatura=dati_temperatura, dati_sportello=dati_sportello,
                               messaggio=messaggio)
    else:
        for doc in docs_list:
            row = doc.to_dict()
            dataora = datetime.strptime(row['dataora'], '%Y-%m-%d %H:%M:%S.%f')
            dataora = dataora.strftime('%H:%M:%S')
            dati_temperatura.append([dataora, float(row['temperatura'])])
            dati_sportello.append([dataora, int(row['sportello'])])
        data = data.split('-')
        messaggio = f"Dati riferiti al {data[2]}-{data[1]}-{data[0]} {orario_inizio}-{orario_fine}"

        return render_template('area_analisi.html', dati_temperatura=dati_temperatura, dati_sportello=dati_sportello,
                               messaggio=messaggio)


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

'''def check_messaggio(lista_messaggi):
    if len(lista_messaggi) == 1:
        messaggio = lista_messaggi[0]
        lista_messaggi.pop()
    else:
        messaggio = ""
    return messaggio

@app.route('/invia_messaggio', methods=['POST'])
def invia_messaggio():
    messaggio = check_messaggio(lista_messaggi)
    return messaggio'''

'''@app.route('/invia_messaggio', methods=['POST'])
def invia_messaggio():
    global lista_messaggi

    if len(lista_messaggi) > 0:
        messaggio = lista_messaggi[0]
        lista_messaggi.pop()
    else:
        messaggio = ""

    return messaggio'''






if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)