import os
import subprocess as sp
from datetime import date, datetime
import re
import ssl
import logging


logging.basicConfig(filename="./debug_logs/npmlite.log", level=logging.ERROR,
                    format="%(asctime)s:%(name)s:%(levelname)s:%(message)s")

ssl_logger = logging.getLogger("ManageSSL")


class ManageSSL:
    def __init__(self):
        self.newLine = '\n'
        self.tab = '\t'

    def generate_ssl(self, domain, email):
        request_test_cert = sp.getoutput(
            f'certbot certonly --nginx -n -d {domain} --agree-tos -m {email} --dry-run')

        if not 'The dry run was successful' in request_test_cert:
            return

        request_cert = sp.getoutput(
            f'certbot certonly --nginx -n -d {domain} --agree-tos -m {email}')

        if 'Certificate not yet due for renewal; no action taken' in request_cert:
            return 'Exists'

        regex = r'(?<=saved at:\s).*(?=)'
        cert_info = re.findall(regex, request_cert)
        ssl_path = {}
        if len(cert_info) == 2:
            ssl_path["ssl_cert_path"] = cert_info[0].strip()
            ssl_path["ssl_key_path"] = cert_info[1].strip()
            return ssl_path
        else:
            ssl_logger.error({"ERROR": f"Unable to request SSL certificate for {domain}"})
            return

    def delete_ssl(domain):
        delete_status = sp.getoutput(f'certbot delete --cert-name {domain} -n')
        if f'Deleted all files relating to certificate {domain}' in delete_status:
            return {"Success": f"SSL certificate deleted for {domain}"}
        else:
            ssl_logger.error({"ERROR": f"Unable to delete SSL certificate for {domain}"})
            return

    @staticmethod
    def renew_ssl():
        try:
            sp.call(f'certbot renew --quiet', shell=True)
        except Exception as e:
            ssl_logger.error({"ERROR": f"Unable to renew SSL certificates: {e}"})

    @staticmethod
    def read_ssl(path_to_cert):
        try:
            cert_file_name = os.path.join(os.path.dirname(__file__), path_to_cert)
            cert_dict = ssl._ssl._test_decode_cert(cert_file_name)

            date_regex = r'[a-zA-Z]+[\s+]+[0-9]{1,2}'
            ssl_issuer = cert_dict['issuer'][1][0][1]
            ssl_active_from = re.search(date_regex, cert_dict['notBefore']).group()+' '+cert_dict['notBefore'][-8:-4]
            ssl_expiry = re.search(date_regex, cert_dict['notAfter']).group()+' '+cert_dict['notAfter'][-8:-4]

            cert_info = {"ssl_issuer": ssl_issuer,
                         "ssl_active_from": ssl_active_from.replace('  ', ' '),
                         "ssl_expiry": ssl_expiry.replace('  ', ' ')}

        except Exception as e:
            ssl_logger.error({"ERROR": f"Unable to read SSL certificate: {e}"})
            cert_info = {"ssl_issuer": "", "ssl_active_from": "", "ssl_expiry": ""}
        return cert_info

    @staticmethod
    def calculate_remaining_ssl_validity_days(date_string):
        try:
            give_full_date = date_string.split(' ')
            given_day = int(give_full_date[1].strip())
            given_month = int(datetime.strptime(give_full_date[0].strip(), "%b").month)
            given_year = int(give_full_date[2].strip())

            date_now = date.today().strftime("%Y, %m, %d").split(',')
            this_day = int(date_now[2])
            this_month = int(date_now[1])
            this_year = int(date_now[0])

            given_date = date(given_year, given_month, given_day)
            current_date = date(this_year, this_month, this_day)
            delta = given_date-current_date
            return {"valid_days": delta.days}
        except Exception as e:
            ssl_logger.error({"ERROR": f"Unable to calculate remaining ssl validity days: {e}"})
            return
