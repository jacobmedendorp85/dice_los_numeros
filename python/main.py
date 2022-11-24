

from die import D6Die
from dice_distribution import DiceDistribution
from gsheets.gsheets import GSheet


class UnknownDieError(Exception):
    pass


class DiceSetup(object):
    _ac_start = 0
    _crit_start = 3

    def __init__(self, gsheet) -> None:
        self._dice_list = []
        self.attack_die_primary = None
        self.attack_die_secondary = None
        self.attack_modifier = None
        self.defense_die_primary = None
        self.defense_die_secondary = None
        self.defense_modifier = None
        self.output_wks = None
        self.ac_range = None
        self.crit_range = None
        self._gsheet = gsheet
        self.get_dice()
        self.get_parameters()

    def get_die_by_name(self, name):
        for die in self._dice_list:
            if die.name == name:
                return die

    def get_dice(self):

        dice_dicts = self._gsheet.read_dice_config()

        for dice_dict in dice_dicts:
            d6_die = D6Die(dice_dict['name'], dice_dict['values'], dice_dict['pips'])
            self._dice_list.append(d6_die)

    def get_parameters(self):

        params = self._gsheet.read_parameters()

        attack_die_primary_name = params.get("Primary Attack")
        self.attack_die_primary = self.get_die_by_name(attack_die_primary_name)
        attack_die_secondary_name = params.get("Secondary Attack")
        self.attack_die_secondary = self.get_die_by_name(attack_die_secondary_name)
        attack_mod = params.get("Attack Modifier")
        if attack_mod != 'none':
            self.attack_modifier = attack_mod
        
        defense_die_primary_name = params.get("Primary Defense")
        self.defense_die_primary = self.get_die_by_name(defense_die_primary_name)
        defense_die_secondary_name = params.get("Secondary Defense")
        self.defense_die_secondary = self.get_die_by_name(defense_die_secondary_name)
        defense_mod = params.get("Defense Modifier")
        if defense_mod != 'none':
            self.defense_modifier = defense_mod
        self.output_wks = params.get("Output WKS")
        ac = params.get("AC")
        self.ac_range = range(self._ac_start, ac + 1)
        crit = params.get("Crit Threshold")
        self.crit_range = range(self._crit_start, crit + 1)


def upload_distribution_to_gsheets(dice_distribution, gsheet, output_wks):

    wks = gsheet.get_wks(output_wks)
    wks.clear()

    row = 1
    col = 1

    msg = "Writing Data to Output WKS [%s]" % output_wks
    print(msg)

    msg = "Uploading Parameters Data..."
    print(msg)
    dice_data_frame = dice_distribution.data_frame
    gsheet.write_to_wks(wks, dice_data_frame, (row,col))

    row += len(dice_data_frame.index) + 2

    # Write all the summaries first
    for crit, ac_distro in dice_distribution.crit_distributions.items():
        msg = "Uploading Summary Data for Crit Threshold %s..." % crit
        print(msg)
        ac_data_frame = ac_distro.data_frame
        gsheet.write_to_wks(wks, ac_data_frame, (row,col), copy_head=False)
        row += len(ac_data_frame.index) + 2
    
    for crit, ac_distro in dice_distribution.crit_distributions.items():
        for ac, face_distro in ac_distro.face_distributions.items():
            msg = "Uploading All Results for Crit Threshold %s and AC %s..." % (crit, ac)
            print(msg)
            face_data_frame = face_distro.data_frame
            gsheet.write_to_wks(wks, face_data_frame, (row,col))
            row += len(face_data_frame.index) + 2


def main():

    gsheet = GSheet()
    dice_setup = DiceSetup(gsheet)

    dice_distribution = DiceDistribution(dice_setup)

    upload_distribution_to_gsheets(dice_distribution, gsheet, dice_setup.output_wks)

    print("All done!")

if __name__ == "__main__":
    main()
    
