# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

# [Source code integration]: move to inginious.frontend.pages.course_admin

""" Import Tasks """
import tarfile

import web

from inginious.common.custom_yaml import load
from inginious.common.exceptions import TaskUnreadableException
from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from inginious.frontend.plugins.template.pages.template_admin.utils import INGIniousTemplateAdminPage


class ImportTasks(INGIniousAdminPage):
    """ Import Tasks """

    def GET_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ GET request """
        course, __ = self.get_course_and_check_rights(courseid, allow_all_staff=False)

        return self.page(course)

    def POST_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ POST request """
        course, __ = self.get_course_and_check_rights(courseid, allow_all_staff=False)

        data = web.input(archive_file={})
        imported_tasks, renamed_tasks = [], {}
        errors = []

        try:
            with tarfile.open(fileobj=data["archive_file"].file) as tar:
                elements = tar.getnames()

                if "import_inginious_file" in data:
                    # import tasks
                    for taskid in get_tasks_id(elements):
                        try:
                            #get files
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
                            task_descriptor = self.task_factory.get_task_descriptor_content(courseid, new_taskid)
                            if not check_task_descriptor(task_descriptor):
                                raise TaskUnreadableException("Invalid task config format")
                            task_descriptor["categories"] = []
                            self.task_factory.update_task_descriptor_content(courseid, taskid, task_descriptor)

                            imported_tasks.append(new_taskid)
                        except:
                            errors.append(_("Invalid format for task ") + taskid)
                            if new_taskid in course.get_tasks():
                                self.task_factory.delete_task(courseid, new_taskid)

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
        except:
            errors.append(_("Invalid archive format"))

        return self.page(course, errors, not errors)

    def page(self, course, errors=None, validated=False):
        """ Get all data and display the page """
        return self.template_helper.get_custom_renderer(
            'frontend/plugins/import_tasks').import_tasks(course, errors, validated)


class ImportTasksTemplate(INGIniousTemplateAdminPage, ImportTasks):
    """ Template equivalent """


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
