import cv2
import numpy as np
import json
import time
import os

IP_ROBOT = '127.0.0.1'  # IP del robot real o simulado
NOMBRE_IMAGEN = "imagenes/foto_tablerocnpiezas.jpg"
ARCHIVO_PLANTILLA = "plantilla_tablero.json"

TAMANIO_TABLERO = 800  # tamaño en píxeles de la imagen rectificada
TAMANIO_TABLERO_CM = 50  # tamaño en centímetros del tablero

#piezas = ['NADA': 0, 'PEON' : 1 , 'CABALLO': 2, 'TORRE' : 3, 'ALFIL' : 4, 'REY' : 5, 'REINA' : 6]

def detectar_esquinas_tablero(img):
    """
    Detecta las 4 esquinas del tablero de ajedrez.
    #Esto es una versión simplificada: en producción se puede mejorar con detección de líneas o aruco.
    Retorna las 4 esquinas ordenadas (tl, tr, br, bl)
    """
    print("[INFO] Procesando contornos para detectar el tablero...")

    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gris, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    # Mostrar bordes detectados
    cv2.imshow("Bordes detectados (Canny)", edges)
    cv2.waitKey(0)

    contornos, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    img_contornos = img.copy()
    cv2.drawContours(img_contornos, contornos, -1, (0, 255, 0), 2)
    cv2.imshow("Contornos detectados", img_contornos)
    cv2.waitKey(0)

    contorno_max = max(contornos, key=cv2.contourArea)
    epsilon = 0.02 * cv2.arcLength(contorno_max, True)
    approx = cv2.approxPolyDP(contorno_max, epsilon, True)

    if len(approx) != 4:
        raise Exception("[ERROR] No se detectaron 4 esquinas. Ajustar iluminación o filtros.")

    img_esquinas = img.copy()
    for punto in approx:
        cv2.circle(img_esquinas, tuple(punto[0]), 10, (0, 0, 255), -1)

    cv2.imshow("Esquinas detectadas", img_esquinas)
    cv2.waitKey(0)

    esquinas = [p[0] for p in approx]

    # Ordenar esquinas: top-left, top-right, bottom-right, bottom-left
    esquinas = sorted(esquinas, key=lambda x: x[1])
    top = sorted(esquinas[:2], key=lambda x: x[0])
    bottom = sorted(esquinas[2:], key=lambda x: x[0])

    return np.float32([top[0], top[1], bottom[1], bottom[0]])

def aplicar_homografia(img, esquinas_img):
    print("[INFO] Calculando homografía y rectificando imagen...")
    esquinas_ideal = np.float32([[0, 0], [TAMANIO_TABLERO, 0],
                                 [TAMANIO_TABLERO, TAMANIO_TABLERO], [0, TAMANIO_TABLERO]])

    H, _ = cv2.findHomography(esquinas_img, esquinas_ideal)
    img_warped = cv2.warpPerspective(img, H, (TAMANIO_TABLERO, TAMANIO_TABLERO))

        # Mostrar imagen rectificada
    cv2.imshow("Imagen rectificada (homografía)", img_warped)
    cv2.waitKey(0)

    return img_warped

def generar_plantilla_rectificada(img_rectificada):
    print("[INFO] Generando plantilla a partir de imagen rectificada...")

    casilla_w = TAMANIO_TABLERO // 8
    casilla_h = TAMANIO_TABLERO // 8
    columnas = 'abcdefgh'
    filas = '12345678'

    plantilla = {}

    for i in range(8):
        for j in range(8):
            cx = j * casilla_w + casilla_w // 2
            cy = i * casilla_h + casilla_h // 2
            casilla = columnas[j] + filas[7 - i]
            plantilla[casilla] = (cx, cy)

            # Dibujar en imagen para verificación
            cv2.circle(img_rectificada, (cx, cy), 5, (0, 255, 0), -1)
            cv2.putText(img_rectificada, casilla, (cx - 15, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # Mostrar imagen con plantilla
    cv2.imshow("Casillas con centros corregidos", img_rectificada)
    cv2.waitKey(0)

    return plantilla, img_rectificada

## Programa para identificar el tablero. Todo nosotros
imagen = cv2.imread(NOMBRE_IMAGEN)

# 1. Detectar esquinas del tablero
esquinas_detectadas = detectar_esquinas_tablero(imagen)

# 2. Calcular homografía y rectificar
img_rectificada = aplicar_homografia(imagen, esquinas_detectadas)

# 3. Generar plantilla con coordenadas del centro de cada casilla
plantilla, img_anotada = generar_plantilla_rectificada(img_rectificada)

# 4. Mostrar imagen resultante
cv2.destroyAllWindows()
cv2.imshow("Tablero rectificado y etiquetado", img_anotada)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 5. Guardar plantilla
with open(ARCHIVO_PLANTILLA, "w") as f:
    json.dump(plantilla, f, indent=4)

print(f"[INFO] Plantilla guardada en {ARCHIVO_PLANTILLA}")
print("[✔️] Preparación completada. Listo para comenzar la partida.")

