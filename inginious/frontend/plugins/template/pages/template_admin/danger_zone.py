# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

# [Source code integration]: move file to inginious.frontend.pages.template_admin, generalise
import hashlib
import logging
import random

import web

from inginious.frontend.plugins.template.pages.template_admin.utils import INGIniousTemplateAdminPage


class TemplateDangerZonePage(INGIniousTemplateAdminPage):
    """ Template administration page: danger zone (delete template) """
    _logger = logging.getLogger("inginious.webapp.danger_zone")

    def GET_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ GET request """
        course, __ = self.get_course_and_check_rights(courseid, allow_all_staff=False)

        return self.page(course)

    def POST_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ POST request """
        course, __ = self.get_course_and_check_rights(courseid, allow_all_staff=False)

        msg, error = "", False

        data = web.input()
        if not data.get("token", "") == self.user_manager.session_token():
            msg, error = _("Operation aborted due to invalid token."), True
        elif "deleteall" in data:
            if not data.get("courseid", "") == courseid:
                msg, error = _("Wrong template id."), True
            else:
                try:
                    # Deletes the course from the factory (entire folder)
                    self.course_factory.delete_course(courseid)
                    self._logger.info("Course %s files erased.", courseid)
                    web.seeother(self.app.get_homepath() + '/template')
                except Exception as ex:
                    msg, error = _("An error occurred while deleting the template data: {}").format(repr(ex)), True

        return self.page(course, msg, error)

    def page(self, course, msg="", error=False):
        """ Get all data and display the page """
        thehash = hashlib.sha512(str(random.getrandbits(256)).encode("utf-8")).hexdigest()
        self.user_manager.set_session_token(thehash)

        return self.template_helper.get_custom_renderer('frontend/plugins/template/templates').template_admin.danger_zone(course, thehash, msg, error)