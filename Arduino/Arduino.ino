#include <DHT.h>

// Definizione dei pin
#define DHTPIN 4          // Pin a cui è collegato il sensore DHT
#define SPORTELLOPIN 2    // Pin a cui è collegato il pulsante dello sportello
#define LEDPIN 12          // Pin a cui è collegato il LED
#define CICALINOPIN 9     // Pin a cui è collegato il cicalino

#define DHTTYPE DHT11

// Inizializzazione del sensore DHT
DHT dht(DHTPIN, DHTTYPE);

unsigned long previousMillis = 0;  // Memorizza il tempo della precedente trasmissione
const long interval = 2000;        // Intervallo di 1 secondo


void setup() {
  // Imposta i pin di input/output
  pinMode(SPORTELLOPIN, INPUT);
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
  // Ogni secondo registra temperatura e stato sportello del sistema
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    float temperatura = dht.readTemperature();
    bool sportello = digitalRead(SPORTELLOPIN) == LOW;  // LOW = aperto

    String output = String(temperatura) + "," + String(sportello ? 0 : 1); // 0 = chiuso; 1 = aperto
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
