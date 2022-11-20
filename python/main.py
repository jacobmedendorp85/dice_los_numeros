

from copy import deepcopy
import pandas as pd
from pprint import pp as pp

from die import DieD6, D6Die
from rollsim import RollSim
from gsheets.gsheets import GSheet

GSHEET = GSheet()


DICE_LIST = []

class UnknownDieError(Exception):
    pass


def get_die_by_name(name):

    for die in DICE_LIST:
        if die.name == name:
            return die

    raise UnknownDieError("Unable to find die with name %s" % name)


def roll_dice(
        attack_die1=None,
        defense_die1=None,
        attack_die2=None,
        defense_die2=None,
        ac=None, 
        crit_threshold=None, 
        attack_modifier=None,
        defense_modifier=None,
        output_wks=None
    ):
    
    attack_die1 = attack_die1
    defense_die1 = defense_die1
    attack_die2 = attack_die2
    defense_die2 = defense_die2
    ac = ac
    crit_threshold = crit_threshold
    attack_modifier = attack_modifier
    defense_modifier = defense_modifier
    output_wks = output_wks
    
    sims = []
    hits = []
    crits = []
    
    i = 1

    bigole_dict = {
        'attack_dice': [],
        'defense_dice': [],
        'attack_dice_alts': [],
        'defense_dice_alts': []
    }

    for attack_face1 in attack_die1.faces:
        attack_die1_copy = deepcopy(attack_die1)
        attack_die1_copy.set_active_face(attack_face1)
        bigole_dict['attack_dice'].append(attack_die1_copy)

    if attack_die2:
        for attack_face2 in attack_die2.faces:
            attack_die2_copy = deepcopy(attack_die2)
            attack_die2_copy.set_active_face(attack_face2)
            bigole_dict['attack_dice_alts'].append(attack_die2_copy)

    if defense_die1:
        for defense_face1 in defense_die1.faces:
            defense_die1_copy = deepcopy(defense_die1)
            defense_die1_copy.set_active_face(defense_face1)
            bigole_dict['defense_dice'].append(defense_die1_copy)

    if defense_die2:
        for defense_face2 in defense_die2.faces:
            defense_die2_copy = deepcopy(defense_die2)
            defense_die2_copy.set_active_face(defense_face2)
            bigole_dict['defense_dice_alts'].append(defense_die2_copy)
            
    
    for attack in bigole_dict['attack_dice']:
        for attack_alt in bigole_dict['attack_dice_alts']:
            for defense in bigole_dict['defense_dice']:
                for defense_alt in bigole_dict['defense_dice_alts']:
                    sim = RollSim(
                        ac=ac, 
                        crit_threshold=crit_threshold, 
                        attack_die=attack,
                        attack_die_alt=attack_alt,
                        defense_die=defense,
                        defense_die_alt=defense_alt,
                        attack_modifier=attack_modifier,
                        defense_modifier=defense_modifier,
                        sim_number=i)
                    sims.append(sim)
                    i += 1


    msg = "=====RUNNING SIMULATION====="
    print(msg)

    for sim in sims:
        sim.calculate()
        
        if sim.hit == True:
            hits.append(sim)

        if sim.crit == True:
            crits.append(sim)

    write_google_sheet(sims, ac, crit_threshold, hits, crits, output_wks)


def write_google_sheet(sims, ac, crit_threshold, hits, crits, output_wks):

    hit_percentage = float(len(hits)) / float(len(sims))
    hit_percentage = hit_percentage * 100
    hit_percentage = round(hit_percentage, 2)

    crit_percentage = float(len(crits)) / float(len(sims))
    crit_percentage = crit_percentage * 100
    crit_percentage = round(crit_percentage, 2)
    
    

    GSHEET.clear_wks(output_wks)
    summary = []

    summary.append(
        {
            'Stat': "AC",
            'Value': ac,
        }
    )
    summary.append(
        {
            'Stat': "Crit Threshold",
            'Value': crit_threshold,
        }
    )
    summary.append(
        {
            'Stat': "Total Number of Sims Rolls",
            'Value': len(sims),
        }
    )
    summary.append(
        {
            'Stat': "Number of Possible Hits",
            'Value': len(hits),
        }
    )
    summary.append(
        {
            'Stat': "Hit Percentage of Total",
            'Value': str(hit_percentage) + "%",
        }
    )
    summary.append(
        {
            'Stat': "Number of Possible Crits",
            'Value': len(crits),
        }
    )
    summary.append(
        {
            'Stat': "Crit Percentage of Total",
            'Value': str(crit_percentage) + "%",
        }
    )

    summary_df = pd.DataFrame(summary)
    GSHEET.write_to_wks(str(output_wks), summary_df, (1,1))

    data_list = []

    for sim in sims:

        data_dict = {}
        data_dict['Simulation Number'] = sim.sim_number
        data_dict['Attack Die 1 Name'] = sim.attack_die.name
        data_dict['Attack Die 1 Number'] = sim.attack_die.active_face['number']
        data_dict['Attack Die 1 Pips'] = sim.attack_die.active_face['pips']
        if sim.attack_die_alt:
            data_dict['Attack Die 2 Name'] = sim.attack_die_alt.name
            data_dict['Attack Die 2 Number'] = sim.attack_die_alt.active_face['number']
            data_dict['Attack Die 2 Pips'] = sim.attack_die_alt.active_face['pips']
        if sim.defense_die:
            data_dict['Defense Die 1 Name'] = sim.defense_die.name
            data_dict['Defense Die 1 Number'] = sim.defense_die.active_face['number']
            data_dict['Defense Die 1 Pips'] = sim.defense_die.active_face['pips']
        if sim.defense_die_alt:
            data_dict['Defense Die 2 Name'] = sim.defense_die_alt.name
            data_dict['Defense Die 2 Number'] = sim.defense_die_alt.active_face['number']
            data_dict['Defense Die 2 Pips'] = sim.defense_die_alt.active_face['pips']
        if sim.attack_modifier:
            data_dict['Attack Modifier'] = sim.attack_modifier
        if sim.defense_modifier:
            data_dict['Defense Modifier'] = sim.defense_modifier
        data_dict['Attack Total'] = sim.attack_value
        data_dict['AC'] = sim.ac
        data_dict['Pips Total'] = sim.pips
        data_dict['Crit Threshold'] = sim.crit_threshold

        data_list.append(data_dict)

    df = pd.DataFrame(data_list)
    GSHEET.write_to_wks(str(output_wks), df, (10,1))
    

def get_dice():

    dice_dicts = GSHEET.read_dice_config()

    for dice_dict in dice_dicts:
        d6_die = D6Die(dice_dict['name'], dice_dict['values'], dice_dict['pips'])
        DICE_LIST.append(d6_die)


def roll_from_sheet():


    wks = GSHEET.get_wks('Dice Setup')

    roll_df = wks.get_as_df(has_header=True, start="A10", end="I11")

    attack_1 = roll_df["Attack Die 1"][0]
    attack_2 = roll_df["Attack Die 2"][0]
    attack_modifier = roll_df["Attack Modifier"][0]
    if attack_modifier == 'none':
        attack_modifier = None
    defense_1 = roll_df["Defense Die 1"][0]
    defense_2 = roll_df["Defense Die 2"][0]
    defense_modifier = roll_df["Defense Modifier"][0]
    if defense_modifier == 'none':
        defense_modifier = None
    output_wks = roll_df["Output WKS"][0]
    ac = roll_df["AC"][0]
    crit_threshold = roll_df["Crit Threshold"][0]

    # roll_dice(
    #     attack_die1=get_die_by_name(attack_1),
    #     defense_die1=get_die_by_name(defense_1),
    #     attack_die2=get_die_by_name(attack_2),
    #     defense_die2=get_die_by_name(defense_2),
    #     ac=ac,
    #     crit_threshold=crit_threshold,
    #     attack_modifier=attack_modifier,
    #     defense_modifier=defense_modifier,
    #     output_wks=output_wks
    # )

    roll_sims(
        attack_die1=get_die_by_name(attack_1),
        defense_die1=get_die_by_name(defense_1),
        attack_die2=get_die_by_name(attack_2),
        defense_die2=get_die_by_name(defense_2),
        ac=ac,
        crit_threshold=crit_threshold,
        attack_modifier=attack_modifier,
        defense_modifier=defense_modifier,
        output_wks=output_wks
    )

def roll_sims(
        attack_die1=None,
        defense_die1=None,
        attack_die2=None,
        defense_die2=None,
        ac=None, 
        crit_threshold=None, 
        attack_modifier=None,
        defense_modifier=None,
        output_wks=None
    ):

    sims = []
    hits = []
    crits = []
    
    i = 1

    bigole_dict = {
        'attack_dice': [],
        'defense_dice': [],
        'attack_dice_alts': [],
        'defense_dice_alts': []
    }

    for attack_face1 in attack_die1.faces:
        attack_die1_copy = deepcopy(attack_die1)
        attack_die1_copy.set_active_face(attack_face1)
        bigole_dict['attack_dice'].append(attack_die1_copy)

    if attack_die2:
        for attack_face2 in attack_die2.faces:
            attack_die2_copy = deepcopy(attack_die2)
            attack_die2_copy.set_active_face(attack_face2)
            bigole_dict['attack_dice_alts'].append(attack_die2_copy)

    if defense_die1:
        for defense_face1 in defense_die1.faces:
            defense_die1_copy = deepcopy(defense_die1)
            defense_die1_copy.set_active_face(defense_face1)
            bigole_dict['defense_dice'].append(defense_die1_copy)

    if defense_die2:
        for defense_face2 in defense_die2.faces:
            defense_die2_copy = deepcopy(defense_die2)
            defense_die2_copy.set_active_face(defense_face2)
            bigole_dict['defense_dice_alts'].append(defense_die2_copy)

    if attack_modifier and defense_modifier:
        for attack in bigole_dict['attack_dice']:
            for attack_alt in bigole_dict['attack_dice_alts']:
                for defense in bigole_dict['defense_dice']:
                    for defense_alt in bigole_dict['defense_dice_alts']:
                        sim = RollSim(
                            ac=ac, 
                            crit_threshold=crit_threshold, 
                            attack_die=attack,
                            attack_die_alt=attack_alt,
                            defense_die=defense,
                            defense_die_alt=defense_alt,
                            attack_modifier=attack_modifier,
                            defense_modifier=defense_modifier,
                            sim_number=i)
                        sims.append(sim)
                        i += 1
    elif attack_modifier and not defense_modifier:
        for attack in bigole_dict['attack_dice']:
            for attack_alt in bigole_dict['attack_dice_alts']:
                for defense in bigole_dict['defense_dice']:
                    sim = RollSim(
                        ac=ac, 
                        crit_threshold=crit_threshold, 
                        attack_die=attack,
                        attack_die_alt=attack_alt,
                        defense_die=defense,
                        attack_modifier=attack_modifier,
                        sim_number=i)
                    sims.append(sim)
                    i += 1
    elif not attack_modifier and defense_modifier:
        for attack in bigole_dict['attack_dice']:
            for defense in bigole_dict['defense_dice']:
                for defense_alt in bigole_dict['defense_dice_alts']:
                    sim = RollSim(
                        ac=ac, 
                        crit_threshold=crit_threshold, 
                        attack_die=attack,
                        defense_die=defense,
                        defense_die_alt=defense_alt,
                        defense_modifier=defense_modifier,
                        sim_number=i)
                    sims.append(sim)
                    i += 1
    elif not attack_modifier and not defense_modifier:
        for attack in bigole_dict['attack_dice']:
            for defense in bigole_dict['defense_dice']:
                sim = RollSim(
                    ac=ac, 
                    crit_threshold=crit_threshold, 
                    attack_die=attack,
                    defense_die=defense,
                    sim_number=i)
                sims.append(sim)
                i += 1
    elif attack_die1 and attack_die_2 and not defense_die1:
        for attack in bigole_dict['attack_dice']:
            for attack_alt in bigole_dict['attack_dice_alts']:
                sim = RollSim(
                    ac=ac, 
                    crit_threshold=crit_threshold, 
                    attack_die=attack,
                    attack_die_alt=attack_alt,
                    attack_modifier=attack_modifier,
                    sim_number=i)
                sims.append(sim)
                i += 1

    msg = "=====RUNNING SIMULATION====="
    print(msg)

    for sim in sims:
        sim.calculate()
        
        if sim.hit == True:
            hits.append(sim)

        if sim.crit == True:
            crits.append(sim)

    write_google_sheet(sims, ac, crit_threshold, hits, crits, output_wks)


if __name__ == "__main__":
    get_dice()
    roll_from_sheet()
    print("All done!")
