import pygame, random, math
from classes import Card,Stack
pygame.init()

screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
screenSize = pygame.display.get_surface().get_size()
on = True
keys = []
scale = 1 #zoom = x1
clock = pygame.time.Clock()
camera = [250,250,screenSize[0],screenSize[1]]
selected = []

grab = pygame.cursors.load_xbm('grab.xbm','grab.xbm')
normal = pygame.cursors.load_xbm('normal.xbm','normal.xbm')

selection_border = pygame.image.load("selected.png")


objects = [Card("king_of_hearts.png",230,260), Card("king_of_hearts.png",230,460)]
selection_rect = (0,0,0,0)

clicking = False # si le clic gauche est enfoncé
moving = False #si un objet est en train d'être bougé
selecting = False

def getScreenPos(obj):
    surface = pygame.transform.scale(obj.image,(round(obj.image.get_width()*scale),round(obj.image.get_height()*scale)))
    surface1 = pygame.transform.rotate(surface,obj.angle)
    rect = surface1.get_rect()
    screenPos = ((obj.x-camera[0]+camera[2]/2)*scale,(obj.y-camera[1]+camera[3]/2)*scale)
    return rect, screenPos, surface1

def changeSelection(obj,zone=False):
    if obj in selected and not zone: #si l'objet cliqué était sélectionné
        if pygame.K_LCTRL in keys:
            selected.remove(obj)
        else:
            selected.clear()
            selected.append(obj)

    elif not obj in selected: #si il était pas sélectionné
        if not pygame.K_LCTRL in keys and not zone:
            selected.clear()
        selected.append(obj)

def contains(r1,r2): #vérifie si r1 appartient à r2
    return (r1[0]+r1[2]>r2[0] and r1[0]<r2[0]+r2[2] and r1[1]+r1[3] > r2[1] and r1[1] < r2[1]+r2[3])

def updateSelection(pos):
    global selection_rect
    x = clicking[0]
    y = clicking[1]
    w = abs(clicking[0]-pos[0])
    h = abs(clicking[1]-pos[1])

    if pos[0] < clicking[0]:
        x = pos[0]
    if pos[1] < clicking[1]:
        y = pos[1]

    selection_rect = (x,y,w,h)

def moveSelection(pos): #update la position des objets sélectionnés quand la souris bouge
    for obj in selected:
        obj = objects[objects.index(obj)]
        relativePos = (pos[0]+obj.relative[0],pos[1]+obj.relative[1])
        obj.x = relativePos[0]/scale+camera[0]-camera[2]/2
        obj.y = relativePos[1]/scale+camera[1]-camera[3]/2

def getRelative(obj,pos): #récupère la position relative de l'objet par rapport à la souris au début d'un drag
    rect, screenPos, surface = getScreenPos(obj)
    rect.move_ip(screenPos[0],screenPos[1])
    relative = (rect.x-pos[0],rect.y-pos[1])
    return relative

def isClicked(obj,pos): #trivial
    rect, screenPos, surface = getScreenPos(obj)
    rect.move_ip(screenPos[0],screenPos[1])
    if rect.collidepoint(pos[0],pos[1]):
        return True
    return False

def endClick(pos):
    global selecting
    global selection_rect
    global objects
    global moving
    moving = False

    clicked = []
    clicked_unselected = []
    #on cherche les objets cliqués (même les objets stackés)
    for obj in objects:
        if isClicked(obj,pos):
            if obj in selected:
                clicked.append(obj)
            else:
                clicked_unselected.append(obj)
                clicked.append(obj)


    if math.sqrt(math.pow(pos[0]-clicking[0],2)+math.pow(pos[1]-clicking[1],2)) < 2: #si la souris n'a pas bougé pendant le clic (si le joueur a drag)

        if clicked == []: #si le clic est dans le vide
            selected.clear()

        for obj in selected:
            obj.relative = (0,0)

    else: #si la souris a bougé pendant le clic
        if len(clicked_unselected) > 0:
            for obj in selected:
                    if obj.type != "stack":
                        objects.remove(obj)
                        selected.remove(obj)
                        if clicked_unselected[-1].type != "stack":
                            objects.remove(clicked_unselected[-1])
                            objects.insert(0,Stack([obj,clicked_unselected[-1]],clicked_unselected[-1].x,clicked_unselected[-1].y))
                        else:
                            clicked_unselected[-1].list.insert(0,obj)
                    else:
                        if clicked_unselected[-1].type != "stack":
                            objects.remove(clicked_unselected[-1])
                            obj.list.append(clicked_unselected[-1])
                            obj.x = clicked_unselected[-1].x
                            obj.y = clicked_unselected[-1].y
                        else:
                            objects.remove(obj)
                            selected.remove(obj)
                            clicked_unselected[-1].list = obj.list + clicked_unselected[-1].list
                            clicked_unselected[-1].updateStack()

    selecting = False
    selection_rect = (0,0,0,0)

def startClick(pos):
    global selecting
    global moving

    clicked = [0,0,0,0,False]
    #on cherche l'objet cliqué du dessus (si plusieurs objets sont stackés)
    for obj in objects:
        if isClicked(obj,pos):
            clicked = obj

    if clicked != [0,0,0,0,False]: #si le clic est pas dans le vide: on bouge les objets avec la souris
        changeSelection(clicked)
        moving = True
        for obj in selected:
            objects.remove(obj)# on met l'objet au dessus
            objects.append(obj)
            objects[-1].relative = getRelative(obj,pos)#mon moi du passé étant un fils de pute je suis obligé de faire cette merde pour modifier un objet

    else: #si le clic est dans le vide: zone de sélection
        selecting = True
        selected.clear()

def events():
    global on
    global clicking
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            on = False

        elif event.type == pygame.KEYDOWN:
            keys.append(event.key)
            if event.key == pygame.K_ESCAPE:
                on = False

        elif event.type == pygame.KEYUP:
            keys.remove(event.key)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                startClick(event.pos)
                clicking = event.pos #clicking != False quand le bouton de la souris est enfoncé
                pygame.mouse.set_cursor(*grab)
            elif event.button == 5:
                camera[2] *=0.9
                camera[3] *= 0.9
            elif event.button == 4:
                camera[2] /= 0.9
                camera[3] /= 0.9

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            endClick(event.pos)
            clicking = False# le bouton de la souris est relâché
            pygame.mouse.set_cursor(*pygame.cursors.arrow)



        if clicking:
            if event.type == pygame.MOUSEMOTION:
                if selecting:
                    updateSelection(event.pos)
                else:
                    moveSelection(event.pos)

def compute(): #prise en charge du clavier et calculs
    global scale
    global camera
    if pygame.K_z in keys:
        camera[1] -= 20
    if pygame.K_s in keys:
        camera[1] += 20
    if pygame.K_d in keys:
        camera[0] += 20
    if pygame.K_q in keys:
        camera[0]-= 20
    if 3 in keys:
        camera[2] -= 60
        camera[3] -= 60
    if 4 in keys:
        camera[2] += 60
        camera[3] += 60
    if pygame.K_e in keys:
        for obj in selected:
            obj.angle -= 2
    if pygame.K_a in keys:
        for obj in selected:
            obj.angle += 2

    scale = screenSize[0]/camera[2] #sert de zoom
    for obj in objects:
        rect, screenPos, surface = getScreenPos(obj)
        if contains((screenPos[0],screenPos[1],rect.width,rect.height),selection_rect):
            changeSelection(obj,zone=True)

def getAngle(x,y): #t'as compris
    a = math.degrees(math.acos(x))
    if y <0:
        a = -a
    return a

def onScreen(container,rect,pos): #fonction qui détermine si l'objet (rect) est visible à l'écran (container)
    width = round(rect[2]/scale)
    height = round(rect[3]/scale)
    if pos[0]+width > container[0]-container[2]/2 and pos[0] < container[0]+container[2]/2:
        if pos[1]+height > container[1]-container[3]/2 and pos[1] < container[1]+container[3]/2:
            return True
    return False

def draw():
    #On utilise pygame.transform.scale et pygame.transform.rotate pour mettre en forme les images
    screen.fill((255,255,255))
    for obj in objects:
        rect, screenPos, surface = getScreenPos(obj)
        rect.move_ip(screenPos[0],screenPos[1])
        if onScreen(camera,rect,(obj.x,obj.y)):
            screen.blit(surface,screenPos)
            if obj in selected:
                surface = pygame.transform.scale(selection_border,(round(selection_border.get_width()*scale),round(selection_border.get_height()*scale)))
                surface1 = pygame.transform.rotate(surface,obj.angle)
                screen.blit(surface1,screenPos)
    if selecting:
        s = pygame.Surface((abs(selection_rect[2]),abs(selection_rect[3])))
        s.set_alpha(128)
        s.fill((100,100,100))
        screen.blit(s, (selection_rect[0],selection_rect[1]))
    pygame.display.update()

def main():
    while on:
        clock.tick(60) #limite de 60 ips
        events()
        compute()
        draw()

if __name__ == "__main__":
    main()
