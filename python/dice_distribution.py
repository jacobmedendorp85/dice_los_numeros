from copy import deepcopy as deepcopy
from pprint import pprint as pp

import pandas as pd


class UncalculatedError(Exception):
    pass


class SingleRoll(object):

    def __init__(self, 
        ac=None, 
        crit_threshold=None, 
        attack_die_primary=None,
        defense_die_primary=None,
        attack_die_secondary='',
        defense_die_secondary='',
        attack_modifier=None,
        defense_modifier=None,
        roll_index=None
    ):

        self.ac = ac
        self.crit_threshold = crit_threshold
        self.attack_die_primary = attack_die_primary
        self.defense_die_primary = defense_die_primary
        self.attack_die_secondary = attack_die_secondary
        self.defense_die_secondary = defense_die_secondary
        self.attack_modifier = attack_modifier
        self.defense_modifier = defense_modifier
        self.roll_index = roll_index

        self.attack_total = None
        self.hit = None
        self.pip_total = None
        self.crit = None

        self.rolled_dice = []

        self.rolled_dice.append(self.attack_die_primary)
        if self.defense_die_primary:
            self.rolled_dice.append(self.defense_die_primary)
        if self.attack_die_secondary:
            self.rolled_dice.append(self.attack_die_secondary)
        if self.defense_die_secondary:
            self.rolled_dice.append(self.defense_die_secondary)

    def add_numbers(self):

        attack_num = self.attack_die_primary.active_face['number']
        if self.attack_die_secondary:
            attack_alt_num = self.attack_die_secondary.active_face['number']
        
        defense_num = 0
        if self.defense_die_primary:
            defense_num = self.defense_die_primary.active_face['number']
        if self.defense_die_secondary:
            defense_alt_num = self.defense_die_secondary.active_face['number']

        if self.attack_modifier == 'adv':
            attack_num = max(attack_num, attack_alt_num)

        elif self.attack_modifier == 'dis':
            attack_num = min(attack_num, attack_alt_num)

        if self.defense_modifier == 'adv':
            defense_num = max(defense_num, defense_alt_num)

        elif self.defense_modifier == 'dis':
            defense_num = min(defense_num, defense_alt_num)
        
        self.attack_total = attack_num + defense_num

        if self.attack_total >= self.ac:
            self.hit = True
        else:
            self.hit = False
        
    def add_pips(self):

        attack_pips_num = self.attack_die_primary.active_face['pips']
        if self.attack_die_secondary:
            attack_pips_num_alt = self.attack_die_secondary.active_face['pips']
        
        defense_pips_num = 0
        if self.defense_die_primary:
            defense_pips_num = self.defense_die_primary.active_face['pips']
        if self.defense_die_secondary:
            defense_pips_alt_num = self.defense_die_secondary.active_face['pips']

        if self.attack_modifier == 'adv':
            attack_pips_num = max(attack_pips_num, attack_pips_num_alt)

        elif self.attack_modifier == 'dis':
            attack_pips_num = min(attack_pips_num, attack_pips_num_alt)

        if self.defense_modifier == 'adv':
            defense_pips_num = min(defense_pips_num, defense_pips_alt_num)

        elif self.defense_modifier == 'dis':
            defense_pips_num = max(defense_pips_num, defense_pips_alt_num)

        self.pip_total = attack_pips_num + defense_pips_num

        if self.hit == True and self.pip_total >= self.crit_threshold:
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

class DiceDistribution(object):

    def __init__(self, dice_setup) -> None:
        self._dice_setup = dice_setup
        self.crit_distributions = {}
        self.distribute_acs_for_crit_threshold()
        self.create_data_frame()

    def distribute_acs_for_crit_threshold(self):
        
        for crit_threshold in self._dice_setup.crit_range:
            ac_distribution = ArmorClassDistribution(self._dice_setup, crit_threshold)
            self.crit_distributions[crit_threshold] = ac_distribution

    def create_data_frame(self):

        data_list = []
        data_dict = {}
        data_dict['Attack Die Primary'] = self._dice_setup.attack_die_primary.name
        if self._dice_setup.attack_die_secondary:
            data_dict['Attack Die Secondary'] = self._dice_setup.attack_die_secondary.name
        data_dict['Attack Modifier'] = str(self._dice_setup.attack_modifier)
        
        if self._dice_setup.defense_die_primary:
            data_dict['Defense Die Primary'] = self._dice_setup.defense_die_primary.name
        if self._dice_setup.defense_die_secondary:
            data_dict['Defense Die Secondary'] = self._dice_setup.defense_die_secondary.name
        data_dict['Defense Modifier'] = str(self._dice_setup.defense_modifier)
        data_list.append(data_dict)

        self.data_frame = pd.DataFrame(data_list)


class ArmorClassDistribution(object):

    def __init__(self, dice_setup, crit_threshold) -> None:
        self._dice_setup = dice_setup
        self._crit_threshold = crit_threshold
        self.face_distributions = {}
        self.distribute_faces_for_ac()
        self.create_data_frame()

    def distribute_faces_for_ac(self):
        
        for ac in self._dice_setup.ac_range:
            face_distribution = FaceDistribution(self._dice_setup, ac, self._crit_threshold)
            self.face_distributions[ac] = face_distribution

    def create_data_frame(self):

        data_list = []

        for ac, distro in self.face_distributions.items():
            data_dict = {}
            data_dict['AC'] = ac
            data_dict['Crit Threshold'] = self._crit_threshold
            data_dict['Total Results'] = str(len(distro.all_results))
            data_dict['Hit Results'] = str(len(distro.hits))
            data_dict['Hit Rate'] = str(distro.hit_percentage)
            data_dict['Crit Results'] = str(len(distro.hits))
            data_dict['Crit Rate (Total)'] = str(distro.crit_percentage_of_total)
            data_dict['Crit Rate (Hits)'] = str(distro.crit_percentage_of_hits)
            

            data_list.append(data_dict)

        self.data_frame = pd.DataFrame(data_list)
        self.data_frame = self.data_frame.transpose().reset_index()
        #print(ac_data_frame)


class FaceDistribution(object):

    def __init__(self, dice_setup, ac, crit_threshold) -> None:
        
        self._dice_setup = dice_setup
        self._ac = ac
        self._crit_threshold = crit_threshold

        self._is_calculated = False
        self._all_results = []
        self._hits = []
        self._crits = []
        self.data_frame = None

        self._distro_dict = {
            'attack_dice': [],
            'defense_dice': [],
            'attack_dice_alts': [],
            'defense_dice_alts': []
        }

        self.add_dice_to_distro()
        self.setup_rolls()
        self.calculate_results()
        self.create_data_frame()

    @property
    def all_results(self):
        return self._all_results

    @property
    def hits(self):
        return self._hits

    @property
    def crits(self):
        return self._crits
    
    @property
    def faces_data_frame(self):
        return self._faces_data_frame

    @property
    def hit_percentage(self):

        if not self.is_calculated:
            raise UncalculatedError("Results have not yet been calculated")

        hit_percentage = 0.0
        if len(self._all_results) > 0:
            hit_percentage = float(len(self._hits)) / float(len(self._all_results))
        hit_percentage = hit_percentage * 100
        hit_percentage = round(hit_percentage, 2)
        return hit_percentage

    @property
    def crit_percentage_of_total(self):

        if not self.is_calculated:
            raise UncalculatedError("Results have not yet been calculated")

        crit_percentage = 0.0
        
        if len(self._all_results) > 0:
            crit_percentage = float(len(self._crits)) / float(len(self._all_results))
        crit_percentage = crit_percentage * 100
        crit_percentage = round(crit_percentage, 2)
        return crit_percentage

    @property
    def crit_percentage_of_hits(self):

        if not self.is_calculated:
            raise UncalculatedError("Results have not yet been calculated")

        crit_percentage = 0.0
        if len(self._hits) > 0:
            crit_percentage = float(len(self._crits)) / float(len(self._hits))
        crit_percentage = crit_percentage * 100
        crit_percentage = round(crit_percentage, 2)
        return crit_percentage

    @property
    def is_calculated(self):
        return self._is_calculated

    @property
    def attack_die_primary(self):
        return self._dice_setup.attack_die_primary

    @property
    def attack_die_secondary(self):
        return self._dice_setup.attack_die_secondary

    @property
    def defense_die_primary(self):
        return self._dice_setup.defense_die_primary

    @property
    def defense_die_secondary(self):
        return self._dice_setup.defense_die_secondary

    @property
    def ac(self):
        return self._ac

    @property
    def crit_threshold(self):
        return self._crit_threshold

    @property
    def attack_modifier(self):
        return self._dice_setup.attack_modifier

    @property
    def defense_modifier(self):
        return self._dice_setup.defense_modifier

    def add_die_faces_to_distro(self, die, die_type):

        for face in die.faces:
            die_copy = deepcopy(die)
            die_copy.set_active_face(face)
            self._distro_dict[die_type].append(die_copy)

    def add_dice_to_distro(self):

        self.add_die_faces_to_distro(self.attack_die_primary, 'attack_dice')        

        if self.attack_die_secondary:
            self.add_die_faces_to_distro(self.attack_die_secondary, 'attack_dice_alts')

        if self.defense_die_primary:
            self.add_die_faces_to_distro(self.defense_die_primary, 'defense_dice')

        if self.defense_die_secondary:
            self.add_die_faces_to_distro(self.defense_die_secondary, 'defense_dice_alts')

    def calculate_results(self):

        for result in self._all_results:
            result.calculate()

            if result.hit:
                self._hits.append(result)

            if result.crit:
                self._crits.append(result)
        
        self._is_calculated = True


    def setup_rolls(self):

        roll_num = 1

        # Rolling 4 dice
        if self.attack_modifier and self.defense_modifier:
            for attack in self._distro_dict['attack_dice']:
                for attack_alt in self._distro_dict['attack_dice_alts']:
                    for defense in self._distro_dict['defense_dice']:
                        for defense_alt in self._distro_dict['defense_dice_alts']:
                            result = SingleRoll(
                                ac=self.ac, 
                                crit_threshold=self.crit_threshold, 
                                attack_die_primary=attack,
                                attack_die_secondary=attack_alt,
                                defense_die_primary=defense,
                                defense_die_secondary=defense_alt,
                                attack_modifier=self.attack_modifier,
                                defense_modifier=self.defense_modifier,
                                roll_index=roll_num
                            )
                            self._all_results.append(result)
                            roll_num += 1
        
        # Rolling 2 attacks vs 1 defense
        elif self.attack_modifier and not self.defense_modifier:
            for attack in self._distro_dict['attack_dice']:
                for attack_alt in self._distro_dict['attack_dice_alts']:
                    for defense in self._distro_dict['defense_dice']:
                        result = SingleRoll(
                            ac=self.ac, 
                            crit_threshold=self.crit_threshold, 
                            attack_die_primary=attack,
                            attack_die_secondary=attack_alt,
                            defense_die_primary=defense,
                            attack_modifier=self.attack_modifier,
                            roll_index=roll_num
                        )
                        self._all_results.append(result)
                        roll_num += 1
        
        # Rolling 1 attack vs 2 defense
        elif not self.attack_modifier and self.defense_modifier:
            for attack in self._distro_dict['attack_dice']:
                for defense in self._distro_dict['defense_dice']:
                    for defense_alt in self._distro_dict['defense_dice_alts']:
                        result = SingleRoll(
                            ac=self.ac, 
                            crit_threshold=self.crit_threshold, 
                            attack_die_primary=attack,
                            defense_die_primary=defense,
                            defense_die_secondary=defense_alt,
                            defense_modifier=self.defense_modifier,
                            roll_index=roll_num
                        )
                        self._all_results.append(result)
                        roll_num += 1
        
        # Rolling 1 attack and 1 defense
        elif not self.attack_modifier and not self.defense_modifier:
            for attack in self._distro_dict['attack_dice']:
                for defense in self._distro_dict['defense_dice']:
                    result = SingleRoll(
                        ac=self.ac, 
                        crit_threshold=self.crit_threshold, 
                        attack_die_primary=attack,
                        defense_die_primary=defense,
                        roll_index=roll_num
                    )
                    self._all_results.append(result)
                    roll_num += 1
        
        # Rolling 2 attack and no defense (skill check)
        elif self.attack_die_primary and self.attack_die_secondary and not self.defense_die_primary:
            for attack in self._distro_dict['attack_dice']:
                for attack_alt in self._distro_dict['attack_dice_alts']:
                    result = SingleRoll(
                        ac=self.ac, 
                        crit_threshold=self.crit_threshold, 
                        attack_die_primary=attack,
                        attack_die_secondary=attack_alt,
                        attack_modifier=self.attack_modifier,
                        roll_index=roll_num
                    )
                    self._all_results.append(result)
                    roll_num += 1
    
    def create_data_frame(self):
        data_list = []

        for result in self._all_results:

            data_dict = {}
            data_dict['Result Number'] = result.roll_index
            data_dict['Die Name (Primary Attack)'] = result.attack_die_primary.name
            data_dict['Face (Primary Attack)'] = result.attack_die_primary.active_face['number']
            data_dict['Pips (Primary Attack)'] = result.attack_die_primary.active_face['pips']
            if result.attack_die_secondary:
                data_dict['Die Name (Secondary Attack)'] = result.attack_die_secondary.name
                data_dict['Face (Secondary Attack)'] = result.attack_die_secondary.active_face['number']
                data_dict['Pips (Secondary Attack)'] = result.attack_die_secondary.active_face['pips']
            if result.defense_die_primary:
                data_dict['Die Name (Primary Defense)'] = result.defense_die_primary.name
                data_dict['Face (Primary Defense)'] = result.defense_die_primary.active_face['number']
                data_dict['Pips (Primary Defense)'] = result.defense_die_primary.active_face['pips']
            if result.defense_die_secondary:
                data_dict['Die Name (Secondary Defense)'] = result.defense_die_secondary.name
                data_dict['Face (Secondary Defense)'] = result.defense_die_secondary.active_face['number']
                data_dict['Pips (Secondary Defense)'] = result.defense_die_secondary.active_face['pips']
            if result.attack_modifier:
                data_dict['Attack Modifier'] = result.attack_modifier
            if result.defense_modifier:
                data_dict['Defense Modifier'] = result.defense_modifier
            data_dict['Attack Total'] = result.attack_total
            data_dict['Pip Total'] = result.pip_total
            data_dict['AC'] = result.ac
            data_dict['Crit Threshold'] = result.crit_threshold

            data_list.append(data_dict)

        self.data_frame = pd.DataFrame(data_list)








