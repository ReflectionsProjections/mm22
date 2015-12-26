import pygame
import vis_constants as const
import math


class Animation(object):

    def __init__(self):
        self.current_tick = 0
        self.images = []
        self.image_tick = []
        self.image_rects = []
        self.remove_after_complete = True
        self.repeat = False

    def update(self):
        self.current_tick += 1
        if (self.current_tick >= len(self.image_tick) - 1):
            if (self.remove_after_complete):
                return True
            elif (self.repeat):
                self.current_tick = 0
            else:
                self.current_tick = len(self.image_tick) - 2

    def draw(self, screen, x, y):
        screen.blit(self.images[self.image_tick[self.current_tick]], (x, y))


class Upgrade(Animation):

    def __init__(self):
        Animation.__init__(self)
        self.setup_animation()

    def setup_animation(self):
        # Add the images to the images
        for i in range(1, 2):
            self.images.append(pygame.image.load("src/vis/sprites/upgrade_" + str(i) + ".png"))
        for i in range(60):
            self.image_tick.append(0)
        for i in range(len(self.images)):
            self.image_rects.append(self.images[i].get_rect())


class ChangeOwner(Animation):

    def __init__(self):
        Animation.__init__(self)
        self.setup_animation()

    def setup_animation(self):
        # Add the images to the images
        for i in range(1, 2):
            self.images.append(pygame.image.load("src/vis/sprites/change_owner_" + str(i) + ".png"))
        for i in range(60):
            self.image_tick.append(0)
        for i in range(len(self.images)):
            self.image_rects.append(self.images[i].get_rect())


class AddRootkit(Animation):

    def __init__(self):
        Animation.__init__(self)
        self.setup_animation()
        self.remove_after_complete = False
        self.repeat = True

    def setup_animation(self):
        # Add the images to the images
        for i in range(1, 2):
            self.images.append(pygame.image.load("src/vis/sprites/add_rootkit_" + str(i) + ".png"))
        for i in range(60):
            self.image_tick.append(0)
        for i in range(len(self.images)):
            self.image_rects.append(self.images[i].get_rect())


class CleanRootkit(Animation):

    def __init__(self):
        Animation.__init__(self)
        self.setup_animation()

    def setup_animation(self):
        # Add the images to the images
        for i in range(1, 2):
            self.images.append(pygame.image.load("src/vis/sprites/clean_rootkit_" + str(i) + ".png"))
        for i in range(60):
            self.image_tick.append(0)
        for i in range(len(self.images)):
            self.image_rects.append(self.images[i].get_rect())


class IPS(Animation):

    def __init__(self):
        Animation.__init__(self)
        self.setup_animation()
        self.remove_after_complete = False

    def setup_animation(self):
        # Add the images to the images
        for i in range(1, 2):
            self.images.append(pygame.image.load("src/vis/sprites/ips_" + str(i) + ".png"))
        for i in range(60):
            self.image_tick.append(0)
        for i in range(len(self.images)):
            self.image_rects.append(self.images[i].get_rect())


class Infiltration(Animation):

    def __init__(self):
        Animation.__init__(self)
        self.setup_animation()

    def setup_animation(self):
        # Add the images to the images
        for i in range(1, 2):
            self.images.append(pygame.image.load("src/vis/sprites/infiltration_" + str(i) + ".png"))
        for i in range(60):
            self.image_tick.append(0)
        for i in range(len(self.images)):
            self.image_rects.append(self.images[i].get_rect())


class Heal(Animation):

    def __init__(self):
        Animation.__init__(self)
        self.setup_animation()

    def setup_animation(self):
        # Add the images to the images
        for i in range(1, 6):
            self.images.append(pygame.image.load("src/vis/sprites/heal_" + str(i) + ".png"))
        for i in range(12):
            self.image_tick.append(0)
        for i in range(12):
            self.image_tick.append(1)
        for i in range(12):
            self.image_tick.append(2)
        for i in range(12):
            self.image_tick.append(3)
        for i in range(12):
            self.image_tick.append(4)
        for i in range(len(self.images)):
            self.image_rects.append(self.images[i].get_rect())


class DDOS(Animation):

    def __init__(self):
        Animation.__init__(self)
        self.setup_animation()

    def setup_animation(self):
        # Add the images to the images
        for i in range(1, 10):
            self.images.append(pygame.image.load("src/vis/sprites/ddos_" + str(i * 2) + ".png"))
            for _ in range(3):
                self.image_tick.append(i - 1)
        for _ in range(33):
            self.image_tick.append(8)
        for i in range(len(self.images)):
            self.image_rects.append(self.images[i].get_rect())


class Scan(Animation):

    def __init__(self):
        Animation.__init__(self)
        self.setup_animation()

    def setup_animation(self):
        # Add the images to the images
        for i in range(1, 17):
            self.images.append(pygame.image.load("src/vis/sprites/scan_" + str(i) + ".png"))
            for _ in range(4):
                self.image_tick.append(i - 1)
        for i in range(len(self.images)):
            self.image_rects.append(self.images[i].get_rect())

# Below are global animations


class PortScan(object):

    def __init__(self):
        self.x = const.screenWidth
        self.speed = -const.screenWidth / const.ticksPerTurn

    def update(self):
        self.x += self.speed
        if (self.x < 0):
            return True

    def draw(self, screen):
        pygame.draw.line(screen, (0, 255, 0), (self.x, 0), (self.x, const.screenHeight), 10)


class InfiltrationLines(object):

    def __init__(self, _target_node, _source_nodes):
        self.target_node = _target_node
        self.source_nodes = _source_nodes
        self.ticks = 0

    def update(self):
        self.ticks += 1
        if (self.ticks > 60):
            return True

    def draw(self, screen):
        for node in self.source_nodes:
            pygame.draw.line(screen, const.TEAM_COLORS[node.owner_id], (node.x, node.y), (self.target_node.x, self.target_node.y), 1)
            vector = (self.target_node.x - node.x, self.target_node.y - node.y)
            circle_pos_x = int(node.x + vector[0] * (self.ticks / 60.0))
            circle_pos_y = int(node.y + vector[1] * (self.ticks / 60.0))
            pygame.draw.circle(screen, const.TEAM_COLORS[node.owner_id], (circle_pos_x, circle_pos_y), 3)
