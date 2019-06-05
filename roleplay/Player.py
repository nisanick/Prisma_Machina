from web import Web


class Player:
    
    def __init__(self, user_id, items):
        self.user_id = user_id
        self.melee = None
        self.utility = []
        self.back = None
        self.heavy = None
        self.chest = None
        self.gloves = None
        self.defense = None
        self.nap = None
        self.light = None
        self.disposable1 = None
        self.disposable2 = None
        self.disposable3 = None
        self.disposable4 = None
        self.medium = None
        self.head = None
        self.drone = None
        self.shoes = None
        self.pet = None
        
        for item in items:
            slot = item["Slot"]
            piece = (item['Item ID'], item["Item"])
            if slot == 'melee':
                self.melee = piece
            elif slot == 'utility':
                add_utility(self.utility, piece)
            elif slot == 'back':
                self.back = piece
            elif slot == 'heavy':
                self.heavy = piece
            elif slot == 'chest':
                self.chest = piece
            elif slot == 'gloves':
                self.gloves = piece
            elif slot == 'defense':
                self.defense = piece
            elif slot == 'light':
                self.light = piece
            elif slot == 'disposable1':
                self.disposable1 = piece
            elif slot == 'disposable2':
                self.disposable2 = piece
            elif slot == 'disposable3':
                self.disposable3 = piece
            elif slot == 'disposable4':
                self.disposable4 = piece
            elif slot == 'medium':
                self.medium = piece
            elif slot == 'head':
                self.head = piece
            elif slot == 'shoes':
                self.shoes = piece
                
    def have_util(self, util):
        for item_id, name in self.utility:
            if name == util:
                return True
        return False
    
    async def use_item(self, number):
        from data.links import item_use_link
        link = item_use_link
        if number == 1:
            item = self.disposable1[0]
            self.disposable1 = None
        elif number == 2:
            item = self.disposable2[0]
            self.disposable2 = None
        elif number == 3:
            item = self.disposable3[0]
            self.disposable3 = None
        elif number == 4:
            item = self.disposable4[0]
            self.disposable4 = None
        else:
            return
        args = {
            'discord_id': self.user_id,
            'item_id': item
        }
        response = await Web.get_response(link, args)
    
    
def add_utility(colection, piece):
    name = piece[1]
    if name == 'Chaff Launcher':
        piece = (piece[0], 'chaff')
    elif name == 'Auto Field Maintenance Unit':
        piece = (piece[0], 'afmu')
    elif name == 'Environmental Layout Scanner':
        piece = (piece[0], 'els')
    elif name == 'Heat Sink Launcher':
        piece = (piece[0], 'hsl')
    elif name == 'Kill Warrant Scanner':
        piece = (piece[0], 'kws')
    elif name == 'Shield Cell Bank':
        piece = (piece[0], 'scb')
    elif name == 'Encryption Cracking Unit':
        piece = (piece[0], 'ecu')
    elif name == 'Holo-Me Decoy Projector':
        piece = (piece[0], 'hdp')
    elif name == 'Virtual Distortion Cloak':
        piece = (piece[0], 'vdc')
    elif name == 'Electronic Ghost Generator':
        piece = (piece[0], 'egg')

    colection.append(piece)

