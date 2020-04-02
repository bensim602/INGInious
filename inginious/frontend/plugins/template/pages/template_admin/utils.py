# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

# [Source code integration]: move to inginious.frontend.pages.template_admin
import web

from inginious.frontend.pages.course_admin.tags import CourseTagsPage
from inginious.frontend.pages.course_admin.task_edit import CourseEditTask
from inginious.frontend.pages.course_admin.task_edit_file import CourseTaskFiles, CourseTaskFileUpload
from inginious.frontend.pages.course_admin.task_list import CourseTaskListPage
from inginious.frontend.pages.utils import INGIniousAuthPage
from inginious.frontend.plugins.template.template_factory import TemplateFactory


class INGIniousTemplatePage(INGIniousAuthPage):
    """
    An improved version of INGIniousAuthPage that replace te factories with the one for template
    """

    @property
    def course_factory(self) -> TemplateFactory:
        return self.plugin_manager.call_hook("template_factory")[0]

    @property
    def task_factory(self) -> TemplateFactory:
        return self.plugin_manager.call_hook("template_task_factory")[0]


class INGIniousTemplateAdminPage(INGIniousTemplatePage):
    """
    An improved version of INGIniousTemplatePage that checks rights for the edition of the template
    """

    def get_course_and_check_rights(self, courseid, taskid=None, allow_all_staff=True):
        """ Returns the course with id ``courseid`` and the task with id ``taskid``, and verify the rights of the user.
            Raise web.notfound() when there is no such course of if the users has not enough rights.

            :param courseid: the course on which to check rights
            :param taskid: If not None, returns also the task with id ``taskid``
            :param allow_all_staff: for compatibility but useless
            :returns (Course, Task)
        """

        try:
            course = self.course_factory.get_course(courseid)
            if not self.user_manager.has_admin_rights_on_course(course) or courseid.endswith("_g1t"):
                raise web.notfound()

            if taskid is None:
                return course, None
            else:
                return course, course.get_task(taskid)
        except:
            raise web.notfound()


class TemplateTaskListPage(INGIniousTemplateAdminPage, CourseTaskListPage):
    """ List informations about all tasks """


class TemplateEditTask(INGIniousTemplateAdminPage, CourseEditTask):
    """ Pages that allow editing of tasks """


class TemplateTaskFiles(INGIniousTemplateAdminPage, CourseTaskFiles):
    """ Allow to create/edit/delete/move/download files associated to tasks """


class TemplateTaskFileUpload(INGIniousTemplateAdminPage, CourseTaskFileUpload):
    """ Upload task files """


class TemplateTagsPage(INGIniousTemplateAdminPage, CourseTagsPage):
    """ Tags management """


def template_structure_editor_page():
    try:
        from inginious.frontend.plugins.course_structure.structure_editor import CourseEditor

        class TemplateStructureEditorPage(INGIniousTemplateAdminPage, CourseEditor):
            """ Couse structure editor """

        return TemplateStructureEditorPage
    except:
        raise web.notfound()


class CourseRedirect(INGIniousTemplateAdminPage):
    """ Redirect editors to /settings """

    def GET_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ GET request """
        raise web.seeother(self.app.get_homepath() + '/edit_template/{}/settings'.format(courseid))

    def POST_AUTH(self, courseid):  # pylint: disable=arguments-differ
        """ POST request """
        return self.GET_AUTH(courseid)
