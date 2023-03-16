import pygame

red = (200, 0, 0)
blue = (0, 0, 255)
green = (0, 155, 0)
yellow = (155, 155, 0)
white = (255, 255, 255)
black = (0, 0, 0) 

X_RES = 640
Y_RES = 480

X_ORIG_OFFSET = int(X_RES * 0.4)
Y_ORIG_OFFSET = int(Y_RES * 0.9)

def x2pix(x,y):
    new_x = -1*x + X_ORIG_OFFSET
    new_y = -1*y + Y_ORIG_OFFSET
    return new_x, new_y

def draw_robot(x, y, p):
    pass


class Simulator: 
    def __init__(self):
        self.x = [0] * 24

    def main(self , screen):
        clock = pygame.time.Clock()
        while 1:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return
            screen.fill(white)
            orig = x2pix(0,0)
            pygame.draw.line(screen, black, (0, orig[1]), (X_RES, orig[1]))
            pygame.draw.circle(screen,red,x2pix(0,0),5)
            pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((X_RES,Y_RES))
    pygame.display.set_caption("Soft Robot Simulator")
    Simulator().main(screen)