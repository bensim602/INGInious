# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

# [Source code integration]: move to inginious.frontend.pages.course_admin

""" Export course """
import web

from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from inginious.frontend.plugins.template.template_factory import TemplateFactory
from inginious.frontend.plugins.template.template_common import export


class CourseAdminTemplates(INGIniousAdminPage):
    """ Export course """

    @property
    def template_factory(self) -> TemplateFactory:
        return self.plugin_manager.call_hook("template_factory")[0]

    def GET_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ GET request """
        course, __ = self.get_course_and_check_rights(courseid, allow_all_staff=False)

        return self.page(course)

    def POST_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ POST request """
        course, __ = self.get_course_and_check_rights(courseid, allow_all_staff=False)

        templateid = web.input()["new_template_id"]
        user = self.user_manager.session_username()

        try:
            export(self.course_factory, self.template_factory, courseid, templateid, user, True)
            raise web.redirect(self.app.get_homepath() + "/edit_template/{}".format(templateid))
        except:
            return self.page(course, True)

    def page(self, course, error=False):
        """ Get all data and display the page """
        template_source_id = course.get_descriptor().get("source", None)
        template_source = self.template_factory.get_course(template_source_id)
        return self.template_helper.get_custom_renderer(
            'frontend/plugins/template/templates').course_admin.templates(course, template_source, error)
