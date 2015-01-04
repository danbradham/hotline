import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
from hotline import ConfigBase

os.environ['TEST_CFG'] = os.path.abspath('../hotline/conf')

conf = ConfigBase()
conf.from_env('TEST_CFG')
print conf
# conf.from_file(os.path.join(config_root, 'config.json'))
# conf.save(ext='yml')

# store = ConfigBase()
# store.from_file(os.path.join(config_root, 'config.json'))
