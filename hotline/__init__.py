try:
    import sip
    for datatype in ['QString', 'QVariant', 'QUrl', 'QDate',
                     'QDateTime', 'QTextStream', 'QTime']:
        sip.setapi(datatype, 2)
except:
    pass

from .api import *
