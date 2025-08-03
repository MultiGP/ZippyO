'''
Global configurations
'''
import copy
import json
import shutil
import time
import os
from datetime import datetime


class Config:
    def __init__(self, configcontext, filename='config.json'):
        self._configcontext = configcontext
        self.filename = filename

        self.config = {
            'SECRETS': {},
            'GENERAL': {},
        }

        # other default configurations
        self.config['GENERAL']['HTTP_PORT'] = 5000
        self.config['GENERAL']['ADMIN_USERNAME'] = 'admin'
        self.config['GENERAL']['ADMIN_PASSWORD'] = 'zippyo'
        self.config['GENERAL']['SECONDARIES'] = []
        self.config['GENERAL']['SECONDARY_TIMEOUT'] = 300  # seconds
        self.config['GENERAL']['DEBUG'] = False
        self.config['GENERAL']['CORS_ALLOWED_HOSTS'] = '*'
        self.config['GENERAL']['FILE_PATH'] = '../../../../../Documents/livetime.json'

        self.InitResultStr = None


        # override defaults above with config from file
        try:
            with open(self.filename, 'r') as f:
                ExternalConfig = json.load(f)

            for key in ExternalConfig.keys():
                if key in self.config:
                    self.config[key].update(ExternalConfig[key])

            self.config_file_status = 1
            self.InitResultStr = "Using configuration file '{0}'".format(self.filename)
        except IOError:
            self.config_file_status = 0
            self.InitResultStr = "No configuration file found, using defaults"
        except ValueError as ex:
            self.config_file_status = -1
            self.InitResultStr = "Configuration file invalid, using defaults; error is: " + str(ex)

        self.check_backup_config_file()
        self.save_config()

    def get_item(self, section, key):
        try:
            return self.config[section][key]
        except:
            return False

    def get_item_int(self, section, key, default_value=0):
        try:
            val = self.config[section][key]
            if val:
                return int(val)
            else:
                return default_value
        except:
            return default_value

    def get_section(self, section):
        try:
            return self.config[section]
        except:
            return False

    def set_item(self, section, key, value):
        try:
            self.config[section][key] = value
            self.save_config()
        except:
            return False
        return True

    def save_config(self):
        self.config['GENERAL']['LAST_MODIFIED_TIME'] = int(time.time())
        with open(self.filename, 'w') as f:
            f.write(json.dumps(self.config, indent=2))

    # if config file does not contain 'LAST_MODIFIED_TIME' item or time
    #  does not match file-modified timestamp then create backup of file
    def check_backup_config_file(self):
        try:
            if os.path.exists(self.filename):
                last_modified_time = self.get_item_int('GENERAL', 'LAST_MODIFIED_TIME')
                file_modified_time = int(os.path.getmtime(self.filename))
                if file_modified_time > 0 and abs(file_modified_time - last_modified_time) > 5:
                    time_str = datetime.fromtimestamp(file_modified_time).strftime('%Y%m%d_%H%M%S')
                    (fname_str, fext_str) = os.path.splitext(self.filename)
                    bkp_file_name = "{}_bkp_{}{}".format(fname_str, time_str, fext_str)
                    shutil.copy2(self.filename, bkp_file_name)
        except Exception as ex:
           print ("exception with backup config")

    def get_sharable_config(self):
        sharable_config = copy.deepcopy(self.config)
        del sharable_config['SECRETS']
        return sharable_config

