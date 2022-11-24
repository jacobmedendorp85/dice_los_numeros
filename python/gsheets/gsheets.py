import os
import pygsheets


class GSheet(object):
    _SHEET_TITLE = 'Dice Los Numeros'
    _CONFIG_WKS = 'Dice Setup'
    
    def __init__(self) -> None:

        self.credentials_path = self.get_credentials_path()
        self.gc = pygsheets.authorize(service_file=self.credentials_path)
        self.sheet = self.gc.open(self._SHEET_TITLE)
        self.cfg_wks = self.get_wks(self._CONFIG_WKS)

    def get_credentials_path(self):

        rel_path = 'service_account_credentials.json'
        dirname, filename = os.path.split(__file__)
        credentials_path = os.path.join(dirname, rel_path)
        return credentials_path

    def get_wks(self, wks_name):
        return self.sheet.worksheet_by_title(wks_name)

    def clear_wks(self, wks_name):
        wks = self.get_wks(wks_name)
        wks.clear()

    def write_to_wks(self, wks_obj, dataframe, pos, copy_head=True):
        wks_obj.set_dataframe(dataframe, pos, copy_head=copy_head)

    def read_dice_config(self):
        dice_list = []

        df = self.cfg_wks.get_as_df(has_header=True, start="B1")

        atk_col = 0
        pip_col = 2

        num_of_dice = 6

        for die in range(1, num_of_dice+1):
            die_ser = df.iloc[0:6, atk_col:pip_col]
            die_index = (die_ser.columns)
            die_name = die_index.values[0]

            atk_col +=2
            pip_col +=2

            values = die_ser.iloc[0:6, 0].tolist()
            pips = die_ser.iloc[0:6, 1].tolist()

            die_dict = {
                'name': die_name,
                'values': values, 
                'pips': pips
                }
            dice_list.append(die_dict)

        return dice_list

    def read_parameters(self):

        param_dict = {}
        params_df = self.cfg_wks.get_as_df(has_header=True, start="A10", end="I11")

        for name, data in params_df.items():
            param_dict[name] = data[0]

        return param_dict


if __name__ == "__main__":
    gsheet = GSheet()

