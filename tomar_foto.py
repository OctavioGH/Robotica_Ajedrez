from abb import Robot
import cv2
import time

def tomar():
	
	CY_OFFSET = 0
	CX_OFFSET = 0
	CZ_OFFSET = 10

	camara_joints = [0.57 , -20.52 , 25.64 , 0 , 84.54 , 0.03]

	cam = cv2.VideoCapture(0)

	time.sleep(7)

	# Muevo a posición para tomar imagen
	print("Moviendo a posición cámara...")
	robot.moveRel(CX_OFFSET,CY_OFFSET,CZ_OFFSET)
	robot.set_joints(camara_joints)
	time.sleep(2)  # Pequeña pausa

	# Tomo imagen
	ret, frame = cam.read()
	cv2.imwrite("prueba", frame)

	cam.release()
	print("Conexión cerrada")