import json

class Command:
    def __init__(self, payload):
        self.topic = payload["topic"]
        self.options = payload["options"]

    def as_dict(self):
        return {
            'topic': self.topic,
            'options': self.options
        }

    def to_json(self):
        return json.dumps(self.as_dict())

class SpecialCommand(Command):
    def __init__(self, payload):
        super().__init__(payload)

class MovementCommand(Command):
    def __init__(self, payload):
        super().__init__(payload)