from abb import Robot
import cv2
import time

def tomar():
	
	CY_OFFSET = 0
	CX_OFFSET = 0

	camara_joints = [0.57 , -20.52 , 25.64 , 0 , 84.54 , 0.03]
	ORIENT = [0.00273 , -0.39556 , 0.91844 , -0.00115]

	Z = 15 # 131.2
	w = 400

	cam = cv2.VideoCapture(0)

	time.sleep(7)

	# Posiciones objetivo
	POSICION_HOME = [0, 0, 0, 0, 30, 0]  # Articulaciones en grados

	POSICION_CARTESIANA = [
	    [400, 0, 300],  # Coordenadas XYZ en mm
	    [1, 0, 0, 0]    # Cuaternión de orientación (w, x, y, z)
	]


	# Muevo a posición para tomar imagen
	print("Moviendo a posición cámara...")
	robot.set_joints(camara_joints)
	time.sleep(2)  # Pequeña pausa

	# Tomo imagen
	ret, frame = cam.read()
	cv2.imwrite("prueba", frame)

	cam.release()
	print("Conexión cerrada")