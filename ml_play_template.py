"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import (
    SceneInfo, GameStatus, PlatformAction
)


def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False

    dirX = 0
    dirY = 0
    xRec = 95
    yRec = 200
    left = 0
    right = 195
    location = 0
    platSpeed = 5
    ballSpeed = 7
    count = 0
    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()
    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
                scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed

            ball_served = False

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information

        # 3.4. Send the instruction for this frame to the game process
        ballx, bally = scene_info.ball
        platx, platy = scene_info.platform

        if not ball_served:
            comm.send_instruction(
                scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True
            max = 0
            for x, y in scene_info.bricks:
                if y > max:
                    max = y
            print(max)
        else:

            if ballx - xRec > 0:
                dirX = 1
            else:
                dirX = -1
            xRec = ballx
            if bally - yRec > 0:
                dirY = 1
            else:
                dirY = -1
            yRec = bally
            # print(dirY)
            if (bally < max+ballSpeed*4 and bally > max+ballSpeed*2) and dirY == 1:
                fps = (platy-bally)/ballSpeed
                tmpdirX = dirX
                tmpBall = ballx

                for i in range(int(fps)):
                    # print(tmpBall)
                    if tmpdirX == 1 and tmpBall + ballSpeed <= right:
                        tmpBall = tmpBall+ballSpeed
                    elif tmpdirX == 1 and tmpBall + ballSpeed > right:
                        tmpBall = right
                        tmpdirX = -1
                        continue
                    if tmpdirX == -1 and tmpBall - ballSpeed >= left:
                        tmpBall = tmpBall - ballSpeed
                    elif tmpdirX == -1 and tmpBall - ballSpeed < left:
                        tmpBall = left
                        tmpdirX = 1
                        continue
                location = tmpBall

                if platx+20 < ballx:
                    comm.send_instruction(
                        scene_info.frame, PlatformAction.MOVE_RIGHT)
                elif platx+20 > ballx:
                    comm.send_instruction(
                        scene_info.frame, PlatformAction.MOVE_LEFT)
                else:
                    comm.send_instruction(
                        scene_info.frame, PlatformAction.NONE)
                # print(fps)
            elif bally > max+ballSpeed*2 and dirY == 1:
                # print(count)
                # print(scene_info.ball)
                # print(location)
                count = count+1
                if platx+20 < location + platSpeed/2 and platx+20 > location - platSpeed/2:
                    comm.send_instruction(
                        scene_info.frame, PlatformAction.NONE)
                elif platx+20 < location:
                    comm.send_instruction(
                        scene_info.frame, PlatformAction.MOVE_RIGHT)
                elif platx+20 > location:
                    comm.send_instruction(
                        scene_info.frame, PlatformAction.MOVE_LEFT)

            else:
                if platx+20 < ballx:
                    comm.send_instruction(
                        scene_info.frame, PlatformAction.MOVE_RIGHT)
                elif platx+20 > ballx:
                    comm.send_instruction(
                        scene_info.frame, PlatformAction.MOVE_LEFT)
                else:
                    comm.send_instruction(
                        scene_info.frame, PlatformAction.NONE)
