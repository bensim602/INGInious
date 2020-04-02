# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" A template class with some modification for the interface """

# [Source code integration]: move to inginious.frontend
import copy
import re

from inginious.common.courses import Course


class ExportException(Exception):
    pass


class Template(Course):
    def __init__(self, courseid, content, template_content, course_fs, task_factory, hook_manager):
        super(Template, self).__init__(courseid, content, course_fs, task_factory, hook_manager)
        self._template_content = template_content if template_content is not None else {}

    def get_template_descriptor(self):
        """ Get (a copy) the description and skills of the template and his content """
        return copy.deepcopy(self._template_content)

    def get_structure_description(self):
        """ Get (a copy) the descriptions of the sections in the structure """
        return copy.deepcopy(self._template_content.get("structure_description", {}))

    def get_structure_skills(self):
        """ Get (a copy) the skills of the sections in the structure """
        return copy.deepcopy(self._template_content.get("structure_skills", {}))
