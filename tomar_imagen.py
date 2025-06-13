from abb import Robot
import cv2
import time

# Configuración de conexión (usar IP real del robot)
ROBOT_IP = '127.0.0.1'

CY_OFFSET = 0
CX_OFFSET = 0

camara_joints = [0.57 , -20.52 , 25.64 , 0 , 84.54 , 0.03]
ORIENT = [0.00273 , -0.39556 , 0.91844 , -0.00115]

Z = 15 # 131.2
w = 400

place_red = [0, 0, 0, 0 , 90, 0]
place_blue = [100 , 0 , 0 , 0 , 90 , 0]

#cam = video.WebcamVideoStream(1).start()
cam = cv2.VideoCapture(0)
# cam.set(cv2.CAP_PROP_FRAME_WIDTH , 1920)
# cam.set(cv2.CAP_PROP_FRAME_HEIGHT , 1080)

time.sleep(7)

# frame_undistort = cam.undistort(frame)

# Posiciones objetivo (ejemplo)
POSICION_HOME = [0, 0, 0, 0, 30, 0]  # Articulaciones en grados
POSICION_CARTESIANA = [
    [400, 0, 300],  # Coordenadas XYZ en mm
    [1, 0, 0, 0]    # Cuaternión de orientación (w, x, y, z)
]

print("Conectando...")

with Robot(ip=ROBOT_IP) as robot:
    
    # 1. Mover a posición HOME mediante articulaciones
    print("Moviendo a posición HOME...")
    robot.set_joints(POSICION_HOME)
    time.sleep(2)  # Pequeña pausa
    
    # Verificar posición actual
    joints = robot.get_joints()
    print(f"Posición actual de articulaciones: {joints}")
    
    # 2. Mover a posición cartesiana específica
    print("Moviendo a posición cámara...")
    robot.set_joints(camara_joints)
    time.sleep(2)  # Pequeña pausa
    ret, frame = cam.read()
    cv2.imwrite("prueba", frame)
    #robot.set_cartesian(POSICION_CARTESIANA)

    # Verificar posición actual
    joints = robot.get_joints()
    print(f"Posición actual de articulaciones: {joints}")
    
    # Verificar posición cartesiana
    pose = robot.get_cartesian()
    print(f"Posición cartesiana actual: XYZ={pose[0]}, Orientación={pose[1]}")

cam.release()
print("Conexión cerrada")