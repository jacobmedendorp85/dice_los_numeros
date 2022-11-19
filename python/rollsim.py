class RollSim(object):

    def __init__(self, 
        ac=None, 
        crit_threshold=None, 
        attack_die=None,
        defense_die=None,
        attack_die_alt=None,
        defense_die_alt=None,
        attack_modifier=None,
        defense_modifier=None,
        sim_number=None
    ):

        self.ac = ac
        self.crit_threshold = crit_threshold
        self.attack_die = attack_die
        self.defense_die = defense_die
        self.attack_die_alt = attack_die_alt
        self.defense_die_alt = defense_die_alt
        self.attack_modifier = attack_modifier
        self.defense_modifier = defense_modifier
        self.sim_number = sim_number

        self.attack_value = None
        self.hit = None
        self.pips = None
        self.crit = None

        self.rolled_dice = []

        self.rolled_dice.append(self.attack_die)
        self.rolled_dice.append(self.defense_die)
        if self.attack_die_alt:
            self.rolled_dice.append(self.attack_die_alt)
        if self.defense_die_alt:
            self.rolled_dice.append(self.defense_die_alt)

    def add_numbers(self):

        attack_num = self.attack_die.active_face['number']
        if self.attack_die_alt:
            attack_alt_num = self.attack_die_alt.active_face['number']
        
        defense_num = self.defense_die.active_face['number']
        if self.defense_die_alt:
            defense_alt_num = self.defense_die_alt.active_face['number']

        if self.attack_modifier == 'adv':
            attack_num = max(attack_num, attack_alt_num)

        elif self.attack_modifier == 'dis':
            attack_num = min(attack_num, attack_alt_num)

        if self.defense_modifier == 'adv':
            defense_num = max(defense_num, defense_alt_num)

        elif self.defense_modifier == 'dis':
            defense_num = min(defense_num, defense_alt_num)
        
        self.attack_value = attack_num + defense_num

        if self.attack_value >= self.ac:
            self.hit = True
        else:
            self.hit = False
        
    def add_pips(self):

        attack_pips_num = self.attack_die.active_face['pips']
        if self.attack_die_alt:
            attack_pips_num_alt = self.attack_die_alt.active_face['pips']
        
        defense_pips_num = self.defense_die.active_face['pips']
        if self.defense_die_alt:
            defense_pips_alt_num = self.defense_die_alt.active_face['pips']

        if self.attack_modifier == 'adv':
            attack_pips_num = max(attack_pips_num, attack_pips_num_alt)

        elif self.attack_modifier == 'dis':
            attack_pips_num = min(attack_pips_num, attack_pips_num_alt)

        if self.defense_modifier == 'adv':
            defense_pips_num = min(defense_pips_num, defense_pips_alt_num)

        elif self.defense_modifier == 'dis':
            defense_pips_num = max(defense_pips_num, defense_pips_alt_num)

        self.pips = attack_pips_num + defense_pips_num

        if self.hit == True and self.pips >= self.crit_threshold:
            self.crit = True
        else:
            self.crit = False

        
    def calculate(self):
        self.add_numbers()
        self.add_pips()

    def report(self):

        msg = "Roll Results.... "
        msg += "\nDice Rolled: "

        for die in self.rolled_dice:
            msg = msg + "\n    %s - %s" % (die.die_type, die.active_face)

        msg += "\nAttack Modifier: %s" % self.attack_modifier 
        msg += "\nDefense Modifier: %s" % self.defense_modifier

        print(msg)