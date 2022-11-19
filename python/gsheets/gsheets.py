import os
import pygsheets


class GSheet(object):
    _SHEET_TITLE = 'Dice Los Numeros'
    _CONFIG_WKS = 'Dice Setup'
    def __init__(self) -> None:

        self.credentials_path = self.get_credentials_path()
        self.gc = pygsheets.authorize(service_file=self.credentials_path)
        self.sheet = self.gc.open(self._SHEET_TITLE)

    def get_credentials_path(self):

        rel_path = 'service_account_credentials.json'
        dirname, filename = os.path.split(__file__)
        credentials_path = os.path.join(dirname, rel_path)
        return credentials_path

    def get_wks(self, sheet_name):
        return self.sheet.worksheet_by_title(sheet_name)

    def write_to_sheet(self, sheet_name, dataframe, pos):
        wks = self.get_wks(sheet_name)
        wks.set_dataframe(dataframe, pos)

    def read_dice_config(self):
        print("Getting dice")

        dice_list = []
        wks = self.get_wks(self._CONFIG_WKS)

        df = wks.get_as_df(has_header=True, start="B1")

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


if __name__ == "__main__":
    gsheet = GSheet()
