# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

# [Source code integration]: move to inginious.frontend.pages.template_admin
import web

from inginious.frontend.plugins.template.pages.template_admin.utils import INGIniousTemplateAdminPage


class TemplateSettings(INGIniousTemplateAdminPage):
    """ Template settings """

    def GET_AUTH(self, temlateid):  # pylint: disable=arguments-differ
        """ GET request """
        template, _ = self.get_course_and_check_rights(temlateid, allow_all_staff=False)
        return self.page(template)

    def POST_AUTH(self, templateid):  # pylint: disable=arguments-differ
        """ POST request """
        template, __ = self.get_course_and_check_rights(templateid, allow_all_staff=False)

        errors = []
        course_content = {}
        try:
            data = web.input()
            course_content = self.course_factory.get_course_descriptor_content(templateid)
            course_content['name'] = data['name']
            if course_content['name'] == "":
                errors.append(_('Invalid name'))
            course_content['description'] = data['description']
            course_content['editors'] = list(map(str.strip, data['editors'].split(',')))
            if not self.user_manager.user_is_superadmin() and self.user_manager.session_username() not in course_content['editors']:
                errors.append(_('You cannot remove yourself from the editors of this template'))

            if data["private"] == "true":
                course_content['private'] = True
            else:
                course_content['private'] = False

        except:
            errors.append(_('User returned an invalid form.'))

        if len(errors) == 0:
            self.course_factory.update_course_descriptor_content(templateid, course_content)
            errors = None
            template, __ = self.get_course_and_check_rights(templateid, allow_all_staff=False)  # don't forget to reload the modified course

        return self.page(template, errors, errors is None)

    def page(self, template, errors=None, saved=False):
        """ Get all data and display the page """
        return self.template_helper.get_custom_renderer('frontend/plugins/template/templates').template_admin.settings(template, errors, saved)