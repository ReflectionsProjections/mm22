#!/usr/bin/env python2
import pygame
import sys
import math
import random
from node import Node
from animation import Upgrade, ChangeOwner, AddRootkit, CleanRootkit, IPS, Infiltration, InfiltrationLines, Heal, DDOS, PortScan, Scan
import vis_constants as const
# import animate as ani


class Visualizer(object):

    def __init__(self, _map_json_data, _debug=False, _log_json_data=None, alone=False):
        # Check and init vis
        self.screenHeight = const.screenWidth
        self.screenWidth = const.screenHeight
        self.title = const.title
        self.fps = const.FPStgt
        self.running = True
        self.debug = _debug
        self.json_data = _map_json_data
        self.ticks = 0
        self.ticks_per_turn = const.ticksPerTurn
        self.team_json = None
        self.turn_json = []
        self.game_animations = []  # Used to for global animations like portscan

        self.waterImage = pygame.image.load("src/vis/sprites/water.png")

        self.landImage = pygame.image.load("src/vis/sprites/grass.png")

        # If a log file is given, add all turns first
        if (_log_json_data is not None):
            for item in _log_json_data:
                self.add_turn(item)

        # Setup pygame
        pygame.init()
        self.setup_pygame()
        # process map json to visual data
        self.process_json()
        if alone:
            while 1:
                self.run()

    # Sets up pygame
    def setup_pygame(self):
        pygame.display.set_caption(self.title)
        self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight))
        self.myfont = pygame.font.SysFont("monospace", 10)  # Font used for debugging purpose
        self.gameClock = pygame.time.Clock()

    # Go through the map json and produces where each node should be placed in the visualizer
    #
    # The way it works is that is separates space for each continent.
    # Then places the ISP, DC, and nodes is predefined positions +/- random offsets
    def process_json(self):
        self.draw_json = {}

        # Calculate number of blocks needed for the given map json. Blocks are organized into a square
        # cont_blocks = len(self.json_data['continents'])
        # blocks = math.ceil(math.sqrt(cont_blocks))  # We just need the amount of blocks on one side of the square
        blocks = 4
        self.cont_blocks_taken = [0] * (int(blocks) ** 2)

        x_blockSize = math.floor(self.screenWidth / blocks)
        y_blockSize = math.floor(self.screenHeight / blocks)
        self.landImage = pygame.transform.scale(self.landImage, (int(x_blockSize * 1.1), int(y_blockSize * 1.1)))

        j = random.randint(0, int(blocks) ** 2 - 1)  # Randomly chose a non taken block
        for cont in self.json_data['continents']:

            # This section finds the center of the randomly chosen block, with a given offset
            while(self.cont_blocks_taken[j] != 0):
                j = random.randint(0, int(blocks) ** 2 - 1)
            x_rand = random.randint(-math.floor(x_blockSize * const.center_offset), math.floor(x_blockSize * const.center_offset))
            y_rand = random.randint(-math.floor(y_blockSize * const.center_offset), math.floor(y_blockSize * const.center_offset))
            center_x = (x_blockSize) * ((j % blocks) + 1 - 0.5) + x_rand
            center_y = (y_blockSize) * (math.floor(j / blocks) + 1 - 0.5) + y_rand
            self.cont_blocks_taken[j] = (int(center_x) - x_blockSize / 2, int(center_y) - y_blockSize / 2)

            # For each isp, place it in a circle
            i = 0
            isp_amount = len(cont['isps'])
            for isp in cont['isps']:
                x_offset = random.randint(-math.floor(x_blockSize * const.isp_offset), math.floor(x_blockSize * const.isp_offset))
                y_offset = random.randint(-math.floor(y_blockSize * const.isp_offset), math.floor(y_blockSize * const.isp_offset))
                x = int(center_x + (const.isp_radius * x_blockSize / 2) * math.cos((2 * math.pi / isp_amount) * i)) + x_offset
                y = int(center_y + (const.isp_radius * y_blockSize / 2) * math.sin((2 * math.pi / isp_amount) * i)) + y_offset
                self.draw_json[isp['id']] = Node(x, y, 'isp')

                # For each isp, place its cities around in a circle around the isp
                k = 0
                city_amount = len(isp['cities'])
                for city in isp['cities']:
                    x_offset = random.randint(-math.floor(x_blockSize * const.city_offset), math.floor(x_blockSize * const.city_offset))
                    y_offset = random.randint(-math.floor(y_blockSize * const.city_offset), math.floor(y_blockSize * const.city_offset))
                    x = int(self.draw_json[isp['id']].x + (const.city_radius * x_blockSize / 2) * math.cos((2 * math.pi / city_amount) * k)) + x_offset
                    y = int(self.draw_json[isp['id']].y + (const.city_radius * y_blockSize / 2) * math.sin((2 * math.pi / city_amount) * k)) + y_offset
                    for node in self.json_data['nodes']:
                        if node['id'] == city:
                            self.draw_json[city] = Node(x, y, node['type'])
                    k += 1
                i += 1

            i = 0
            # Same as ISPs, just no cities and closer to center of block
            datacenter_amount = len(cont['datacenters'])
            for datacenter in cont['datacenters']:
                x_offset = random.randint(-math.floor(x_blockSize * const.datacenter_offset), math.floor(x_blockSize * const.datacenter_offset))
                y_offset = random.randint(-math.floor(y_blockSize * const.datacenter_offset), math.floor(y_blockSize * const.datacenter_offset))
                x = int(center_x + (const.datacenter_radius * x_blockSize / 2) * math.cos((2 * math.pi / datacenter_amount) * i)) + x_offset
                y = int(center_y + (const.datacenter_radius * y_blockSize / 2) * math.sin((2 * math.pi / datacenter_amount) * i)) + y_offset
                self.draw_json[datacenter['id']] = Node(x, y, 'datacenter')
                i += 1

    # Game inf loop
    def run(self):
        # while 1:  # Run game forever till exit -- commented out when changed to run in gamerunner
        self.gameClock.tick(self.fps)  # Make sure game is on 60 FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if (self.debug):  # If debugging, then allow going back in time!
                    if event.key == pygame.K_SPACE:  # Space pauses the game
                        self.running = False if self.running else True
                    if event.key == pygame.K_LEFT:
                        self.ticks -= self.ticks_per_turn + self.ticks % self.ticks_per_turn
                        if (self.ticks < 0):
                            self.ticks = 0
                        print("Changed to turn " + str(self.ticks / self.ticks_per_turn))
                    if event.key == pygame.K_ESCAPE:
                        pygame.display.quit()
                        pygame.quit()
                        sys.exit()
        if self.running:
            if(self.ticks % self.ticks_per_turn == 0 and self.ticks > 0):
                self.change_turn(self.ticks / self.ticks_per_turn)
            self.update()
            self.draw()
            self.ticks += 1
        if((self.ticks - 1) % self.ticks_per_turn == 0 and self.ticks > 0):
            return ((self.ticks - 1) / self.ticks_per_turn)
        else:
            return None

    def update(self):
        for key, value in self.draw_json.iteritems():
            value.update()  # update each node in draw_json
        for anim in self.game_animations:
            if(anim.update()):  # If the animation returns true, it is finished and should be removed
                self.game_animations.remove(anim)

    def draw(self):
        self.screen.fill(const.WHITE)  # Background color

        # Draw background water
        for x in range(0, const.screenWidth / 100):
            for y in range(0, const.screenHeight / 100):
                self.screen.blit(self.waterImage, (x * 100, y * 100))

        # Draw continents
        for cont in range(len(self.cont_blocks_taken)):
            if self.cont_blocks_taken[cont] != 0:
                self.screen.blit(self.landImage, self.cont_blocks_taken[cont])

        # If debug mode, draw line between connected nodes and draw its id
        if self.debug:
            for edge in self.json_data['edges']:
                v1, v2 = edge
                pygame.draw.line(self.screen, const.BLACK, (self.draw_json[v1].x, self.draw_json[v1].y), (self.draw_json[v2].x, self.draw_json[v2].y), 1)
        for key, value in self.draw_json.iteritems():
            value.draw(self.screen, self.myfont)
            if self.debug:
                node_id = self.myfont.render(str(key), 1, (0, 0, 0))
                self.screen.blit(node_id, (value.x - 7, value.y - 7))

        for anim in self.game_animations:
            anim.draw(self.screen)  # draw global animations
        pygame.display.update()
        pygame.display.flip()

    def add_turn(self, json):
        if self.team_json is None:
            self.team_json = json
        else:
            self.turn_json.append(json)

    def change_turn(self, turn):
        if(len(self.turn_json) > turn):
            if (self.debug):
                print("Processing turn " + str(turn))
            for node in self.turn_json[turn]['map']:
                # Change owner?
                if node['owner'] != self.draw_json[node['id']].owner_id:
                    self.draw_json[node['id']].change_owner(node['owner'])

                # Maintain node level?
                self.draw_json[node['id']].level = node['upgradeLevel']

                # Add animations
                for prev_node in self.turn_json[(turn) - 1]['map']:
                    if node['id'] == prev_node['id']:
                        self.add_node_animations(node, prev_node)
            for actions in self.turn_json[turn]['turnResults']:
                self.add_player_animations(actions, turn)
        else:
            print("Next turn does not exist")
            self.running = False

    def add_node_animations(self, node, prev_node):
        # Not implemented in game yet
        # Upgrade has occured
        if (node['upgradeLevel'] != prev_node['upgradeLevel']):
            if (not self.found_anim(node, Upgrade)):
                self.draw_json[node['id']].animations.append(Upgrade())

        # Owner has changed, do CONTROL animation
        if node['owner'] != prev_node['owner']:
            if (not self.found_anim(node, ChangeOwner)):
                self.draw_json[node['id']].animations.append(ChangeOwner())

        # Rootkit has been cleaned or rooted
        if len(node['rootkits']) is not 0:
            if (not self.found_anim(node, AddRootkit)):
                self.draw_json[node['id']].animations.append(AddRootkit())

        if len(node['rootkits']) is 0:
            if (self.found_anim(node, AddRootkit)):
                anim = self.found_anim(node, AddRootkit)
                self.draw_json[node['id']].animations.remove(anim)
                if (not self.found_anim(node, CleanRootkit)):
                    self.draw_json[node['id']].animations.append(CleanRootkit())

        # infiltration protection activated
        if node['isIPSed'] is True:
            if (not self.found_anim(node, IPS)):
                self.draw_json[node['id']].animations.append(IPS())
        else:
            anim = self.found_anim(node, IPS)
            if anim:
                self.draw_json[node['id']].animations.remove(anim)

        # infiltration
        for i in range(5):
            curr_infrat_num = node['infiltration'][str(i)]
            prev_infrat_num = prev_node['infiltration'][str(i)]
            if node['owner'] == prev_node['owner']:
                if curr_infrat_num != prev_infrat_num:
                    if curr_infrat_num > prev_infrat_num:
                        if (not self.found_anim(node, Infiltration)):
                            # Being infiltrated, An attack has occured
                            self.draw_json[node['id']].animations.append(Infiltration())
                        break
                    else:
                        if (not self.found_anim(node, Heal)):
                            # Is currently healing
                            self.draw_json[node['id']].animations.append(Heal())
                        break

        # DDoS
        if node['isDDoSed']:
            if (not self.found_anim(node, DDOS)):
                self.draw_json[node['id']].animations.append(DDOS())

    def add_player_animations(self, actions, turn):
        for action in actions:
            if action['status'] != 'fail':
                if action['action'] == 'portscan':
                    if (not self.found_game_anim(PortScan)):
                        self.game_animations.append(PortScan())
                        continue

                if action['action'] == 'control':
                    sourceNodes = []
                    for nodeId in action['powerSources']:
                        sourceNodes.append(self.draw_json[nodeId])
                    self.game_animations.append(InfiltrationLines(self.draw_json[action['target']], sourceNodes))
                    continue

                if action['action'] == 'scan':
                    for node in self.turn_json[turn]['map']:
                        if node['id'] == action['target']:
                            self.draw_json[node['id']].animations.append(Scan())
                    
    def found_anim(self, node, animation_type):
        for animation in self.draw_json[node['id']].animations:
            if(type(animation) is animation_type):
                return animation
        return False

    def found_game_anim(self, animation_type):
        for animation in self.game_animations:
            if(type(animation) is animation_type):
                return True
        return False
