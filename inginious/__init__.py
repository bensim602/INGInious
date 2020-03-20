# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.
#

import os
import gettext
import builtins

__version__ = "0.6.dev0"


builtins.__dict__['_'] = gettext.gettext


def get_root_path():
    """ Returns the INGInious root path """
    return os.path.abspath(os.path.dirname(__file__))
