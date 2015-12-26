import pygame
import vis_constants as const
from animation import IPS


class Node(object):

    def __init__(self, _x, _y, _node_type):
        self.x = _x
        self.y = _y
        self.node_type = _node_type
        self.animations = []
        self.update_city_sprite()
        self.owner_id = -1
        self.level = 0

    def update_city_sprite(self):
        try:
            self.sprite = pygame.image.load("src/vis/sprites/" + self.node_type + ".png")
            self.sprite_rect = self.sprite.get_rect()
            self.sprite_rect[2] = 20
            self.sprite_rect[3] = 20
            self.sprite_rect[0] = self.x - int(self.sprite_rect[2] / 2.0)
            self.sprite_rect[1] = self.y - int(self.sprite_rect[3] / 2.0)
        except IOError:  # TODO what is the exact exception?
            print("Failed to load sprite image")

    def update(self):
        for animation in self.animations:
            if(animation.update()):
                self.animations.remove(animation)

    def change_owner(self, _owner_id):
        for x in range(0, self.sprite_rect[2]):
            for y in range(0, self.sprite_rect[3]):
                selfColor = const.WHITE if self.owner_id == -1 else const.TEAM_COLORS[self.owner_id]
                if self.sprite.get_at([x, y]) == selfColor:
                    self.sprite.set_at([x, y], const.TEAM_COLORS[_owner_id])
        self.owner_id = _owner_id

    def draw(self, screen, font):
        # Draw IPS if it has one
        for animation in self.animations:
            if isinstance(animation, IPS):
                animation.draw(screen, self.sprite_rect[0], self.sprite_rect[1])

        # Draw node image
        screen.blit(self.sprite, self.sprite_rect)

        # Draw animations
        for animation in self.animations:
            if not isinstance(animation, IPS):
                animation.draw(screen, self.sprite_rect[0], self.sprite_rect[1])

        # Draw node level
        if(self.level != 0):
            level = font.render(str(self.level), 1, (0, 0, 0))
            screen.blit(level, (self.x - 3, self.y + 7))
