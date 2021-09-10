
class States:
    def __init__(self):
        self.Incursion = 0
        self.Infested = 0
        self.Blight = 0
        self.Drought = 0
        self.Outbreak = 0
        self.InfrastructureFailure = 0
        self.NaturalDisaster = 0
        self.Revolution = 0
        self.ColdWar = 0
        self.TradeWar = 0
        self.PirateAttack = 0
        self.Terrorism = 0
        self.PublicHoliday = 0
        self.TechnologyLeap = 0
        self.HistoricEvent = 0
        self.Colonisation = 0
        self.War = 0
        self.CivilWar = 0
        self.Election = 0
        self.Retreat = 0
        self.Expansion = 0
        
        self.Lockdown = 0
        self.CivilUnrest = 0
        self.CivilLiberty = 0
        
        self.Famine = 0
        self.Bust = 0
        self.Boom = 0
        self.Investment = 0
        
    def __str__(self):
        result = list()
        if self.Incursion > 0:
            result.append('Incursion'.format(self.Incursion))
        if self.Infested > 0:
            result.append('Infested'.format(self.Infested))
        if self.Blight > 0:
            result.append('Blight'.format(self.Blight))
        if self.Drought > 0:
            result.append('Drought'.format(self.Drought))
        if self.Outbreak > 0:
            result.append('Outbreak'.format(self.Outbreak))
        if self.InfrastructureFailure > 0:
            result.append('Infrastructure Failure'.format(self.InfrastructureFailure))
        if self.NaturalDisaster > 0:
            result.append('Natural Disaster'.format(self.NaturalDisaster))
        if self.Revolution > 0:
            result.append('Revolution'.format(self.Revolution))
        if self.ColdWar > 0:
            result.append('Cold War'.format(self.ColdWar))
        if self.TradeWar > 0:
            result.append('Trade War'.format(self.TradeWar))
        if self.PirateAttack > 0:
            result.append('Pirate Attack'.format(self.PirateAttack))
        if self.Terrorism > 0:
            result.append('Terrorist Attack'.format(self.Terrorism))
        if self.PublicHoliday > 0:
            result.append('Public Holiday'.format(self.PublicHoliday))
        if self.TechnologyLeap > 0:
            result.append('Technology Leap'.format(self.TechnologyLeap))
        if self.HistoricEvent > 0:
            result.append('Historic Event'.format(self.HistoricEvent))
        if self.Colonisation > 0:
            result.append('Colonisation'.format(self.Colonisation))
        if self.War > 0:
            result.append('War'.format(self.War))
        if self.CivilWar > 0:
            result.append('Civil War'.format(self.CivilWar))
        if self.Election > 0:
            result.append('Elections'.format(self.Election))
        if self.Retreat > 0:
            result.append('Retreat'.format(self.Retreat))
        if self.Expansion > 0:
            result.append('Expansion'.format(self.Expansion))
            
        if self.Lockdown > 0:
            result.append('Lockdown'.format(self.Lockdown))
        if self.CivilUnrest > 0:
            result.append('Civil Unrest'.format(self.CivilUnrest))
        if self.CivilLiberty > 0:
            result.append('Civil Liberty'.format(self.CivilLiberty))
            
        if self.Famine > 0:
            result.append('Famine'.format(self.Famine))
        if self.Bust > 0:
            result.append('Bust'.format(self.Bust))
        if self.Boom > 0:
            result.append('Boom'.format(self.Boom))
        if self.Investment > 0:
            result.append('Investment'.format(self.Investment))
        if self.Investment > 0:
            result.append('Investment'.format(self.Investment))
            
        if len(result) > 0:
            return "\n".join(result)
        else:
            return "None"
