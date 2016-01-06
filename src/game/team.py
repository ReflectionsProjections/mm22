from character import Character

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
        for i in range(len(characters)):
            try:
                self.characters[i] = Character(i, characters[i]['characterName'], characters[i]['classId'])
            except KeyError:
                self.character[i] = Character(i)

    def toJson(self):
        """ Returns information about the team as a json
        :return json: (json) 
        """

        json = {}
        for character in self.characters:
            json[character.characterId] = character.toJson()

        return json
