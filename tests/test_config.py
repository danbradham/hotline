from hotline import config

conf = config.Config('./conf/defaults.yaml')

conf.save(ext="json")
