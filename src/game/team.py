from src.game.character import Character


class Team:

    def __init__(self, id, name, characters):
        """ Init a team based off a team id and a list of characters
        - characters should be a list of json objects that each contain the key
        "characterName" and ""classId". If it doesn't it will just set it to default

        :param id: (int) id of the team
        :param name: (string) name of team
        :param characters: (list) list of characters to create
        """

        self.name = name
        self.characters = []
        self.id = id
        for i in range(len(characters)):
            try:
                self.characters.append(Character(id + i, characters[i]['characterName'], characters[i]['classId']))
            except KeyError:
                self.characters.append(Character(id + i))

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
