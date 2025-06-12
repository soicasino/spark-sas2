import configparser
import os
from typing import Optional, Union

class ConfigManager:
    """Manages configuration settings for the SAS machine application"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """Load configuration from file, create default if doesn't exist"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration file"""
        self.config['SAS_MACHINE'] = {
            'asset_number': '108',
            'registration_key': '00000000000000000000000000000000000000000000',
            'sas_address': '01',
            'baud_rate': '19200',
            'timeout': '0.1'
        }
        
        self.config['AFT_SETTINGS'] = {
            'aft_timeout': '15.0',
            'default_transfer_type': '00',
            'max_retry_attempts': '3'
        }
        
        self.config['LOGGING'] = {
            'debug_aft': 'true',
            'debug_asset': 'true'
        }
        
        self.save_config()
    
    def save_config(self):
        """Save current configuration to file"""
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
    
    def get_asset_number(self) -> int:
        """Get asset number as integer"""
        return self.config.getint('SAS_MACHINE', 'asset_number', fallback=108)
    
    def set_asset_number(self, asset_number: int):
        """Set asset number and save to config"""
        if 'SAS_MACHINE' not in self.config:
            self.config.add_section('SAS_MACHINE')
        self.config.set('SAS_MACHINE', 'asset_number', str(asset_number))
        self.save_config()
    
    def get_asset_number_hex(self) -> str:
        """Get asset number as 4-byte hex string (e.g., '0000006C' for 108)"""
        asset_num = self.get_asset_number()
        return f"{asset_num:08X}"
    
    def get_registration_key(self) -> str:
        """Get registration key as hex string"""
        return self.config.get('SAS_MACHINE', 'registration_key', 
                              fallback='00000000000000000000000000000000000000000000')
    
    def set_registration_key(self, key: str):
        """Set registration key and save to config"""
        if 'SAS_MACHINE' not in self.config:
            self.config.add_section('SAS_MACHINE')
        self.config.set('SAS_MACHINE', 'registration_key', key)
        self.save_config()
    
    def get_aft_timeout(self) -> float:
        """Get AFT timeout in seconds"""
        return self.config.getfloat('AFT_SETTINGS', 'aft_timeout', fallback=15.0)
    
    def get_default_transfer_type(self) -> str:
        """Get default transfer type"""
        return self.config.get('AFT_SETTINGS', 'default_transfer_type', fallback='00')
    
    def get_max_retry_attempts(self) -> int:
        """Get maximum retry attempts for AFT operations"""
        return self.config.getint('AFT_SETTINGS', 'max_retry_attempts', fallback=3)
    
    def is_debug_aft_enabled(self) -> bool:
        """Check if AFT debug logging is enabled"""
        return self.config.getboolean('LOGGING', 'debug_aft', fallback=True)
    
    def is_debug_asset_enabled(self) -> bool:
        """Check if asset debug logging is enabled"""
        return self.config.getboolean('LOGGING', 'debug_asset', fallback=True)
    
    def get_sas_address(self) -> str:
        """Get SAS address"""
        return self.config.get('SAS_MACHINE', 'sas_address', fallback='01')
    
    def get_baud_rate(self) -> int:
        """Get baud rate"""
        return self.config.getint('SAS_MACHINE', 'baud_rate', fallback=19200)
    
    def get_timeout(self) -> float:
        """Get communication timeout"""
        return self.config.getfloat('SAS_MACHINE', 'timeout', fallback=0.1)
    
    # Backward compatibility methods for old interface
    def get(self, section: str, option: str, fallback=None):
        """Backward compatibility method for old config interface"""
        return self.config.get(section, option, fallback=fallback)
    
    def getint(self, section: str, option: str, fallback=0):
        """Backward compatibility method for old config interface"""
        return self.config.getint(section, option, fallback=fallback)
    
    def getfloat(self, section: str, option: str, fallback=0.0):
        """Backward compatibility method for old config interface"""
        return self.config.getfloat(section, option, fallback=fallback)
    
    def getboolean(self, section: str, option: str, fallback=False):
        """Backward compatibility method for old config interface"""
        return self.config.getboolean(section, option, fallback=fallback)

# Global config manager instance
config_manager = ConfigManager() 