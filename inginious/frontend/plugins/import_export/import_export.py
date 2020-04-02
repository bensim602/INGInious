# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" Export tasks"""
import copy
import io
import os
import tarfile
import tempfile
import web

import inginious.common.custom_yaml
from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from inginious.frontend.plugins.template.pages.template_admin.utils import INGIniousTemplateAdminPage


class ImportExport(INGIniousAdminPage):
    """ Export tasks """
    def GET_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ GET request """
        course, __ = self.get_course_and_check_rights(courseid, allow_all_staff=False)

        return self.page(course)

    def POST_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ POST request """
        course, __ = self.get_course_and_check_rights(courseid, allow_all_staff=False)

        errors = []
        export_tasks, exported_tasks = [], []
        export_sections = []

        # get input and filter
        for id in web.input().keys():
            if id.startswith("task_"):
                export_tasks.append(id[5:])
            elif id.startswith("section_"):
                export_sections.append(id[8:])

        tmpfile = tempfile.TemporaryFile()
        with tarfile.open(fileobj=tmpfile, mode='w:gz') as tar:
            # export tasks
            for taskid in export_tasks:
                try:
                    task_path = course.get_task(taskid).get_fs().prefix.rstrip('/')
                    tar.add(task_path, arcname=os.path.basename(task_path))
                    exported_tasks.append(taskid)
                except:
                    errors.append(_("Could not export task ") + taskid)
            # export sections
            try:
                from inginious.frontend.plugins.course_structure.webapp_course import get_sections_tasks_ids, \
                    get_course_structure
                toc = get_course_structure(course)
                filtered_toc = filter_sections(toc, export_sections, exported_tasks)

                sections_yaml = io.BytesIO(inginious.common.custom_yaml.dump(filtered_toc).encode('utf-8'))
                info = tarfile.TarInfo(name="sections.yaml")
                info.size = sections_yaml.getbuffer().nbytes
                tar.addfile(info, fileobj=sections_yaml)
            except:
                errors.append(_("Error adding section description to the archive"))
        tmpfile.seek(0)

        if errors:
            return self.page(course, errors, False)
        else:
            web.header('Content-Type', 'application/x-gzip', unique=True)
            web.header('Content-Disposition', 'attachment; filename="inginious_tasks.tgz"', unique=True)
            return tmpfile

    def page(self, course, errors=None, validated=False):
        """ Get all data and display the page """
        try:
            from inginious.frontend.plugins.course_structure.webapp_course import get_course_structure
            toc = get_course_structure(course)
        except:
            toc = [{"id": "tasks-list", "title": "List of exercises", "tasks_list": course.get_tasks()}]
        return self.template_helper.get_custom_renderer(
            'frontend/plugins/import_export').import_export(course, toc, course.get_tasks(), errors, validated)


class ImportExportTemplate(INGIniousTemplateAdminPage, ImportExport):
    """ Template equivalent """


def filter_sections(sections, selected_sections, selected_tasks):
    """
    :param sections: the sections to filter
    :param selected_sections: the section ids to keep
    :param selected_tasks: the task ids to keep
    :return: the sections with sections and tasks not in selected_sections and selected_tasks filtered out
    """
    filtered_sections = []
    for section in sections:
        # add section and filter content
        if section["id"] in selected_sections:
            new_section = copy.deepcopy(section)
            new_section["rank"] = len(filtered_sections)
            if "tasks_list" in new_section:
                new_section["tasks_list"] = filter_tasks_list(new_section["tasks_list"], selected_tasks)
            elif "sections_list" in new_section:
                new_section["sections_list"] = filter_sections(new_section["sections_list"], selected_sections, selected_tasks)
            filtered_sections.append(new_section)
        # check subsections for selected elements
        elif "sections_list" in section:
            for new_section in filter_sections(section["sections_list"], selected_sections, selected_tasks):
                new_section["rank"] = len(filtered_sections)
                filtered_sections.append(new_section)

    return filtered_sections


def filter_tasks_list(tasks_list, selected_tasks):
    """
    :param tasks_list: the initial task list
    :param selected_tasks: the task ids of the task to keep
    :return: the task list with the task not in selected_tasks filtered out
    """
    new_tasks_list, i = {}, 0
    for task_id in tasks_list:
        if task_id in selected_tasks:
            new_tasks_list[task_id] = i
            i += 1
    return new_tasks_list