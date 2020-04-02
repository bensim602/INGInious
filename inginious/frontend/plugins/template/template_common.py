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


def export(source_factory, destination_factory, source_id, destination_id, user, export_as_template=False):
    """
    Create a new course based on a template
    :param source_factory: the course factory in which the course is
    :param destination_factory: the template factory in which the template is
    :param destination_id: the id of the course
    :param source_id: the id of the template
    :param user: user that make the export
    :param export_as_template: true if export is from course to template false otherwise
    :param export_as_template: true if export is from course to template false otherwise
    :raise TemplateExportException if the copy failed
    """
    try:
        course = source_factory.get_course(source_id)

        source_fs = source_factory.get_course(source_id).get_fs()
        source_content = course.get_descriptor()

        source_name = source_content.get("name", destination_id)
        source_description = source_content.get("description", "")
        source_tags = source_content.get("tags", {})

        descriptor = {"name": source_name + "-" + destination_id, "description": source_description,
                      "tags": source_tags, "accessible": False}

        if export_as_template:
            descriptor["editors"] = [user]
        else:
            descriptor["admins"] = [user]
            descriptor["source"] = source_id

        # create the course
        destination_factory.create_course(destination_id, descriptor)
        destination_fs = destination_factory.get_course(destination_id).get_fs()

        # copy files needed
        for element in source_fs.list():
            if not match_some(["course.yaml", "course.json", "\.(.*)"], element):
                destination_fs.copy_to(source_fs.prefix + element, element)

    except Exception as e:
        # remove course if files copy failed
        if destination_id in source_factory.get_all_courses():
            source_factory.delete_course(destination_id)
        raise ExportException(e)


def match_some(patterns, value):
    """ return true if value match some pattern in patterns"""
    for element in patterns:
        if re.match(element, value):
            return True
    return False
