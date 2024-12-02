import cv2
import numpy as np

# Crear una imagen en blanco (300x300 píxeles, 3 canales de color BGR)
image = np.ones((300, 300, 3), dtype=np.uint8) * 255  # Imagen blanca

# Dibujar un cuadrado con borde azul (en BGR) y relleno blanco
# Borde azul: (255, 0, 0) y relleno blanco: (255, 255, 255)
cv2.rectangle(image, (75, 75), (225, 225), (255, 0, 0), 10)  # Borde azul
cv2.rectangle(image, (80, 80), (220, 220), (255, 255, 255), -1)  # Relleno blanco

# Mostrar la imagen generada
cv2.imshow('Cuadrado Azul con Blanco', image)

# Guardar la imagen
cv2.imwrite('cuadrado_azul_blanco.png', image)

# Esperar a que el usuario presione una tecla para cerrar
cv2.waitKey(0)
cv2.destroyAllWindows()
