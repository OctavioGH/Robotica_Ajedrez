import tomar_foto

import recortar_tablero
import procesar_tablero

import tomar_decision
import mover_robot

# Configuración de conexión (IP real del robot)
ROBOT_IP = '127.0.0.1'

JSON_1 = ""
JSON_2 = ""

IMG = ""
IMG_1 = ""
IMG_2 = ""

POS_INICIAL = ""

if __name__ == "__main__":

	print("Conectando...")

	with Robot(ip=ROBOT_IP) as robot:
		entrada = 'y'
		while(entrada == 'y'):
			entrada = input("Continuar? (y/n): ")
			if entrada == 'y'
			    tomar_foto.tomar(robot)
			    recortar_tablero.recortar(IMG)
			    procesar_tablero.procesar(IMG_1, IMG_2)
			    movimiento = tomar_decision.decidir(JSON_1, JSON_2)
			    mover_robot.mover(robot, movimiento, JSON_1, JSON_2)

	print("Conexión cerrada")