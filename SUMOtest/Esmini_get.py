import requests
from os import path
from zipfile import ZipFile
from io import BytesIO


def download_Esmini_getBinPath():
    r = requests.get("https://github.com/esmini/esmini/releases/tag/v2.31.9")
    version = r.url.split("/")[-1]
    print(version)

    esmini_path = "esmini_{}".format(version)
    current_path = path.abspath(path.dirname(__file__))
    target_esmini_path = path.join(current_path, esmini_path)
    target_esmini_bin_path = path.join(current_path, esmini_path, "esmini", "bin")
    print(target_esmini_bin_path)
    # path.abspath(path.join(self.storage_prefix, rel_path))

    # if not path.exists(self._bin_path(self._esmini_path(version))):
    #             return self._download_esmini(version)

    if not path.exists(target_esmini_bin_path):
        archive_name = "esmini-bin_win_x64.zip"
        
        try:
            r = requests.get("https://github.com/esmini/esmini/releases/download/v2.31.9/esmini-bin_Windows.zip")

            with ZipFile(BytesIO(r.content), "r") as zipObj:
                zipObj.extractall(target_esmini_path)
        except requests.exceptions.ConnectionError:
            False
    
    return target_esmini_bin_path
