import requests
import os
from bs4 import BeautifulSoup
from time import sleep
requests.packages.urllib3.disable_warnings()


class KinomeX:
    def __init__(self, session_id, csrf_token):
        self._session_id = session_id
        self._csrf_token = csrf_token

        self._main_url = "https://kinome.simm.ac.cn"
        self._add_to_cart_url = self._main_url + "/en/products/predict-1/add/"
        self._submit_url = self._main_url + "/en/checkout/summary/"

        self._session = requests.Session()
    
    '''
    Upload file to submission list.
    '''
    def add_to_submission_list(self, file_path: str) -> None:
        _headers = {
            'Cookie': 'csrftoken=%s; sessionid=%s;' % (self._csrf_token, self._session_id),
            'Referer': 'https://kinome.simm.ac.cn/en/products/predict-1/?input-type=upload',
            'X-CSRFToken': self._csrf_token
        }
        file_name = os.path.basename(file_path)
        payload = {
            "quantity": 1,
            "variant": 2,
            "file_name": file_name,
            "molecule_value": None,
            "molecule_name": ""
        }
        files = [
            ('upload_file', (file_name, open(file_path, 'rb'), 'text/plain'))
        ]
        self._session.post(url=self._add_to_cart_url, data=payload,
                           files=files, headers=_headers, verify=False)

    '''
    Submit all files in submission list.
    '''
    def submit(self) -> None:
        _headers = {
            'Cookie': 'csrftoken=%s; sessionid=%s;' % (self._csrf_token, self._session_id),
            'Referer': 'https://kinome.simm.ac.cn/en/account/'
        }
        self._session.get(self._submit_url, headers=_headers, verify=False)

        
    '''
    Upload file to submission list and submit it.
    '''
    def upload_one(self, file_path: str) -> None:
        self.add_to_submission_list(file_path)
        print("%s UPLOADED." % file_path)
        self.submit()
        print("Submit 1 file.")

    '''
    A function used to walk file under a specific directory.
    '''
    def _walk_file(self, file: str) -> None:
        file_list = []
        for root, dirs, files in os.walk(file):

            # root: current directory
            # dirs: subdirectories under current directory [list]
            # files: files under current directory

            # walking all files
            for f in files:
                file_list.append(os.path.join(root, f))

            # walking all subdirectories
            # for d in dirs:
            #     print(os.path.join(root, d))
        return file_list

    '''
    Upload all files and submit.
    '''
    def upload_all(self, directory: str) -> None:
        file_list = self._walk_file(directory)
        i = 0
        for file in file_list:
            i += 1
            self.add_to_submission_list(file)
            print("%s UPLOADED." % file)
            if i == 5:
                self.submit()
                print("Submit 5 files.")
                i = 0
        if i != 0:
            self.submit()
            print("Submit %d files." % i)
        print("Submit all %d files!" % len(file_list))

    '''
    Download all molecule files in one record.
    '''
    def download_molecules_from_record(self, url: str, file_path: str) -> None:
        _headers = {
            'Cookie': 'csrftoken=%s; sessionid=%s;' % (self._csrf_token, self._session_id)
        }
        r = self._session.get(url, headers=_headers, verify=False)

        soup_page = BeautifulSoup(r.text, 'html.parser')
        rows = soup_page.find_all(class_="table__order")
        for row in rows:
            molecule_name = row.find(class_="row").find_all(
                class_="order-details__product__description")[0].span.text
            results_link = "https://kinome.simm.ac.cn" + row.find(class_="row").find_all(
                class_="order-details__product__description")[2].span.a['href']
            figures_link = "https://kinome.simm.ac.cn" + row.find(class_="row").find_all(
                class_="order-details__product__description")[4].find_all("a")[1]['href']
            self.download_file(results_link, "%s/%s_results.zip" %
                               (file_path, molecule_name))
            print("%s download completed!" % "%s/%s_results.zip" %
                  (file_path, molecule_name))
            # sleep(3)
            self.download_file(figures_link, "%s/%s_figures.zip" %
                               (file_path, molecule_name))
            print("%s download completed!" % "%s/%s_figures.zip" %
                  (file_path, molecule_name))
            # sleep(3)

    '''
    Function used to download file from url to a local file.
    '''
    def download_file(self, url: str, file_path: str) -> None:
        _headers = {
            'Cookie': 'csrftoken=%s; sessionid=%s;' % (self._csrf_token, self._session_id)
        }
        with requests.get(url, headers=_headers, verify=False) as r:
            with open(file_path, 'wb') as f:
                f.write(r.content)

    '''
    Download all molecules results and figures.
    '''
    def download_all(self, file_path: str) -> None:
        _headers = {
            'Cookie': 'csrftoken=%s; sessionid=%s;' % (self._csrf_token, self._session_id)
        }
        r = self._session.get("https://kinome.simm.ac.cn/en/account/?page=1",
                              headers=_headers, verify=False)
        soup_main = BeautifulSoup(r.text, 'html.parser')
        last_page_number = int(soup_main.select(
            ".last a")[0]['href'].split("=")[-1])

        for i in range(last_page_number):
            r = self._session.get("https://kinome.simm.ac.cn/en/account/?page=%s" % str(i+1),
                                  headers=_headers, verify=False)
            soup_page = BeautifulSoup(r.text, 'html.parser')
            detail_links = soup_page.find_all("a", {"class": "link--styled"})
            for detail_element in detail_links:
                detail_link = detail_element['href']
                self.download_molecules_from_record(
                    "https://kinome.simm.ac.cn" + detail_link, file_path)


# k = KinomeX("YOUR_SESSIONID",
            # "YOUR_CRSF_TOKEN")
# k.upload_one("/path/to/your.txt")
# k.upload_all("/path/to/your/directory")
# k.download_all("/path/to/your/directory")
