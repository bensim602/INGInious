# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

# [Source code integration]: move file to inginious.frontend.pages.course_admin, register page,
# add link for course admin menu
import json
import web

from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from inginious.frontend.plugins.course_structure.webapp_course import get_course_structure, check_toc, update_toc_content


class CourseEditor(INGIniousAdminPage):
    """ Couse structure editor """

    def GET_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ GET request """
        course, __ = self.get_course_and_check_rights(courseid, allow_all_staff=False)
        return self.page(course)

    def POST_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ POST request """
        course, __ = self.get_course_and_check_rights(courseid, allow_all_staff=False)

        errors = []
        try:
            user_input = web.input()
            new_toc = json.loads(user_input["course_structure"])
            task_renamed = json.loads(user_input["task_renamed"])

            valid, message = check_toc(course, new_toc)
            if valid:
                update_toc_content(self.course_factory, courseid, new_toc)
            else:
                errors.append(message)

            for taskid, new_name in task_renamed.items():
                task_data = self.task_factory.get_task_descriptor_content(courseid, taskid)
                task_data["name"] = new_name
                self.task_factory.update_task_descriptor_content(courseid, taskid, task_data)
        except:
            errors.append(_("Something wrong happened"))

        if len(errors) == 0:
            errors = None

        return self.page(course, errors, errors is None)

    def page(self, course, errors=None, validated=False):
        """ Get all data and display the page """
        tasks = course.get_tasks()
        toc = get_course_structure(course, [])
        return self.template_helper.get_custom_renderer('frontend/plugins/course_structure').structure_editor(course,
                                                                                                              toc,
                                                                                                              tasks,
                                                                                                              errors,
                                                                                                              validated)