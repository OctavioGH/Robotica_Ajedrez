import tomar_foto
import recortar_tablero
import procesar_tablero
import tomar_decision
import mover_robot

if __name__ == "__main__":

	# Configuración de conexión (usar IP real del robot)
	ROBOT_IP = '127.0.0.1'

	print("Conectando...")

	with Robot(ip=ROBOT_IP) as robot:
	    tomar_foto.tomar()
	    recortar_tablero.recortar()
	    procesar_tablero.procesar()
	    tomar_decision.decidir()
	    mover_robot.mover()

	print("Conexión cerrada")