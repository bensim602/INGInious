# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

# [Source code integration]: move as part of the import_tasks extension

""" Import template tasks """

import web

from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from inginious.frontend.plugins.template.template_factory import TemplateFactory


class ImportTemplateTasks(INGIniousAdminPage):
    """ Import template tasks """

    @property
    def template_factory(self) -> TemplateFactory:
        return self.plugin_manager.call_hook("template_factory")[0]

    def get_template(self, templateid):
        """ Return the template """
        try:
            template = self.template_factory.get_course(templateid)
        except:
            raise web.notfound()
        if template.is_private() and not self.user_manager.has_staff_rights_on_course(template):
            raise web.notfound()

        return template

    def GET_AUTH(self, courseid, templateid):  # pylint: disable=arguments-differ
        """ GET request """
        course, __ = self.get_course_and_check_rights(courseid, allow_all_staff=False)
        template = self.get_template(templateid)

        return self.page(course, template)

    def POST_AUTH(self, courseid, templateid):  # pylint: disable=arguments-differ
        """ POST request """
        try:
            from inginious.frontend.plugins.import_export.import_export import filter_sections
        except:
            raise web.notfound()

        course, __ = self.get_course_and_check_rights(courseid, allow_all_staff=False)
        template = self.get_template(templateid)

        errors = []
        import_tasks, imported_tasks = [], []
        import_sections = []
        renamed_tasks = {}

        # get inputs and filter them
        for id in web.input().keys():
            if id.startswith("task_"):
                import_tasks.append(id[5:])
            elif id.startswith("section_"):
                import_sections.append(id[8:])

        # import tasks
        for taskid in import_tasks:
            try:
                # avoid tasks with same id
                new_taskid = make_id_unique(taskid, course.get_tasks())
                if taskid != new_taskid:
                    renamed_tasks[taskid] = new_taskid

                # copy files
                task_fs = template.get_task(taskid).get_fs()
                course.get_fs().copy_to(task_fs.prefix, new_taskid)

                # remove tags from the task descriptor
                task_descriptor = self.task_factory.get_task_descriptor_content(courseid, new_taskid)
                task_descriptor["categories"] = []
                self.task_factory.update_task_descriptor_content(courseid, taskid, task_descriptor)

                imported_tasks.append(taskid)
            except:
                errors.append("Could not import task " + taskid)

        # import sections
        try:
            from inginious.frontend.plugins.course_structure.webapp_course import get_toc, update_toc_content, \
                replace_sections_tasks_ids, get_course_structure
            template_toc, course_toc = get_course_structure(template), get_toc(course)

            filtered_toc = filter_sections(template_toc, import_sections, imported_tasks)
            replace_sections_tasks_ids(filtered_toc, renamed_tasks)

            # add sections to course structure and adapt rank
            for section in filtered_toc:
                section["rank"] = len(course_toc)
                course_toc.append(section)

            update_toc_content(self.course_factory, course.get_id(), course_toc)
        except Exception as e:
            print(e)
            errors.append("Could not import sections")

        return self.page(course, template, errors, not errors)

    def page(self, course, template, errors=None, validated=False):
        """ Get all data and display the page """
        try:
            from inginious.frontend.plugins.course_structure.webapp_course import get_course_structure
            toc = get_course_structure(template)
        except:
            toc = [{"id": "tasks-list", "title": "List of exercises", "tasks_list": template.get_tasks()}]
        return self.template_helper.get_custom_renderer(
            'frontend/plugins/template/templates').course_admin.import_templates_tasks(course, template, toc, template.get_tasks(), errors, validated)


# [Source code integration]: move to frontend.pages.utils
def make_id_unique(old_id, list_of_ids):
    """ Return an id corresponding to old id but unique with respect to the ids in list_of_ids """
    new_id, i = old_id, 1
    while new_id in list_of_ids:
        new_id = old_id + "_" + str(i)
        i += 1
    return new_id
