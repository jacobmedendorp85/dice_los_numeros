import os
import pygsheets


class GSheet(object):

    def __init__(self) -> None:

        self.credentials_path = self.get_credentials_path()
        self.gc = pygsheets.authorize(service_file=self.credentials_path)

    def get_credentials_path(self):

        rel_path = 'service_account_credentials.json'
        dirname, filename = os.path.split(__file__)
        credentials_path = os.path.join(dirname, rel_path)
        return credentials_path


if __name__ == "__main__":
    gsheet = GSheet()
