
# author:kunli
# date:2011-07-12
# email:kunli@bainainfo.com
import logging

logger = logging.getLogger("dolphinop.db")

_db = None


def get_built_ins(spec=None, fields=None):
    assert _db, 'Dolphinop/speeddials database server not correctly configured, review your settings.py.'

    builtins = _db.builtins.find_one(spec, fields=fields)
    return builtins
