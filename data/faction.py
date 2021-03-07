from data.states import States


class Faction(object):
    def __init__(self, faction_id, name, link):
        self.faction_id = faction_id
        self.name = name
        self.link = link
        self.message = 0
        self.recovering = States()
        self.active = States()
        self.pending = States()
        self.systems = 0
        self.scaned = 0
        self.expansion_warning = list()
        self.mild_warning = list()
        self.high_warning = list()
        self.not_control = list()
        
    def set_recovering(self, data):
        states = data.split('|')
        for state in states:
            if len(state) > 0 and state != 'None':
                amount = getattr(self.recovering, state)
                setattr(self.recovering, state, amount + 1)
    
    def set_active(self, data):
        states = data.split('|')
        for state in states:
            if len(state) > 0 and state != 'None':
                amount = getattr(self.active, state)
                setattr(self.active, state, amount + 1)
    
    def set_pending(self, data):
        states = data.split('|')
        for state in states:
            if len(state) > 0 and state != 'None':
                amount = getattr(self.pending, state)
                setattr(self.pending, state, amount + 1)
    

