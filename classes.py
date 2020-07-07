import pygame

class Card():
    def __init__(self,path,x,y):
        self.image = pygame.image.load(path)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.x = x
        self.y = y
        self.angle = 0
        self.relative = (0,0)
        self.type = "card"
        self.side = 0

class Stack():
    def __init__(self,list,x,y):
        self.x = x
        self.y = y
        self.list = list
        self.type = "stack"
        self.side = 0
        self.angle = 0
        self.relative = (0,0)
        self.updateStack()

    def updateStack(self):
        self.image = self.list[-1].image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
