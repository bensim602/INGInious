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

from inginious.common.custom_yaml import load, dump
from inginious.common.exceptions import TaskUnreadableException
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
        data = web.input(archive_file={})
        if "export" in data:
            return self.export_elements(course, data)
        elif "import" in data:
            return self.import_elements(course, data)
        else:
            return self.page(course)

    def export_elements(self, course, data):
        errors = []
        export_tasks, exported_tasks = [], []
        export_sections = []

        # get input and filter
        for id in data.keys():
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

                sections_yaml = io.BytesIO(dump(filtered_toc).encode('utf-8'))
                info = tarfile.TarInfo(name="sections.yaml")
                info.size = sections_yaml.getbuffer().nbytes
                tar.addfile(info, fileobj=sections_yaml)
            except:
                errors.append(_("Error adding section description to the archive"))
        tmpfile.seek(0)

        if errors:
            return self.page(course, errors, None)
        else:
            web.header('Content-Type', 'application/x-gzip', unique=True)
            web.header('Content-Disposition', 'attachment; filename="inginious_tasks.tgz"', unique=True)
            return tmpfile

    def import_elements(self, course, data):
        imported_tasks, renamed_tasks = [], {}
        errors = []

        try:
            with tarfile.open(fileobj=data["archive_file"].file) as tar:
                elements = tar.getnames()

                if "import_inginious_file" in data:
                    # import tasks
                    for taskid in get_tasks_id(elements):
                        try:
                            # get files
                            task_files = get_task_files(taskid, elements)
                            tar_members = [tar.getmember(task_file) for task_file in task_files]

                            # avoid tasks with same id
                            new_taskid = make_id_unique(taskid, course.get_tasks())
                            if taskid != new_taskid:
                                renamed_tasks[taskid] = new_taskid
                                for tar_member in tar_members:
                                    tar_member.name = new_taskid + tar_member.name.lstrip(taskid)

                            # extract files
                            tar.extractall(course.get_fs().prefix, tar_members)

                            # check task descriptor is in inginious format and remove tags
                            task_descriptor = self.task_factory.get_task_descriptor_content(course.get_id(), new_taskid)
                            if not check_task_descriptor(task_descriptor):
                                raise TaskUnreadableException("Invalid task config format")
                            task_descriptor["categories"] = []
                            self.task_factory.update_task_descriptor_content(course.get_id(), taskid, task_descriptor)

                            imported_tasks.append(new_taskid)
                        except:
                            errors.append(_("Invalid format for task ") + taskid)
                            if new_taskid in course.get_tasks():
                                self.task_factory.delete_task(course.get_id(), new_taskid)

                    # import sections
                    if "sections.yaml" in elements:
                        try:
                            from inginious.frontend.plugins.course_structure.webapp_course import \
                                get_sections_tasks_ids, replace_sections_tasks_ids, get_toc, update_toc_content

                            sections_content = load(tar.extractfile("sections.yaml").read())
                            replace_sections_tasks_ids(sections_content, renamed_tasks)

                            # if all tasks in the sections are imported, add sections to course structure and adapt rank
                            if all(elem in imported_tasks for elem in get_sections_tasks_ids(sections_content)):
                                toc = get_toc(course)
                                for section in sections_content:
                                    section["rank"] = len(toc)
                                    toc.append(section)

                                update_toc_content(self.course_factory, course.get_id(), toc)
                            else:
                                errors.append(_("Some tasks in the structure are not included in the archive"))
                        except:
                            errors.append(_("Sections not supported for this instance"))
        except Exception as e:
            print()
            errors.append(_("Invalid archive format"))

        return self.page(course, errors, None if errors else _("Import successful."))

    def page(self, course, errors=None, validated=None):
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


def get_tasks_id(elements):
    """
    :param elements: the list of names of elements in the archive
    :return: if the list come from a valid inginious archive, list all the tasks ids
    """
    return [element for element in elements if '/' not in element and element != "sections.yaml"]


def get_task_files(task, elements):
    """
    :param task: the id of the task
    :param elements: the list of names of elements in the archive
    :return: if the list come from a valid inginious archive, list all the files and directories linked to the task
    """
    return [element for element in elements if element.startswith(task)]


def check_task_descriptor(task_descriptor):
    """ Return true if task_descriptor is a valid task descriptor, false otherwise """
    if "environment" not in task_descriptor and "environment_type" not in task_descriptor:
        return False
    if "problems" not in task_descriptor:
        return False
    return True


# [Source code integration]: move to frontend.pages.utils
def make_id_unique(old_id, list_of_ids):
    """ Return an id corresponding to old id but unique with respect to the ids in list_of_ids """
    new_id, i = old_id, 1
    while new_id in list_of_ids:
        new_id = old_id + "_" + str(i)
        i += 1
    return new_id