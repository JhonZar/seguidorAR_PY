import cv2
import numpy as np
import requests
import time

# Dirección IP del ESP8266 (ajusta la IP según tu red local)
esp_ip = "http://192.168.100.19"  # Cambia esto por la IP de tu ESP8266

# Función para enviar comandos al ESP8266
def send_command(command):
    url = f"{esp_ip}/{command}"
    try:
        response = requests.get(url)
        print(f"Comando enviado: {command}")
        print(f"Respuesta del ESP8266: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar el comando: {e}")

# Iniciar la cámara
cap = cv2.VideoCapture(1)

# Configurar una resolución más baja para mejorar la velocidad de procesamiento
cap.set(3, 320)  # Ancho más bajo (cambiar de 640 a 320)
cap.set(4, 240)  # Alto más bajo (cambiar de 480 a 240)

# Variable para controlar el tiempo entre envíos de comandos
last_command_time = time.time()

# Umbral de tiempo entre comandos (en segundos)
command_delay = 0.5  # Evita enviar comandos demasiado rápido

# Número de fotogramas que se van a omitir para reducir el uso de CPU
frame_skip = 5  # Solo procesar un fotograma cada 5
frame_count = 0

while True:
    # Captura un fotograma de la cámara
    ret, frame = cap.read()

    if not ret:
        print("Error al acceder a la cámara")
        break

    # Solo procesar cada 'frame_skip' fotogramas
    frame_count += 1
    if frame_count % frame_skip != 0:
        continue  # Saltar este fotograma y continuar con el siguiente

    # Convertir la imagen a espacio de color HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Definir un rango más amplio para el color azul en el espacio HSV
    lower_blue = np.array([90, 50, 50])  # Valores mínimos para azul
    upper_blue = np.array([150, 255, 255])  # Valores máximos para azul

    # Crear una máscara para los píxeles que estén dentro del rango del color azul
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Convertir la imagen a escala de grises para detectar el borde blanco
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Umbralizar la imagen en blanco y negro
    _, white_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    # Combinar las máscaras para detectar el borde azul con el interior blanco
    combined_mask = cv2.bitwise_and(blue_mask, white_mask)

    # Encontrar los contornos en la imagen combinada
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Inicializar variable para el contorno del cuadrado
    square_contour = None

    # Recorrer los contornos encontrados
    for contour in contours:
        # Aproximar el contorno a una forma poligonal
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Si el contorno tiene 4 puntos, es un cuadrado
        if len(approx) == 4:
            square_contour = approx
            break

    # Si se ha encontrado un cuadrado
    if square_contour is not None:
        # Dibujar el contorno del cuadrado con borde azul
        cv2.drawContours(frame, [square_contour], -1, (255, 0, 0), 2)  # Azul

        # Calcular el centro del cuadrado
        M = cv2.moments(square_contour)
        if M["m00"] != 0:  # Verificar que m00 no sea cero
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # Dibujar el centro del cuadrado con color rojo
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)  # Rojo

            # Análisis de la posición del centro
            frame_width = frame.shape[1]
            frame_height = frame.shape[0]

            # Decisiones para el movimiento del vehículo
            current_time = time.time()
            if abs(cx - frame_width // 2) < 50 and cy > frame_height // 3:
                if current_time - last_command_time > command_delay:  # Solo enviar comando si ha pasado el tiempo necesario
                    print("Adelante")  # El cuadrado está centrado y cerca
                    send_command("adelante")  # Enviar comando al ESP8266
                    last_command_time = current_time
            elif cx < frame_width // 3:
                if current_time - last_command_time > command_delay:
                    print("Izquierda")  # El cuadrado está a la izquierda
                    send_command("izquierda")  # Enviar comando al ESP8266
                    last_command_time = current_time
            elif cx > 2 * frame_width // 3:
                if current_time - last_command_time > command_delay:
                    print("Derecha")  # El cuadrado está a la derecha
                    send_command("derecha")  # Enviar comando al ESP8266
                    last_command_time = current_time
            else:
                if current_time - last_command_time > command_delay:
                    print("Centrado")  # El cuadrado está centrado
                    send_command("centrado")  # Enviar comando al ESP8266
                    last_command_time = current_time
    else:
        # Si no se detecta el cuadrado, enviar un comando "no detectado" o cualquier otro
        print("No se detectó el cuadrado")
        send_command("no_detectado")  # Comando cuando no se detecta el cuadrado

    # Mostrar la máscara combinada en blanco y negro para verificar qué se está detectando
    # Solo mostrar si es necesario para mejorar el rendimiento
    # cv2.imshow('Máscara Combinada (Blanco y Negro)', combined_mask) 

    # Mostrar la imagen original con los contornos y el centro del cuadrado
    cv2.imshow('Reconocimiento de Cuadrado Azul con Blanco', frame)

    # Salir si se presiona 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()
