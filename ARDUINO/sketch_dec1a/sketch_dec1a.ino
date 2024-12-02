#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

// Configuración de la red Wi-Fi
const char* ssid = "...";
const char* password = "ZARZ00000";

// Crea una instancia del servidor web
ESP8266WebServer server(80);  // Puerto 80

// Definir los pines para el control del motor (usando un puente H L298N como ejemplo)
const int motor1_pin1 = 5;  // GPIO5 (IN1 Motor 1)
const int motor1_pin2 = 4;  // GPIO4 (IN2 Motor 1)
const int motor2_pin1 = 0;  // GPIO0 (IN3 Motor 2)
const int motor2_pin2 = 2;  // GPIO2 (IN4 Motor 2)

// Definir los pines PWM para control de velocidad
const int motor1_pwm = 14;  // GPIO14 (PWM Motor 1)
const int motor2_pwm = 12;  // GPIO12 (PWM Motor 2)

// Velocidad máxima del motor (PWM de 0 a 1023 para ESP8266)
const int max_speed = 200;  // Velocidad máxima
const int slow_speed = 70;  // Velocidad lenta para giros

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  // Esperar hasta que el ESP esté conectado a la red WiFi
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Conectando a WiFi...");
  }

  Serial.println("Conectado a WiFi");
  Serial.print("Dirección IP: ");
  Serial.println(WiFi.localIP());

  // Configuración de los pines de los motores como salida
  pinMode(motor1_pin1, OUTPUT);
  pinMode(motor1_pin2, OUTPUT);
  pinMode(motor2_pin1, OUTPUT);
  pinMode(motor2_pin2, OUTPUT);

  // Configuración de los pines PWM para control de velocidad
  pinMode(motor1_pwm, OUTPUT);
  pinMode(motor2_pwm, OUTPUT);

  // Configura las rutas para los comandos HTTP
  server.on("/adelante", HTTP_GET, []() {
    // Mueve los motores hacia adelante
    Serial.println("Movimiento hacia adelante");
    adelante();
    server.send(200, "text/plain", "Adelante");
  });

  server.on("/izquierda", HTTP_GET, []() {
    // Mueve el robot hacia la izquierda
    Serial.println("Movimiento hacia la izquierda");
    izquierda();
    server.send(200, "text/plain", "Izquierda");
  });

  server.on("/derecha", HTTP_GET, []() {
    // Mueve el robot hacia la derecha
    Serial.println("Movimiento hacia la derecha");
    derecha();
    server.send(200, "text/plain", "Derecha");
  });

  server.on("/centrado", HTTP_GET, []() {
    // Detiene los motores para centrar el robot
    Serial.println("Centrado");
    detener();
    server.send(200, "text/plain", "Centrado");
  });

  server.on("/no_detectado", HTTP_GET, []() {
    // Simplemente, no hacer nada y devolver una respuesta
    Serial.println("No detectado - No se realiza ninguna acción");
    server.send(200, "text/plain", "No detectado - Sin acción realizada");
  });


  server.on("/velocidad", HTTP_GET, []() {
    String speedStr = server.arg("value");
    int speed = speedStr.toInt();
    if (speed >= 0 && speed <= 1023) {
      setSpeed(speed);  // Ajustar la velocidad
      server.send(200, "text/plain", "Velocidad ajustada");
    } else {
      server.send(400, "text/plain", "Valor de velocidad no válido");
    }
  });

  // Comienza a escuchar las peticiones HTTP
  server.begin();
}

void loop() {
  server.handleClient();  // Maneja las solicitudes entrantes
}

// Funciones para controlar los motores

void adelante() {
  digitalWrite(motor1_pin1, HIGH);
  digitalWrite(motor1_pin2, LOW);
  digitalWrite(motor2_pin1, HIGH);
  digitalWrite(motor2_pin2, LOW);
  analogWrite(motor1_pwm, max_speed);
  analogWrite(motor2_pwm, max_speed);
}

void izquierda() {
  digitalWrite(motor1_pin1, HIGH);
  digitalWrite(motor1_pin2, LOW);
  digitalWrite(motor2_pin1, LOW);
  digitalWrite(motor2_pin2, HIGH);
  analogWrite(motor1_pwm, max_speed);
  analogWrite(motor2_pwm, max_speed);
}

void derecha() {
  digitalWrite(motor1_pin1, LOW);
  digitalWrite(motor1_pin2, HIGH);
  digitalWrite(motor2_pin1, HIGH);
  digitalWrite(motor2_pin2, LOW);
  analogWrite(motor1_pwm, max_speed);
  analogWrite(motor2_pwm, max_speed);
}

void detener() {
  digitalWrite(motor1_pin1, LOW);
  digitalWrite(motor1_pin2, LOW);
  digitalWrite(motor2_pin1, LOW);
  digitalWrite(motor2_pin2, LOW);
}

void retroceder() {
  digitalWrite(motor1_pin1, LOW);
  digitalWrite(motor1_pin2, HIGH);
  digitalWrite(motor2_pin1, LOW);
  digitalWrite(motor2_pin2, HIGH);
  analogWrite(motor1_pwm, slow_speed);  // Retroceder rápido
  analogWrite(motor2_pwm, slow_speed);
}

void giro_lento() {
  digitalWrite(motor1_pin1, HIGH);
  digitalWrite(motor1_pin2, LOW);
  digitalWrite(motor2_pin1, LOW);
  digitalWrite(motor2_pin2, HIGH);
  analogWrite(motor1_pwm, slow_speed);  // Velocidad baja para giros lentos
  analogWrite(motor2_pwm, slow_speed);
}

void setSpeed(int speed) {
  analogWrite(motor1_pwm, speed);
  analogWrite(motor2_pwm, speed);
}
