
from controller import Robot


robot = Robot()
time_step = int(robot.getBasicTimeStep())

left_motor = robot.getDevice('left wheel motor')
right_motor = robot.getDevice('right wheel motor')

# Posição infinita coloca os motores em controle de velocidade.
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))

left_motor.setVelocity(10.0)
right_motor.setVelocity(10.0)

start_time = robot.getTime()

while robot.step(time_step) != -1:
    elapsed = robot.getTime() - start_time

    if elapsed < 1.0:
        left_motor.setVelocity(0.0)
        right_motor.setVelocity(0.0)
    elif elapsed < 6.0:
        # TODO 1: use a mesma velocidade nas duas rodas.
        left_motor.setVelocity(3.0)
        right_motor.setVelocity(3.0)
    else:
        left_motor.setVelocity(0.0)
        right_motor.setVelocity(0.0)