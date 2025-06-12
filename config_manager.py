import configparser

class ConfigManager:
    """Configuration manager for SAS application"""
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        # Set default values
        self.config.read_dict({
            'sas': {
                'address': '01'
            },
            'machine': {
                'devicetypeid': '8'
            },
            'casino': {
                'casinoid': '8'
            }
        })
    
    def get(self, section, key, fallback=None):
        """Get configuration value with fallback"""
        try:
            return self.config.get(section, key)
        except:
            return fallback
    
    def getint(self, section, key, fallback=None):
        """Get integer configuration value with fallback"""
        try:
            return self.config.getint(section, key)
        except:
            return fallback if fallback is not None else 0
    
    def set(self, section, key, value):
        """Set configuration value"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value)) 