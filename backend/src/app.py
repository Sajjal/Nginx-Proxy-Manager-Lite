import os
import shutil
import json
import logging
from datetime import timedelta
from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, set_access_cookies, unset_jwt_cookies, JWTManager
from werkzeug.security import generate_password_hash, check_password_hash


from util.ManageDB import ManageDB
from util.RouteController import RouteController

logging.basicConfig(filename="./debug_logs/npmlite.log", level=logging.ERROR,
                    format="%(asctime)s:%(name)s:%(levelname)s:%(message)s")

logger = logging.getLogger('werkzeug')
logger.setLevel(logging.ERROR)


# ***********************************************************
# Docker Mount Volume Check
path = '/data'
dir = os.listdir(path)

# Checking if the data directory is empty or not
if len(dir) == 0:
    try:
        source_dir = '/npmlite/initial_data'
        target_dir = '/data'

        file_names = os.listdir(source_dir)

        for file_name in file_names:
            shutil.move(os.path.join(source_dir, file_name), target_dir)
    except:
        logger.error({"Error": "Unable to copy initial data files"})
else:
    pass

# ***********************************************************

# Uncomment the first line and comment second and third and forth on production
db = ManageDB('../data/database/npmlite.db', './config/db_config.json', False)
# db.create_table()
# db.insert_data('users', {"email": "npm@npmlite.com", "password": generate_password_hash("npmlite"), "first_login": 1})

controller = RouteController(db)


class LocalFlask(Flask):
    def process_response(self, response):
        SERVER_NAME = 'NPM LITE (https://mrsajjal.com)'
        # Every response will be processed here first
        response.headers['server'] = SERVER_NAME
        return(response)


app = LocalFlask(__name__, static_url_path='', static_folder='public', template_folder='public')

config = {}
try:
    with open("../data/npmlite_config/config.json") as file:
        config = json.loads(file.read())
except:
    logger.error({"Error": "Unable to read npmlite config file"})

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = config['jwt_secret_key']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_COOKIE_SAMESITE'] = "Strict"  # Uncomment this in production!
app.config["JWT_COOKIE_SECURE"] = config['JWT_COOKIE_SECURE']

jwt = JWTManager(app)

if config['enable_web_portal']:

    @ app.route('/', methods=['GET'])
    def home():
        return render_template("index.html")

    @ app.errorhandler(404)
    def page_not_found(e):
        return render_template('index.html')

    @ app.route('/login', methods=['POST'])
    def login():
        user = db.search_data('users', {'email': request.json['email']})
        if not user:
            return {"Error": "User not found!"}, 403

        is_valid_password = check_password_hash(user[0]['password'], request.json['password'])
        if not is_valid_password:
            return {"Error": "Invalid Login!"}, 403

        access_token = create_access_token(identity=user[0]['id'])

        if user and user[0]['first_login'] == '1':
            response = jsonify({"Status": "Change Password"})

        else:
            response = jsonify({"Status": "Login"})

        set_access_cookies(response, access_token)
        return response

    @ app.route('/changePassword', methods=['POST'])
    def changePassword():
        if not 'email' in request.json or not 'password' in request.json:
            return {"Error": "Invalid login params"}, 406

        if request.json['email'].lower() == 'npm@npmlite.com' or request.json['password'].lower() == 'npmlite':
            return {"Error": "Default login info is not allowd!"}, 403

        default_user = db.search_data('users')

        if len(default_user):
            db.update_data(
                'users', default_user[0]['id'], {"email": request.json['email'],
                                                 "password": generate_password_hash(request.json['password']),
                                                 "first_login": 0})
            return {"Status": "Password Changed"}
        return {"Error": "User not found!"}, 400

    @ app.route('/changePasswordLater', methods=['POST'])
    @ jwt_required()
    def changePasswordLater():
        if not 'email' in request.json or not 'password' in request.json:
            return {"Error": "Invalid login params"}, 406

        if request.json['email'].lower() == 'npm@npmlite.com' or request.json['password'].lower() == 'npmlite':
            return {"Error": "Default login info is not allowd!"}, 403

        current_user = db.search_data('users', {'id': get_jwt_identity()})

        if len(current_user):
            db.update_data(
                'users', current_user[0]['id'], {"email": request.json['email'],
                                                 "password": generate_password_hash(request.json['password']),
                                                 "first_login": 0})
            return {"Status": "Password Changed"}
        return {"Error": "User not found!"}, 400

    @ app.route('/create', methods=['POST'])
    @ jwt_required()
    def create():
        request.json['userID'] = get_jwt_identity()
        return controller.create(request.json)

    @ app.route('/requestSSL', methods=['POST'])
    @ jwt_required()
    def request_SSL():
        request.json['userID'] = get_jwt_identity()
        return controller.request_new_ssl(request.json)

    @ app.route('/list', methods=['GET'])
    @ jwt_required()
    def list():
        domain_list = db.search_data('domain_info', {"userID": get_jwt_identity()})
        for item in domain_list:
            if 'ips' in item:
                item['ips'] = json.loads(item['ips'])
        return {"domain_list": domain_list}

    @ app.route('/listSSL', methods=['GET'])
    @ jwt_required()
    def listSSL():
        ssl_list = db.search_data('ssl_info', {"userID": get_jwt_identity()})
        for ssl in ssl_list:
            cert_info = controller.read_ssl(ssl['ssl_cert_path'])
            ssl['cert_info'] = cert_info
        return {"ssl_list": ssl_list}

    @ app.route('/update', methods=['POST'])
    @ jwt_required()
    def update():
        request.json['userID'] = get_jwt_identity()
        return controller.update(request.json)

    @ app.route('/enable', methods=['POST'])
    @ jwt_required()
    def enable():
        request.json['userID'] = get_jwt_identity()
        return controller.enable(request.json)

    @ app.route('/disable', methods=['POST'])
    @ jwt_required()
    def disable():
        request.json['userID'] = get_jwt_identity()
        return controller.disable(request.json)

    @ app.route('/delete', methods=['POST'])
    @ jwt_required()
    def delete():
        request.json['userID'] = get_jwt_identity()
        return controller.delete(request.json)

    @ app.route('/logout', methods=['GET', 'POST'])
    def logout():
        response = jsonify({"Status": "Logout"})
        unset_jwt_cookies(response)
        return response


if config['enable_rest_api']:

    @ app.route('/api/status', methods=['GET'])
    def api_status():
        return {"serverStatus": "API Server Up & Running..."}

    @ app.route('/api/create', methods=['POST'])
    def api_create():
        if not request.headers.get('Authorization') or not request.headers.get('Authorization').split()[1] == config[
                'api_key']:
            return {"Error": "Invalid API Key"}, 401

        user = db.search_data('users')
        request.json['userID'] = user[0]['id']
        return controller.create(request.json)

    @ app.route('/api/requestSSL', methods=['POST'])
    def api_request_SSL():
        if not request.headers.get('Authorization') or not request.headers.get('Authorization').split()[1] == config[
                'api_key']:
            return {"Error": "Invalid API Key"}, 401

        user = db.search_data('users')
        request.json['userID'] = user[0]['id']
        return controller.request_new_ssl(request.json)

    @ app.route('/api/list', methods=['GET'])
    def api_list():
        if not request.headers.get('Authorization') or not request.headers.get('Authorization').split()[1] == config[
                'api_key']:
            return {"Error": "Invalid API Key"}, 401

        user = db.search_data('users')
        domain_list = db.search_data('domain_info', {"userID": user[0]['id']})
        for item in domain_list:
            if 'ips' in item:
                item['ips'] = json.loads(item['ips'])
        return {"domain_list": domain_list}

    @ app.route('/api/listSSL', methods=['GET'])
    def api_listSSL():
        if not request.headers.get('Authorization') or not request.headers.get('Authorization').split()[1] == config[
                'api_key']:
            return {"Error": "Invalid API Key"}, 401

        user = db.search_data('users')
        ssl_list = db.search_data('ssl_info', {"userID": user[0]['id']})
        for ssl in ssl_list:
            cert_info = controller.read_ssl(ssl['ssl_cert_path'])
            ssl['cert_info'] = cert_info
        return {"ssl_list": ssl_list}

    @ app.route('/api/update', methods=['POST'])
    def api_update():
        if not request.headers.get('Authorization') or not request.headers.get('Authorization').split()[1] == config[
                'api_key']:
            return {"Error": "Invalid API Key"}, 401

        user = db.search_data('users')
        request.json['userID'] = user[0]['id']
        return controller.update(request.json)

    @ app.route('/api/enable', methods=['POST'])
    def api_enable():
        if not request.headers.get('Authorization') or not request.headers.get('Authorization').split()[1] == config[
                'api_key']:
            return {"Error": "Invalid API Key"}, 401

        user = db.search_data('users')
        request.json['userID'] = user[0]['id']
        return controller.enable(request.json)

    @ app.route('/api/disable', methods=['POST'])
    def api_disable():
        if not request.headers.get('Authorization') or not request.headers.get('Authorization').split()[1] == config[
                'api_key']:
            return {"Error": "Invalid API Key"}, 401

        user = db.search_data('users')
        request.json['userID'] = user[0]['id']
        return controller.disable(request.json)

    @ app.route('/api/delete', methods=['POST'])
    def api_delete():
        if not request.headers.get('Authorization') or not request.headers.get('Authorization').split()[1] == config[
                'api_key']:
            return {"Error": "Invalid API Key"}, 401

        user = db.search_data('users')
        request.json['userID'] = user[0]['id']
        return controller.delete(request.json)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=40045, debug=False)

# **************************************
