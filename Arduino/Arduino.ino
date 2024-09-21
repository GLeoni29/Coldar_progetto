#include <DHT.h>

// Definizione dei pin
#define DHTPIN 4          // Pin a cui è collegato il sensore DHT
#define SPORTELLOPIN 2    // Pin a cui è collegato il pulsante dello sportello
#define LEDPIN 12          // Pin a cui è collegato il LED
#define CICALINOPIN 9     // Pin a cui è collegato il cicalino

// Tipo di sensore DHT
#define DHTTYPE DHT11

// Inizializzazione del sensore DHT
DHT dht(DHTPIN, DHTTYPE);


unsigned long previousMillis = 0;  // Memorizza il tempo della precedente trasmissione
const long interval = 1000;        // Intervallo di 1 secondo


void setup() {
  // Imposta i pin di input/output
  pinMode(SPORTELLOPIN, INPUT);  // Pull-up interno per il pulsante
  pinMode(LEDPIN, OUTPUT);
  pinMode(CICALINOPIN, OUTPUT);

  // Inizia la comunicazione seriale
  Serial.begin(9600);

  // Inizia il sensore DHT
  dht.begin();

  // Assicura che il LED e il cicalino siano spenti all'avvio
  digitalWrite(LEDPIN, LOW);
  digitalWrite(CICALINOPIN, LOW);
}


void loop() {
  // Controlla il tempo trascorso
  unsigned long currentMillis = millis();

  // Se è trascorso un secondo dall'ultimo invio dati
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    // Legge la temperatura e lo stato dello sportello
    float temperatura = dht.readTemperature();
    bool sportello = digitalRead(SPORTELLOPIN) == LOW;  // LOW se aperto

    // Costruisce il messaggio da inviare
    String output = String(temperatura) + "," + String(sportello ? 0 : 1); //0:chiuso 1:aperto
    Serial.println(output);
  }

  // Controlla se ci sono comandi in arrivo dal server
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == 'O') {
      digitalWrite(LEDPIN, HIGH);  // Accende il LED
      digitalWrite(CICALINOPIN, HIGH);  // Accende il cicalino
    } else if (command == 'F') {
      digitalWrite(LEDPIN, LOW);  // Spegne il LED
      digitalWrite(CICALINOPIN, LOW);  // Spegne il cicalino
    } else if (command == 'L') {
      digitalWrite(LEDPIN, HIGH);  // Accende il LED
    } else if (command == 'M') {
      digitalWrite(LEDPIN, LOW);  // Spegne il LED
    } else if (command == 'B') {
      digitalWrite(CICALINOPIN, HIGH);  // Accende il cicalino
    } else if (command == 'C') {
      digitalWrite(CICALINOPIN, LOW);  // Spegne il cicalino
    }
  }
}

// void loop() {
//   // Legge la temperatura e lo stato dello sportello
//   float temperatura = dht.readTemperature();
//   //float temperatura = 25.5;
//   bool sportello = digitalRead(SPORTELLOPIN) == LOW;  // LOW se aperto

//   // Controlla se la lettura è valida
//   //if (isnan(temperatura)) {
//   //  Serial.println("Errore nella lettura della temperatura!");
//   //  return;
//   //}

//   // Invia i dati via seriale (Formato: DataOra,Temperatura,Sportello)
//   String dataOra = ""; // Puoi usare un modulo RTC per ottenere la data e l'ora esatta
//   //String output = dataOra + "," + String(temperatura) + "," + String(sportello_aperto ? 1 : 0);
//   //Serial.println(sportello);
//   String output = String(temperatura) + "," + String(sportello ? 0 : 1) ; //0:chiuso 1:aperto
//   Serial.println(output);

//   // Controlla se ci sono comandi in arrivo dal server
//   if (Serial.available() > 0) {
//     char command = Serial.read();
//     if (command == 'O') {
//       digitalWrite(LEDPIN, HIGH);  // Accende il LED
//       digitalWrite(CICALINOPIN, HIGH);  // Accende il cicalino
//     } else if (command == 'F') {
//       digitalWrite(LEDPIN, LOW);  // Spegne il LED
//       digitalWrite(CICALINOPIN, LOW);  // Spegne il cicalino
//     } else if (command == 'L') {
//       digitalWrite(LEDPIN, HIGH);  // Accende il LED
//     } else if (command == 'M') {
//       digitalWrite(LEDPIN, LOW);  // Spegne il LED
//     } else if (command == 'B') {
//       digitalWrite(CICALINOPIN, HIGH);  // Accende il cicalino
//     } else if (command == 'C') {
//       digitalWrite(CICALINOPIN, LOW);  // Spegne il cicalino
//     }
//     else {
//       //
//     }
//   }

//   // Attendi 1 secondo prima di effettuare una nuova lettura
//   delay(1000);
// }
