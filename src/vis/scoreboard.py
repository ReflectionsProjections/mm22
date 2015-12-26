#!/usr/bin/env python2
import pygame
import sys
import vis_constants as vis_const
import scoreboard_constants as const
import json as JSON


class Scoreboard(object):

    def __init__(self):
        # Check and init vis
        self.screenHeight = const.screenHeight
        self.screenWidth = const.screenWidth
        self.title = const.title
        self.debug = False
        self.running = True
        self.scores = None
        self.turns = []
        self.CATEGORY = ['Team', 'Processing', 'Networking', 'Total', 'S. City', 'M. City', 'L. City', 'ISP', 'DC']
        self.SPACING = [100, 100, 100, 100, 75, 75, 75, 50, 0]

        pygame.init()
        self.setup_pygame()
        self.run()

    def setup_pygame(self):
        pygame.display.set_caption(self.title)
        self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight))
        self.myfont = pygame.font.SysFont("monospace", 14)
        self.gameClock = pygame.time.Clock()

    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.display.quit()
                    pygame.quit()
                    sys.exit()
        if self.running:
            self.draw()

    def draw(self):
        self.screen.fill(const.backgroundColor)
        x, y = 10, 10
        for c in range(len(self.CATEGORY)):
            label = self.myfont.render(self.CATEGORY[c], 1, const.textColor)
            self.screen.blit(label, (x, y))
            x += self.SPACING[c]
        x = 10
        y += 20
        pygame.draw.line(self.screen, const.lineColor, (x, y), (self.screenWidth - x, y))
        y += 5
        if self.scores is not None:
            sorted_scores = self.sort_scores()
            for team_id in sorted_scores:
                for i in range(len(self.CATEGORY)):
                    num = self.myfont.render(str(self.scores[team_id][i]), 1, vis_const.TEAM_COLORS[team_id])
                    self.screen.blit(num, (x, y))
                    x += self.SPACING[i]
                x = 10
                y += 20
        x = 100
        y = 10
        pygame.draw.line(self.screen, const.lineColor, (x, y), (x, self.screenHeight - y))

        pygame.display.update()
        pygame.display.flip()

    def sort_scores(self):
        sorted_scores = []
        score_ids = [team_id for team_id, _ in self.scores.iteritems()]

        while len(score_ids) != 0:
            max_score_id = self.get_max_score(score_ids)
            score_ids.remove(max_score_id)
            sorted_scores.append(max_score_id)
            print(len(score_ids))
            print(score_ids)
            print(sorted_scores)

        return sorted_scores

    def get_max_score(self, score_ids):
        max_score_id = score_ids[0]
        for score_id in score_ids:
            if self.scores[score_id] >= self.scores[max_score_id]:
                max_score_id = score_id
        return max_score_id

    def add_turn(self, json):  # TODO FIX IT
        if self.scores is None:
            self.scores = {}
            for player in json:
                self.add_new_player(player["id"], player["teamName"])
        else:
            self.turns.append(json)

    def change_turn(self, turnNum):
        print("Change Turn")
        self.update_scores(int(turnNum))
        self.run()

    def update_scores(self, turnNum):
        # Reset scores
        for player in self.scores:
            self.scores[player][1] = 0
            self.scores[player][2] = 0
            self.scores[player][3] = 0
            self.scores[player][4] = 0
            self.scores[player][5] = 0
            self.scores[player][6] = 0
            self.scores[player][7] = 0
            self.scores[player][8] = 0

        # update
        for node in self.turns[turnNum]['map']:
            if node['owner'] != -1:
                self.scores[node['owner']][1] += node['processingPower']
                self.scores[node['owner']][2] += node['networkingPower']
                self.scores[node['owner']][3] += node['totalPower']
                if node['nodetype'] == "Small City":
                    self.scores[node['owner']][4] += 1
                if node['nodetype'] == "Medium City":
                    self.scores[node['owner']][5] += 1
                if node['nodetype'] == "Large City":
                    self.scores[node['owner']][6] += 1
                if node['nodetype'] == "ISP":
                    self.scores[node['owner']][7] += 1
                if node['nodetype'] == "Data Center":
                    self.scores[node['owner']][8] += 1

    def add_new_player(self, player_id, player_name):
        self.scores[player_id] = [player_name, 0, 0, 0, 0, 0, 0, 0, 0]

if __name__ == '__main__':
    score = Scoreboard(True)
