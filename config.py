import configparser
import os

class Config:
    """A model for saving settings"""

    def __init__(self):
        self.config_path = 'config.ini'
        self.email_receiver = ''
        self.email_server = ''
        self.email_port = '0'
        self.email_username = ''
        self.email_password = ''
        self.email_ssl = False
        self.objects_to_detect = -1
        self.detection_marker_location = 50
        self.detection_marker_direction = 0
        self.mode = ''

    def load(self):
        """Load the settings from the file"""

        if not os.path.exists(self.config_path):
            return

        config_parser = configparser.ConfigParser()
        config_parser.read(self.config_path)

        email_config = config_parser['email']
        objects_config = config_parser['objects']
        detection_marker = config_parser['detection_marker']

        self.email_receiver = email_config['receiver']
        self.email_server = email_config['server']
        self.email_port = email_config['port']
        self.email_username = email_config['username']
        self.email_password = email_config['password']
        self.email_ssl = bool(email_config['ssl'])
        self.objects_to_detect = int(objects_config['index'])
        self.detection_marker_location = int(detection_marker['location'])
        self.detection_marker_direction = int(detection_marker['direction'])

        if(self.objects_to_detect == 0):
            self.mode = 'PH'
        elif(self.objects_to_detect == 1):
            self.mode = 'PV'
        elif(self.objects_to_detect == 3):
            self.mode = 'PLC'
        else:
            self.mode ='PHV'

    def save(self):
        """Save the settings to the file"""
        config_parser = configparser.ConfigParser()
        config_parser['email'] = {'receiver': self.email_receiver,
                                  'server': self.email_server,
                                  'port': self.email_port,
                                  'username': self.email_username,
                                  'password': self.email_password,
                                  'ssl': self.email_ssl
                                  }

        config_parser['objects'] = {'index': str(self.objects_to_detect)}

        config_parser['detection_marker'] = {'location': self.detection_marker_location,
                                            'direction': self.detection_marker_direction}

        with open(self.config_path, 'w') as configfile:
            config_parser.write(configfile)
