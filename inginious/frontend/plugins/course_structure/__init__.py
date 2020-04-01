# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.
import os
import web

from inginious.frontend.plugins.course_structure.course_page import CoursePage
from inginious.frontend.plugins.course_structure.structure_editor import CourseEditor


def switch_view(course, template_helper):
    return str(template_helper.get_custom_renderer('frontend/plugins/course_structure', layout=False).switch_view(course))


def course_admin_menu(course):
    return "structure_editor", "<i class='fa fa-pencil fa-fw'></i>&nbsp; " + _("Structure editor")

class StaticMockPage(object):
    """Get the local javascript file"""
    def GET(self):
        try:
            with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "structure_editor.js"), 'rb') as file:
                return file.read()
        except:
            raise web.notfound()

    def POST(self):
        return self.GET()


def init(plugin_manager, _, _2, _3):
    """ Init the plugin """
    plugin_manager.add_hook('course_menu', switch_view)
    plugin_manager.add_page('/course_section/([^/]+)', CoursePage)

    plugin_manager.add_hook("course_admin_menu", course_admin_menu)
    plugin_manager.add_page('/admin/([^/]+)/structure_editor', CourseEditor)
    plugin_manager.add_page('/plugins/course_structure/structure_editor.js', StaticMockPage)
