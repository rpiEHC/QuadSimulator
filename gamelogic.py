"""
    Quadcopter Simulator
    --
    A quick way to test stabilzation algorithms.
    
    John Drogo
    Septemer 15, 2014
    
    YOU NEED TO USE THIS IN BLENDER!
    Look for spots that say CHANGE THIS and modify them as needed.
    
    This simulator does not take aerodynamics or pressure into account.
    
    The red marks on the quadcopter mark its front,
    each fan is numbered clockwise with fan 0 being the front left.
    
    ALL UNITS ARE IN SI!
    (Angles are in radians.)
    
    When using the acceleration or velocity lists index 0 indicates the x axis,
    1 is the y, and 2 is the z.
    
    I consider clockwise a positive RPM, and counterclockwise as negative.

    Happy flying!

"""

import bge
import random
import math
import mathutils

def main():
    
    cont = bge.logic.getCurrentController()
    quad = cont.owner
    quad_pos = quad.worldPosition
    
    try:
        if quad["last_vel"]:
            pass
        
    except:
        print("Last velocity point does not exist.")
        quad["last_vel"] = [ 0, 0, 0 ]
    
    random.seed()
    force = [ 0.0, 0.0, 0.0 ]
    torque = [ 0, 0, 0]


    #Quadcopter description.
    #CHANGE THIS
    p_m = .018 #Propellor mass.
    p_r = .10  #Prop length.
    p_rpm = [ quad["rpm0"], quad["rpm1"], quad["rpm2"], quad["rpm3"] ] #Prop rpm. (Change in game window or don't at all.)
    q_m = quad.mass #Mass of quadcopter (set using the physics tab below.
    q_r = .15 #Distance from prop center to quad center of mass.

    #Now we calculate the prop's angular momentum. (No need to change this.)
    p_w  = [ (p_rpm[0] / 60) * 2 * math.pi, (p_rpm[1] / 60) * 2 * math.pi, (p_rpm[2] / 60) * 2 * math.pi, (p_rpm[3] / 60) * 2 * math.pi ]
    

    #Your thrust curve. (CHANGE THIS!)
    def thrustRPM(propnum):
        #Basic efficency curve, assuming linear relation. Don't forget to flip the thrust on your ccw props.
        return p_rpm[propnum]/(10000)*quad["maxThrust"] * (-1 if propnum % 2 else 1)


    
    # Resolve force components to moments and total force.
    torque[0] = q_r/math.sqrt(2) * ( -thrustRPM(0) - thrustRPM(1) + thrustRPM(2) + thrustRPM(3) )    #x axis
    torque[1] = q_r/math.sqrt(2) * ( -thrustRPM(0) - thrustRPM(3) + thrustRPM(1) + thrustRPM(2) )    #y axis
    torque[2] =  ( (p_m * (p_r * p_r)) / 2 * p_w[0] ) + ( (p_m * (p_r * p_r)) / 2 * p_w[1] ) + ( (p_m * (p_r * p_r)) / 2 * p_w[2] ) + ( (p_m * (p_r * p_r)) / 2 * p_w[3] ) #z axis
    force[2] = ( thrustRPM(0) + thrustRPM(1) + thrustRPM(2) + thrustRPM(3) )

    local = True    
    quad.applyForce(force, local)
    quad.applyTorque(torque, local)
    
    
    
    #Calculates change in velocity.
    #Each tick should occur at 60Hz.
    def calculateAccel():

        #Simulate the effects of gravity on the accelerometer.
        R = quad.worldOrientation
        g_l = mathutils.Vector((0.0, 0, -9.8)) #Gravity.
        g_l.rotate(R) #Localize gravity.
        
        #print("Rotation matrix:", R)
        #print("Gravity:", g_l.xyz) #Local gravity vector (won't always be straight down.)

        accel = [ 0, 0, 0 ]
        vel = quad.getLinearVelocity(0)
        
        #Simulate the acceleromter values by adding the localized gravity vector.
        accel[0] = (vel[0] - quad["last_vel"][0]) * 60 + g_l[0]
        accel[1] = (vel[1] - quad["last_vel"][1]) * 60 + g_l[1]
        accel[2] = (vel[2] - quad["last_vel"][2]) * 60 + g_l[2]
                
        quad["last_vel"] = vel
        print(accel)
    
        return accel
    
    
    
    #Sets the rpm for each fan.
    #Max rpm is 10000.
    #Fan 0 = fl, then number clockwise.
    #CHANGE THIS!
    def stabilzationTick(accel, angVel):
        maxRPM = 10000

        print("Angular velocity:", angVel)
        
        if (accel[2] > -9.8):
           return [ quad["rpm0"] - 200, quad["rpm1"] + 200, quad["rpm2"] - 200, quad["rpm3"] + 200 ]
       
        elif (accel[2] < -9.8):
           return [ quad["rpm0"] + 70, quad["rpm1"] - 70, quad["rpm2"] + 70, quad["rpm3"] - 70 ]

        return [ quad["rpm0"], quad["rpm1"], quad["rpm2"], quad["rpm3"] ]
        
        
    #Update RPMs based on accelerometer and gyroscope date.
    quad["rpm0"], quad["rpm1"], quad["rpm2"], quad["rpm3"] = stabilzationTick(calculateAccel(), quad.localAngularVelocity)

    return 
 
main()
