# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.
from inginious.frontend.plugins.course_structure.course_page import CoursePage


def switch_view(course, template_helper):
    return str(template_helper.get_custom_renderer('frontend/plugins/course_structure', layout=False).switch_view(course))


def init(plugin_manager, _, _2, _3):
    """ Init the plugin """
    plugin_manager.add_hook('course_menu', switch_view)
    plugin_manager.add_page('/course_section/([^/]+)', CoursePage)
