import os
import subprocess as sp
import re
import logging
import json

from .ManageConf import ManageConf
from .ManageSSL import ManageSSL

logging.basicConfig(filename="./debug_logs/npmlite.log", level=logging.ERROR,
                    format="%(asctime)s:%(name)s:%(levelname)s:%(message)s")

logger = logging.getLogger("ROUTE_CONTROLLER")


class RouteController:

    def __init__(self, db):
        self.db = db
        self.valid_domain_info_keys = [
            'id', 'timestamp', 'userID', 'domain', 'type', 'ips', 'static_path', 'redirect_url', 'enableSSL',
            'forceSSL', 'websocket', 'HSTS', 'http2', 'block_exploit']

        self.valid_ssl_info_keys = ['id', 'timestamp', 'userID', 'domain', 'ssl_cert_path', 'ssl_key_path']

        self.valid_users_key = ['id', 'timestamp', 'email', 'password']

    @staticmethod
    def __validate_user_input(user_input):
        allowed_characters = re.compile(r"[A-Za-z0-9-_.@/]+|^$")
        #domain_regex = re.compile(r"^(\*\.)?([a-z\d][a-z\d-]*[a-z\d]\.)+[a-z]+$")
        domain_regex = re.compile(r"[-A-Za-z0-9+&@#\/%?=~_|!:,.;]+[-A-Za-z0-9+&@#\/%=~_|]")

        if not isinstance(user_input, dict):
            return

        for key, value in user_input.items():
            if isinstance(value, list):
                try:
                    for item in value:
                        if len(item) > 2:
                            return
                        for key, value in item.items():
                            if not re.fullmatch(allowed_characters, str(value)):
                                return
                except:
                    return
            elif key == 'domain':
                try:
                    re.search(domain_regex, str(value)).group()
                except:
                    return
            else:
                try:
                    if not re.fullmatch(allowed_characters, str(value)):
                        return
                except:
                    return

        return True

    def __update_nginx_conf(self, params):
        nginx_conf = ManageConf(params)
        try:
            nginx_conf.createConf()
            if nginx_conf.reload_nginx():
                del nginx_conf
                return True
            del nginx_conf
            return
        except Exception as e:
            logger.error({"Error": 'Unable to Create Nginx .conf file in Server!' + e})
            return

    def request_new_ssl(self, params):
        if not self.__validate_user_input(params):
            return {"Error": "Invalid params"}, 406

        if not "userID" in params or not "domain" in params or not "email" in params or not "agree_le_tos" in params:
            return {"Error": "Missing required params"}, 406

        if not params["agree_le_tos"]:
            return {"Error": "Lets Encrypt's terms is not accepted!"}, 406

        check_if_exists = self.db.search_data('domain_info', {"domain": params['domain']})
        if not check_if_exists:
            if not self.__update_nginx_conf(
                {"userID": params['userID'],
                 "domain": params['domain'],
                 "type": "static", "static_path": "/usr/share/nginx/html/"}):
                return {"Error": 'Unable to Create Nginx .conf file in Server!'}, 500

        ssl_config = ManageSSL()
        ssl_info = ssl_config.generate_ssl(params['domain'], params['email'])
        if ssl_info and ssl_info == 'Exists':
            return {"Error": f'SSL Cert already exists for {params["domain"]}!'}, 406

        if ssl_info and ssl_info != 'Exists':
            params['ssl_cert_path'] = ssl_info['ssl_cert_path']
            params['ssl_key_path'] = ssl_info['ssl_key_path']

            del ssl_config

            ssl_db_data = {"userID": params['userID'],
                           "domain": params['domain'],
                           "ssl_cert_path": ssl_info['ssl_cert_path'],
                           "ssl_key_path": ssl_info['ssl_key_path']
                           }

            ssl_db_info = self.db.insert_data('ssl_info', ssl_db_data)
            if not ssl_db_info:
                logger.error({"Error": 'Unable to insert SSL info in ssl_info table'})
                return {"Error": 'Unable insert SSL info in database!'}, 500
            return ssl_db_data

        try:
            os.remove(f"./data/nginx_conf/{params['domain']}.conf")
        except:
            pass
        return {"Error": f'Unable to Request SSL Certificate for {params["domain"]} !'}, 500

    @staticmethod
    def read_ssl(path_to_cert):
        allowed_characters = re.compile(r"[A-Za-z0-9-_./]+")
        try:
            if not re.fullmatch(allowed_characters, str(path_to_cert)):
                logger.error({"Error": 'Invalid file path for SSL cert'})
                return {"ssl_issuer": "", "ssl_active_from": "", "ssl_expiry": ""}
        except:
            logger.error({"Error": 'Invalid file path for SSL cert'})
            return {"ssl_issuer": "", "ssl_active_from": "", "ssl_expiry": ""}

        ssl_config = ManageSSL()
        ssl_info = ssl_config.read_ssl(path_to_cert)
        del ssl_config
        return ssl_info

    def create(self, req_params):
        if not self.__validate_user_input(req_params):
            return {"Error": "Invalid params"}, 406

        if not "userID" in req_params or not "domain" in req_params or not "type" in req_params:
            return {"Error": "Missing required params"}, 406

        check_if_exists = self.db.search_data('domain_info', {"domain": req_params['domain']})
        if len(check_if_exists):
            return {"Error": "Domain already exists in server"}, 403

        if not self.__update_nginx_conf(req_params):
            return {"Error": 'Unable to Create Nginx .conf file in Server!'}, 500

        temp_params = req_params.copy()
        if 'ips' in temp_params:
            temp_params['ips'] = json.dumps(temp_params['ips'])

        for key in req_params.keys():
            if key not in self.valid_domain_info_keys:
                del temp_params[key]

        temp_params['is_disabled'] = 0
        domain_db_info = self.db.insert_data('domain_info', temp_params)
        del temp_params

        if domain_db_info:
            return {"Success": f"{req_params['domain']} added successfully"}
        else:
            logger.error({"Error": 'Unable to insert data in domain_info table'})
            return {"Error": 'Unable to insert data in domain_info table'}, 500

    def update(self, req_params):
        if not self.__validate_user_input(req_params):
            return {"Error": "Invalid params"}, 406

        if not "userID" in req_params or not "domain" in req_params:
            return {"Error": "Missing required params"}, 406

        check_if_exists = self.db.search_data(
            'domain_info', {"domain": req_params['domain'],
                            "userID": req_params['userID']})
        if not check_if_exists:
            return {"Error": "Domain not found in server"}, 403

        if not self.__update_nginx_conf(req_params):
            return {"Error": 'Unable to Create Nginx .conf file in Server!'}, 500

        temp_params = req_params.copy()
        if 'ips' in temp_params:
            temp_params['ips'] = json.dumps(temp_params['ips'])

        for key in req_params.keys():
            if key not in self.valid_domain_info_keys:
                del temp_params[key]

        domain_db_update_info = self.db.update_data('domain_info', check_if_exists[0]['id'], temp_params)
        del temp_params
        if domain_db_update_info:
            return {"Success": f"{req_params['domain']} record updated successfully"}
        else:
            logger.error({"Error": 'Unable to insert data in domain_info table'})
            return {"Error": f"Unable to update the record of {req_params['domain']}"}, 500

    def delete(self, req_params):
        if not self.__validate_user_input(req_params):
            return {"Error": "Invalid params"}, 406

        if not "userID" in req_params or not "domain" in req_params:
            return {"Error": "Missing required params"}, 406

        domain_info = self.db.search_data(
            'domain_info', {"userID": req_params['userID'],
                            "domain": req_params['domain']})
        ssl_info = []
        if len(domain_info):
            ssl_info = self.db.search_data('ssl_info', {"userID": req_params['userID'], "domain": req_params['domain']})

            if len(ssl_info) and 'delete_ssl' in req_params and req_params['delete_ssl']:
                ssl_config = ManageSSL()
                if not ssl_config.delete_ssl(req_params['domain']):
                    del ssl_config
                    return {"Error": f"Unable to delete {req_params['domain']} SSL info from server"}, 500
                del ssl_config
                self.db.delete_data('ssl_info', ssl_info[0]['id'])

            delete_error_count = 0
            try:
                os.remove(f"../data/nginx_conf/{req_params['domain']}.conf")
            except:
                delete_error_count = delete_error_count+1
            try:
                os.remove(f"../data/nginx_conf/disabled/{req_params['domain']}.conf")
            except:
                delete_error_count = delete_error_count+1
            if delete_error_count > 1:
                return {"Error": f"Unable to delete {req_params['domain']} conf file from server"}, 500

            nginx_conf = ManageConf({"domain": req_params['domain']})
            if nginx_conf.reload_nginx():
                self.db.delete_data('domain_info', domain_info[0]['id'])
                del nginx_conf
                return {"Success": f"{req_params['domain']} removed successfully"}

            return {"Error": f"Unable to remove record of {req_params['domain']} from server"}, 500

        return {"Error": f"Domain {req_params['domain']} not found in server"}, 403

    def enable(self, req_params):
        if not self.__validate_user_input(req_params):
            return {"Error": "Invalid params"}, 406

        if not "userID" in req_params or not "domain" in req_params:
            return {"Error": "Missing required params"}, 406

        check_if_exists = self.db.search_data(
            'domain_info', {"domain": req_params['domain'],
                            "userID": req_params['userID']})

        if not check_if_exists:
            return {"Error": "Domain not found in server"}, 403

        enable_status = sp.getoutput(
            f"mv ../data/nginx_conf/disabled/{req_params['domain']}.conf ../data/nginx_conf/{req_params['domain']}.conf")

        if 'No such file or directory' in enable_status:
            return {"Error": f"Unable to enable {req_params['domain']}"}, 500

        nginx_conf = ManageConf({"domain": req_params['domain']})
        if not nginx_conf.reload_nginx():
            return {"Error": f"Unable to enable {req_params['domain']}"}, 500

        enable_in_db = self.db.update_data('domain_info', check_if_exists[0]['id'], {'is_disabled': 0})
        if not enable_in_db:
            return {"Error": f"Unable to enable {req_params['domain']}"}, 500

        return {"Success": f"{req_params['domain']} is enabled!"}

    def disable(self, req_params):
        if not self.__validate_user_input(req_params):
            return {"Error": "Invalid params"}, 406

        if not "userID" in req_params or not "domain" in req_params:
            return {"Error": "Missing required params"}, 406

        check_if_exists = self.db.search_data(
            'domain_info', {"domain": req_params['domain'],
                            "userID": req_params['userID']})
        if not check_if_exists:
            return {"Error": "Domain not found in server"}, 403

        disable_status = sp.getoutput(
            f"mv ../data/nginx_conf/{req_params['domain']}.conf ../data/nginx_conf/disabled/{req_params['domain']}.conf")

        if 'No such file or directory' in disable_status:
            return {"Error": f"Unable to disable {req_params['domain']}"}, 500

        nginx_conf = ManageConf({"domain": req_params['domain']})
        if not nginx_conf.reload_nginx():
            return {"Error": f"Unable to disable {req_params['domain']}"}, 500

        disable_in_db = self.db.update_data('domain_info', check_if_exists[0]['id'], {'is_disabled': 1})
        if not disable_in_db:
            return {"Error": f"Unable to disable {req_params['domain']}"}, 500

        return {"Success": f"{req_params['domain']} is disabled!"}
