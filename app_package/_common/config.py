import os
from ss_config import ConfigWorkstation, ConfigDev, ConfigProd

match os.environ.get('FLASK_CONFIG_TYPE'):
    case 'dev':
        config = ConfigDev()
        print('- FlaskStarterWebsite01/app_pacakge/config: Development')
    case 'prod':
        config = ConfigProd()
        print('- FlaskStarterWebsite01/app_pacakge/config: Production')
    case _:
        config = ConfigWorkstation()
        print('- FlaskStarterWebsite01/app_pacakge/config: Local')