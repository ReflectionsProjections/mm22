from src.game.character import Character


class Team:

    total_teams = 0

    @staticmethod
    def get_new_team_id():
        Team.total_teams += 1
        return Team.total_teams

    @staticmethod
    def remove_all_teams():
        Team.total_teams = 0

    ########################

    def __init__(self, name):
        self.name = name
        self.characters = []
        self.id = Team.get_new_team_id()

    def add_character(self, json):
        new_character = Character()

        if new_character.init(json) is True:
            self.characters.append(new_character)
            return new_character

        return None

    def get_character(self, id=None, name=None):
        if id is None and name is None:
            return None

        for character in self.characters:
            if character.name == name or character.id == id:
                return character

    def size(self):
        return len(self.characters)

    def toJson(self):
        """ Returns information about the team as a json
        :return json: (json) 
        """

        json = {}
        json['teamName'] = self.name
        json['id'] = self.id
        json['characters'] = []
        for character in self.characters:
            json['characters'].append(character.toJson())

        return json
