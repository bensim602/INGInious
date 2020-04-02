# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

# [Source code integration]: move to inginious.frontend.pages.template_admin
import web

from inginious.frontend.plugins.template.pages.template_admin.utils import INGIniousTemplateAdminPage


class TemplateDescription(INGIniousTemplateAdminPage):
    """ Template description """

    def GET_AUTH(self, temlateid):  # pylint: disable=arguments-differ
        """ GET request """
        template, _ = self.get_course_and_check_rights(temlateid, allow_all_staff=False)
        return self.page(template)

    def POST_AUTH(self, templateid):  # pylint: disable=arguments-differ
        """ POST request """
        template, __ = self.get_course_and_check_rights(templateid, allow_all_staff=False)

        errors = []

        template_content = {}
        try:
            data = web.input()
            template_content = template.get_template_descriptor()

            template_content["short_description"] = data["short_description"]
            template_content["description"] = data["description"]
            template_content["skills"] = list(map(str.strip, data["skills"].split(',')))
            if len(template_content["skills"]) == 1 and template_content["skills"][0].strip() == "":
                template_content["skills"] = []

            try:
                from inginious.frontend.plugins.course_structure.webapp_course import get_ids_and_make_unique
                new_structure_description = {}
                new_structure_skills = {}
                for section_id in get_ids_and_make_unique(template):
                    if "description_section_" + section_id in data:
                        new_structure_description[section_id] = data["description_section_" + section_id]
                    else:
                        new_structure_description[section_id] = template.get_structure_description().get(section_id, "No description available.")
                    if "skills_section_" + section_id in data:
                        new_structure_skills[section_id] = list(map(str.strip, data["skills_section_" + section_id].split(',')))
                        if len(new_structure_skills[section_id]) == 1 and new_structure_skills[section_id][0].strip() == "":
                            new_structure_skills[section_id] = []
                    else:
                        new_structure_skills[section_id] = template.get_structure_skills().get(section_id, [])
                template_content["structure_description"] = new_structure_description
                template_content["structure_skills"] = new_structure_skills
            except:
                pass

        except:
            errors.append(_('User returned an invalid form.'))

        if len(errors) == 0:
            self.course_factory.update_template_descriptor_content(templateid, template_content)
            errors = None
            template, __ = self.get_course_and_check_rights(templateid, allow_all_staff=False)  # don't forget to reload the modified course

        return self.page(template, errors, errors is None)

    def page(self, template, errors=None, saved=False):
        """ Get all data and display the page """
        try:
            from inginious.frontend.plugins.course_structure.webapp_course import get_course_structure
            toc = get_course_structure(template)
        except:
            toc = []

        return self.template_helper.get_custom_renderer('frontend/plugins/template/templates').template_admin.description(template, toc, errors, saved)