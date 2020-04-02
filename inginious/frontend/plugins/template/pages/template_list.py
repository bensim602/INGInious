# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

# [Source code integration]: move to inginious.frontend.pages

""" List of templates """
import web

from inginious.frontend.pages.utils import INGIniousAuthPage
from inginious.frontend.plugins.template.template_factory import TemplateFactory
from inginious.frontend.plugins.template.template_common import export


class TemplateList(INGIniousAuthPage):
    """ List of templates """

    @property
    def template_factory(self) -> TemplateFactory:
        return self.plugin_manager.call_hook("template_factory")[0]

    def GET_AUTH(self):  # pylint: disable=arguments-differ
        """ GET request """
        return self.page()

    def POST_AUTH(self):  # pylint: disable=arguments-differ
        """ POST request """
        username = self.user_manager.session_username()
        user_input = web.input()

        # Change to professors right when available
        if "new_courseid" in user_input and self.user_manager.user_is_superadmin():
            try:
                export(self.template_factory, self.course_factory, user_input["templateid"], user_input["new_courseid"], username)
                raise web.redirect(self.app.get_homepath() + "/admin/{}".format(user_input["new_courseid"]))
            except:
                message, success = _("Failed to create the course."), False
        # Change to professors right when available
        elif "new_templateid" in user_input and self.user_manager.user_is_superadmin():
            try:
                templateid = user_input["new_templateid"]
                self.template_factory.create_course(templateid, {"name": templateid, "editors": [username]})
                message, success = _("Template created."), True
            except:
                message, success = _("Failed to create the course."), False
        elif "pull" in user_input and self.user_manager.user_is_superadmin():
            try:
                self.template_factory.pull_git_templates()
                message, success = _("Templates pulled."), True
            except:
                message, success = _("Failed to pull the course."), False
        else:
            return self.page()

        return self.page(success, message)

    def page(self, success=None, message=""):
        """ Get all data and display the page """
        template_filter = lambda elem: not elem[1].is_private() or self.user_manager.has_staff_rights_on_course(elem[1])
        templates = dict(filter(template_filter, self.template_factory.get_all_courses().items()))
        # Change to professors right when available
        if self.user_manager.user_is_superadmin():
            return self.template_helper.get_custom_renderer('frontend/plugins/template/templates').template_list(
                templates,
                success,
                message)
        else:
            raise web.notfound()
