# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

# [Source code integration]: move to inginious.frontend.pages

""" Template page """
import web

from inginious.common.course_factory import CourseFactory
from inginious.frontend.pages.utils import INGIniousAuthPage
from inginious.frontend.plugins.template.template_common import export


class TemplatePage(INGIniousAuthPage):
    """ Template page """

    @property
    def template_factory(self) -> CourseFactory:
        return self.plugin_manager.call_hook("template_factory")[0]

    def get_template(self, templateid):
        """ Return the course """
        try:
            template = self.template_factory.get_course(templateid)
        except:
            raise web.notfound()
        if template.is_private() and not self.user_manager.has_staff_rights_on_course(template):
            raise web.notfound()

        return template

    def POST_AUTH(self, templateid):  # pylint: disable=arguments-differ
        """ POST request """
        template = self.get_template(templateid)
        username = self.user_manager.session_username()
        user_input = web.input()

        if "new_courseid" in user_input and self.user_manager.user_is_superadmin():
            try:
                export(self.template_factory, self.course_factory, user_input["templateid"], user_input["new_courseid"], username)
                raise web.redirect(self.app.get_homepath() + "/admin/{}".format(user_input["new_courseid"]))
            except:
                message, success = _("Failed to create the course."), False
        else:
            return self.show_page(template)

        return self.show_page(template, success, message)

    def GET_AUTH(self, templateid):  # pylint: disable=arguments-differ
        """ GET request """
        template = self.get_template(templateid)
        return self.show_page(template)

    def show_page(self, template, success=None, message=""):
        """ Prepares and shows the course page """
        try:
            from inginious.frontend.plugins.course_structure.webapp_course import get_course_structure
            toc = get_course_structure(template)
        except:
            toc = []

        # Change to professors right when available
        if self.user_manager.user_is_superadmin():
            return self.template_helper.get_custom_renderer('frontend/plugins/template/templates').template(template,
                                                                                                            toc,
                                                                                                            success,
                                                                                                            message)
        else:
            raise web.notfound()
