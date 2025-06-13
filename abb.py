'''
Michael Dawson-Haggerty

abb.py: contains classes and support functions which interact with an ABB Robot running our software stack (RAPID code module SERVER)


For functions which require targets (XYZ positions with quaternion orientation),
targets can be passed as [[XYZ], [Quats]] OR [XYZ, Quats]

February 2019 - Modifications added by Leandro Mayrata - FIUNER

- Compatible with Python 3.5
-  

'''
from math import pi
import socket
import json 
import time
import inspect
from threading import Thread
from collections import deque
import logging
import numpy as np
# import transformation
# print("ABB imported")

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())
    
class Robot:
    def __init__(self, 
                 ip          = '127.0.0.1',#'192.168.125.1', 
                 port_motion = 5000,
                 port_logger = 5001,
                 logger = False):
        self.delay   = .08
        self.connect_motion((ip, port_motion))
        # self.connect_logger((ip, port_logger))
        #self.log_thread = Thread(target = self.connect_logger , args = ((ip, port_logger))).start()       
        #self.log_thread = Thread(target = self.connect_logger, args = ((ip, port_logger)))
        #self.log_thread.start()
        # self.connect_motion((ip, port_motion))
        self.set_units('millimeters', 'degrees')
        self.set_tool()
        self.set_workobject()
        self.set_speed()
        self.set_zone()
        # self.pose = []

    def connect_motion(self, remote):        
        log.info('Attempting to connect to robot motion server at %s', str(remote))
        # print("motion af: ", socket.AF_INET)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(2.5)
        # print("Smotion", self.sock)
        self.sock.connect(remote)
        self.sock.settimeout(None)
        log.info('Connected to robot motion server at %s', str(remote))

    def connect_logger(self, remote, maxlen=None):
        self.pose   = deque(maxlen=maxlen)
        self.joints = deque(maxlen=maxlen)
        recieved = []
        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Bandera ")
        # print("logger af: ", socket.AF_INET)
        # print("remote Slogger: ", (remote, 5001))
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((remote, 5001))
        self.s.setblocking(1)
        try:
            while True:
                recieved = list(self.s.recv(4096).split())
                data = [x.decode('utf-8') for x in recieved]# print(data)
                #num = int(data[1].decode('utf-8'))
                num = int(data[1])
            	# print((num))
            	# print(data[1].decode('utf-8'))
                # data = map(str, s.recv(4096).split())
                if num:
                    self.joints.append([data[2:5], data[5:]])
            		# print("joints = ", self.joints[-1][1])
                elif num == 0:
                    self.pose.append([data[2:5], data[5:]])
            		# print("pose = ", self.pose[-1][1])
                else:
                    AssertionError
        finally:
            print("proceso finalizado")
            # self.s.shutdown(socket.SHUT_RDWR)

    def set_units(self, linear, angular):
        units_l = {'millimeters': 1.0,
                   'meters'     : 1000.0,
                   'inches'     : 25.4}
        units_a = {'degrees' : 1.0,
                   'radians' : 57.2957795}
        self.scale_linear = units_l[linear]
        self.scale_angle  = units_a[angular]

    def set_cartesian(self, pose):
        '''
        Executes a move immediately from the current pose,
        to 'pose', with units of millimeters.
        '''
        msg  = "01 " + self.format_pose(pose)
        # print(msg) 
        return self.send(msg)

    def set_joints(self, joints):
        '''
        Executes a move immediately, from current joint angles,
        to 'joints', in degrees. 
        '''
        if len(joints) != 6: return False
        msg = "02 "
        for joint in joints: msg += format(joint*self.scale_angle, "+08.2f") + " " 
        msg += "#"
        # print(msg)
        return self.send(msg)

    def get_cartesian(self):
        '''
        Returns the current pose of the robot, in millimeters
        '''
        msg = "03 #"
        data = self.send(msg).split()
        r = [float(s) for s in data]
        return [r[2:5], r[5:9]]

    def get_joints(self):
        '''
        Returns the current angles of the robots joints, in degrees. 
        '''
        msg = "04 #"
        data = self.send(msg).split()
        return [float(s) / self.scale_angle for s in data[2:8]]

    def get_external_axis(self):
        '''
        If you have an external axis connected to your robot controller
        (such as a FlexLifter 600, google it), this returns the joint angles
        '''
        msg = "05 #"
        data = self.send(msg).split()
        return [float(s) for s in data[2:8]]
       
    def get_robotinfo(self):
        '''
        Returns a robot- unique string, with things such as the
        robot's model number. 
        '''
        msg = "98 #"
        data = str(self.send(msg))[5:].split('*')
        log.debug('get_robotinfo result: %s', str(data))
        return data

    def set_tool(self, tool=[[0,0,0], [1,0,0,0]]):
        '''
        Sets the tool centerpoint (TCP) of the robot. 
        When you command a cartesian move, 
        it aligns the TCP frame with the requested frame.
        
        Offsets are from tool0, which is defined at the intersection of the
        tool flange center axis and the flange face.
        '''
        msg       = "06 " + self.format_pose(tool)    
        self.send(msg)
        self.tool = tool

    def load_json_tool(self, file_obj):
        if file_obj.__class__.__name__ == 'str':
            file_obj = open(filename, 'rb');
        tool = check_coordinates(json.load(file_obj))
        self.set_tool(tool)
        
    def get_tool(self): 
        log.debug('get_tool returning: %s', str(self.tool))
        return self.tool

    def set_workobject(self, work_obj=[[0,0,0],[1,0,0,0]]):
        '''
        The workobject is a local coordinate frame you can define on the robot,
        then subsequent cartesian moves will be in this coordinate frame. 
        '''
        msg = "07 " + self.format_pose(work_obj)   
        self.send(msg)

    def set_speed(self, speed=[100,50,50,50]):
        '''
        speed: [robot TCP linear speed (mm/s), TCP orientation speed (deg/s),
                external axis linear, external axis orientation]
        '''

        if len(speed) != 4: return False
        msg = "08 " 
        msg += format(speed[0], "+08.1f") + " " 
        msg += format(speed[1], "+08.2f") + " "  
        msg += format(speed[2], "+08.1f") + " " 
        msg += format(speed[3], "+08.2f") + " #"     
        self.send(msg)

    def set_zone(self, zone_key     = 'z1', point_motion = False, manual_zone  = []):
        zone_dict = {'z0'  : [.3,.3,.03], 
                    'z1'  : [1,1,.1], 
                    'z5'  : [5,8,.8], 
                    'z10' : [10,15,1.5], 
                    'z15' : [15,23,2.3], 
                    'z20' : [20,30,3], 
                    'z30' : [30,45,4.5], 
                    'z50' : [50,75,7.5], 
                    'z100': [100,150,15], 
                    'z200': [200,300,30]}
        '''
        Sets the motion zone of the robot. This can also be thought of as
        the flyby zone, AKA if the robot is going from point A -> B -> C,
        how close do we have to pass by B to get to C
        
        zone_key: uses values from RAPID handbook (stored here in zone_dict)
        with keys 'z*', you should probably use these

        point_motion: go to point exactly, and stop briefly before moving on

        manual_zone = [pzone_tcp, pzone_ori, zone_ori]
        pzone_tcp: mm, radius from goal where robot tool centerpoint 
                   is not rigidly constrained
        pzone_ori: mm, radius from goal where robot tool orientation 
                   is not rigidly constrained
        zone_ori: degrees, zone size for the tool reorientation
        '''
        if point_motion: 
            zone = [0,0,0]
        elif len(manual_zone) == 3: 
            zone = manual_zone
        elif zone_key in zone_dict.keys(): 
            zone = zone_dict[zone_key]
        else: return False
        
        msg = "09 " 
        msg += str(int(point_motion)) + " "
        msg += format(zone[0], "+08.4f") + " " 
        msg += format(zone[1], "+08.4f") + " " 
        msg += format(zone[2], "+08.4f") + " #"
        self.send(msg)

    def buffer_add(self, pose):
        '''
        Appends single pose to the remote buffer
        Move will execute at current speed (which you can change between buffer_add calls)
        '''
        # print(pose)
        if len(pose) == 6:
            msg = "37 "
            for joint in pose: msg += format(joint*self.scale_angle, "+08.2f") + " "
            msg += "#"
        else:
            msg = "30 " + self.format_pose(pose)
        self.send(msg)

    def buffer_set(self, pose_list):
        '''
        Adds every pose in pose_list to the remote buffer
        '''
        self.clear_buffer()
        for pose in pose_list:
            print("pose :", pose)
            self.buffer_add(pose)
        if self.buffer_len() == len(pose_list):
            log.debug('Successfully added %i poses to remote buffer', 
                      len(pose_list))
            return True
        else:
            log.warn('Failed to add poses to remote buffer!')
            self.clear_buffer()
            return False

    def clear_buffer(self):
        msg = "31 #"
        data = self.send(msg)
        if self.buffer_len() != 0:
            log.warn('clear_buffer failed! buffer_len: %i', self.buffer_len())
            raise NameError('clear_buffer failed!')
        return data

    def buffer_len(self):
        '''
        Returns the length (number of poses stored) of the remote buffer
        '''
        msg = "32 #"
        data = self.send(msg).split()
        return int(float(data[2]))

    def buffer_execute(self, tp = 'joint'):
        '''
        Immediately execute linear moves to every pose in the remote buffer.
        '''
        if tp == 'joint':
            msg = "38 #"
        else:
            msg = "33 #"
        return self.send(msg)

    def set_external_axis(self, axis_unscaled=[-550,0,0,0,0,0]):
        if len(axis_unscaled) != 6: return False
        msg = "34 "
        for axis in axis_unscaled:
            msg += format(axis, "+08.2f") + " " 
        msg += "#"   
        return self.send(msg)

    def move_circular(self, pose_onarc, pose_end):
        '''
        Executes a movement in a circular path from current position, 
        through pose_onarc, to pose_end
        '''
        msg_0 = "35 " + self.format_pose(pose_onarc)  
        msg_1 = "36 " + self.format_pose(pose_end)

        data = self.send(msg_0).split()
        if data[1] != '1': 
            log.warn('move_circular incorrect response, bailing!')
            return False
        return self.send(msg_1)

    def set_do(self, id=1, value = 0 ):
        '''
        A function to set a physical DIO line on the robot.
        For this to work you're going to need to edit the RAPID function
        and fill in the DIO you want this to switch. 
        '''
        msg = '11 ' + str(id)+" " + str(int(bool(value))) + ' #'

        return self.send(msg)

    def goHOME(self, HOME=[0,0,0,0,30,0]):
        '''
        A funcion to move to a preset home position
        '''
        self.set_joints(HOME)

    def moveRel(self, x=0, y=0,z=0):
        current_pose = self.get_cartesian()
        # print(current_pose)
        current_pose[0][0] += x
        current_pose[0][1] += y
        current_pose[0][2] += z
        self.set_cartesian(current_pose)

    def rotate(self, rotationaxis , degrees):
        theta = degrees * pi / 180
        current_pose = self.get_cartesian()
        current_eul = list(transformation.euler_from_quaternion(current_pose[1]))
        mask = [i*theta for i in rotationaxis]
        rotated_eul = [sum(i) for i in zip(current_eul, mask)]
        rotated_q = transformation.quaternion_from_euler(rotated_eul [0], rotated_eul [1], rotated_eul [2])
        print("new position rotated ", current_pose[0], rotated_q)
        self.set_cartesian((current_pose[0], rotated_q))

    def rotateRelTool(self, Rx = 0, Ry = 0, Rz = 0):
        '''
        Rotation of TCP frame axis. Rx, Ry, Rz MUST BE given in degrees 
        '''
        msg = "10 "
        msg += format(Rx, ".2f") + " "
        msg += format(Ry, ".2f") + " "
        msg += format(Rz, ".2f") + " #"
        self.send(msg)

    def gripper(self, action = "open"):
        if action == "open":
            self.set_do(1,1)
        elif action == "close":
            self.set_do(1,0)
        else:
            print("Argument not valid")
      
    def send(self, message, wait_for_response=True):
        '''
        Send a formatted message to the robot socket.
        if wait_for_response, we wait for the response and return it
        '''
        caller = inspect.stack()[1][3]
        log.debug('%-14s sending: %s', caller, message)
        self.sock.send(message.encode('ascii'))
        time.sleep(self.delay)
        if not wait_for_response: return
        data = self.sock.recv(4096)
        # log.debug('%-14s recieved: %s', caller, data)
        return data
        
    def format_pose(self, pose):
        pose = check_coordinates(pose)
        msg  = ''
        for cartesian in pose[0]:
            msg += format(cartesian * self.scale_linear,  "+08.1f") + " " 
        for quaternion in pose[1]:
            msg += format(quaternion, "+08.5f") + " " 
        msg += "#"
        # print(msg)
        return msg
        
    def format_pos(self, pose):
        msg = ''
        for cartesian in pose:
            msg += format(cartesian * self.scale_linear, "08.1f") + " "
        msg += "#"
        return msg
        
    def format_orient(self, pose):
        msg = ''
        for quaternion in pose:
            msg += format(quaternion, "08.5f") + " "
        msg += "#"
        return msg
        
    def close(self):
        self.send("99 #", False)
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        #self.log_thread.join()
        #self.s.shutdown(socket.SHUT_RDWR)
        #self.s.close()
        
        # f = open("jointsvalueslogger-cycling-6050.txt", "w")
        # f.writelines(["%s\n" %joint for joint in self.joints])
        # f.close()
        log.info('Disconnected from ABB robot.')

    def __enter__(self):
        return self
        
    def __exit__(self, type, value, traceback):
        self.close()

def check_coordinates(coordinates):
	# print(len(coordinates[0]))
	if type(coordinates[0]) == np.ndarray or type(coordinates[1]) == np.ndarray:
		coordinates[0] = coordinates[0].tolist()[0] 
		coordinates[1]= coordinates[1].tolist()
		# print ("coordinate  -------", coordinates[1])
	if len(coordinates) == 2 and len(coordinates[0]) == 3 and len(coordinates[1]) == 4:
		return coordinates
	elif (len(coordinates) == 7):
		return [coordinates[0:3], coordinates[3:7]]
	log.warn('Recieved malformed coordinate: %s', str(coordinates))
	raise NameError('Malformed coordinate!')

if __name__ == '__main__':
    formatter = logging.Formatter("[%(asctime)s] %(levelname)-7s (%(filename)s:%(lineno)3s) %(message)s", "%Y-%m-%d %H:%M:%S")
    handler_stream = logging.StreamHandler()
    handler_stream.setFormatter(formatter)
    handler_stream.setLevel(logging.DEBUG)
    log = logging.getLogger('abb')
    log.setLevel(logging.DEBUG)
    log.addHandler(handler_stream)
    
