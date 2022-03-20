import random
import pygame 
from pygame.locals import *

pygame.init()

# Game Constants
screen_width = 864
screen_height = 750
ground_scroll = 0
scroll_speed = 4
fps = 60
flying = False
game_over = False
blitted_bg = -100
pipe_gap = 200
pipe_frequency = 1500 # miliseconds
score = 0
pass_pipe = False
font = pygame.font.SysFont("arial",60)
white = (255,255,255)

# Game Setup
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Flappy Bird By Anique")
clock = pygame.time.Clock()
last_pipe = pygame.time.get_ticks() - pipe_frequency

# Loading Images
bg = pygame.image.load("img/bg.png")
ground_image = pygame.image.load("img/ground.png")
button_img = pygame.image.load("img/restart.png")

# Functions
def draw_text(text,font,text_color,x,y):
    img = font.render(text,True,text_color)
    screen.blit(img,(x,y))

def reset_game():
    pipe_group.empty()
    flappy.rect.x , flappy.rect.y = 100 , int(screen_height)/2
    score =0
    return 0

# Classes
class Bird(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)

        self.images = []
        self.index = 0
        self.counter = 0

        for i in range(1,4):
            img = pygame.image.load(f"img/bird{i}.png")
            self.images.append(img)

        self.image = self.images[self.index]
        
        # This is going to return a rectangle of that image
        self.rect = self.image.get_rect()

        # Making the rectangle center at x and y
        self.rect.center = [x,y]

        self.velocity = 0

        self.clicked = False

    def update(self):
        # Handling the movement of the flappy bird

        if flying==True:

            # Gravity
            
            self.velocity += 0.1

            # Limiting the velocity to 8
            if self.velocity > 8:
                self.velocity = 8
            # print(self.velocity)

            if self.rect.bottom < 602:
                self.rect.y += int(self.velocity)

            if self.rect.top < 1:
                self.rect.y -=int(self.velocity)
            # print(self.rect.top)

        # Jumping at the left click

        if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
            self.clicked = True
            self.velocity = -5

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False


        # Handling the animation of the bird
        if game_over == False:
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1

                if self.index >= len(self.images):
                    self.index=0
            self.image=self.images[self.index]
        else:
            self.image = self.images[1]
        if flying == False:
            self.image = self.images[1]

        # Rotating the bird
        # The angle of rotation is counter clockwise by default which is why we have to
        # multiply it with a negative integer
        if game_over==False and flying==True:
            self.image = pygame.transform.rotate(self.images[self.index],self.velocity * -2)
        if game_over ==  True and flying == False:
            self.image = pygame.transform.rotate(self.images[self.index],-52)
        
# Pipe class

class Pipe(pygame.sprite.Sprite):
    def __init__(self,x,y,position):
        pygame.sprite.Sprite.__init__(self)
        self.image= pygame.image.load("img/pipe.png")
        self.rect = self.image.get_rect()

        # Position = 1 means from the top
        # Position = -1 means from the bottom
        if position == 1:
            self.image=pygame.transform.flip(self.image,False,True)
            self.rect.bottomleft = [x , y - int(pipe_gap/2)]
        if position == -1:           
            self.rect.topleft = [x , y + int(pipe_gap/2)]

    def update(self):
        self.rect.x -= scroll_speed

        # Even if the pipe has gone to the right 
        # It is still present in the game memory and the pipe group

        # You can run this below code to see what is happening
        # if self.rect.right < 200:
        #     self.kill()

        if self.rect.right < 0:
            self.kill()

pipe_group=pygame.sprite.Group()


bird_group = pygame.sprite.Group()
flappy = Bird(100 , int( screen_height / 2 ))
bird_group.add(flappy)

class Button():
    def __init__(self,x,y,image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft=(x,y)

    def draw(self):
        action = False

        # Get mouse position
        position = pygame.mouse.get_pos()

        # Check if mouse is over the button
        if self.rect.collidepoint(position):
            if pygame.mouse.get_pressed()[0]==1:
                action = True
        
        # Draw button
        screen.blit(self.image,(self.rect.x,self.rect.y))
        
        return action
button = Button(screen_width//2 -50,screen_height//2 -100,button_img)

run = True
while run:

    clock.tick(fps)

    # Drawing background
    screen.blit(bg,(0,blitted_bg))

    # Drawing the ground
    screen.blit(ground_image,(ground_scroll,602))

    # Drawing the bird
    bird_group.draw(screen)
    bird_group.update()

    # Drawing the pipe
    pipe_group.draw(screen)

    # Checking for score
    # First , we need to check if there is a pipe on the score before trying to get the 
    # co ordinates of a pipe because that will throw an error

    if len(pipe_group) >0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
            and pass_pipe==False:
            pass_pipe=True
        if pass_pipe==True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score+=1
                pass_pipe=False
    
    # Checking for collision
    if pygame.sprite.groupcollide(bird_group,pipe_group,False,False):
        game_over=True

    # Checking if the game is over or not over
    if flappy.rect.bottom > 599:
        game_over=True
        flying=False

    # Scrolling the ground
    # Only scroll when the game is over
    if game_over == False and flying==True:
        draw_text("Score: "+str(score),font,white,int(screen_width/4),20)

        # Generating pipes
        time_now = pygame.time.get_ticks()
        if time_now -last_pipe>pipe_frequency:
            pipe_height = random.randint(-100,100)
            btm_pipe=Pipe(screen_width,int(bg.get_height()/2  + pipe_height),-1)
            top_pipe=Pipe(screen_width,int(bg.get_height()/2 + pipe_height),1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll=0
        pipe_group.update()

    # Check for game over and restart
    if game_over == True:
        if button.draw() == True:
            game_over = False
            score = reset_game()

    if flying == False and game_over == False:
        draw_text("Press S to start",font,white,int(screen_width/4),100)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                run=False
            if event.key == pygame.K_s and flying == False and game_over==False:
                flying = True

    pygame.display.update()
pygame.quit()