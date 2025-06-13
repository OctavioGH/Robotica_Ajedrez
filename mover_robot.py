import chess
from abb import Robot

# Diccionario de coordenadas 3D por casilla (ejemplo simplificado)
SQUARE_TO_COORD = {
    "a1": [0, 0, 0],
    "a2": [0, 50, 0],
    "a3": [0, 100, 0],
    # ... completar para todo el tablero
    "h8": [350, 350, 0]
}

# Orientación constante del efector final (quaternion por defecto)
DEFAULT_ORIENTATION = [1, 0, 0, 0]

def json_to_coord():
    # En esta función la idea es determinar cual de los 2 json es el 
    # ultimo, y generar una tabla con las coordendas de cada una de las celdas
    pass

def square_to_pose(square):
    if square not in SQUARE_TO_COORD:
        raise ValueError(f"No se encuentra la coordenada para {square}")
    return [SQUARE_TO_COORD[square], DEFAULT_ORIENTATION]

def mover(robot, movimiento, JSON_1, JSON_2):
    from_square = move_uci[:2]
    to_square = move_uci[2:4]

    pose_from = square_to_pose(from_square)
    pose_to = square_to_pose(to_square)

    robot = Robot(ip='127.0.0.1')  # Cambiar IP si es necesario

    robot.set_cartesian(pose_from)
    robot.gripper("close")  # Simula tomar la pieza
    robot.set_cartesian(pose_to)
    robot.gripper("open")   # Simula soltar la pieza
    robot.close()

# Ejemplo de uso:
# move_robot_from_chess_move("e2e4")
