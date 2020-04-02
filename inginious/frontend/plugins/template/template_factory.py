# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

# [Source code integration]: move to inginious.common

""" Factory for loading templates from disk """
from inginious.common.base import loads_json_or_yaml, get_json_or_yaml, id_checker
from inginious.common.course_factory import CourseFactory
from inginious.common.exceptions import CourseAlreadyExistsException, InvalidNameException, CourseNotFoundException, \
    CourseUnreadableException
from inginious.common.hook_manager import HookManager
from inginious.common.task_factory import TaskFactory
from inginious.common.tasks import Task
from inginious.frontend.plugins.template.template_common import Template


class TemplateFactory(CourseFactory):

    def get_template_descriptor_content(self, templateid):
        """
        :param templateid: the id of the template
        :raise InvalidNameException, CourseNotFoundException, CourseUnreadableException
        :return: the content of the file that describes the template
        """
        path = self._get_template_descriptor_path(templateid)
        return loads_json_or_yaml(path, self._filesystem.get(path).decode("utf-8"))

    def update_template_descriptor_content(self, templateid, content):
        """
        Updates the content of the file that describes the template
        :param templateid: the id of the template
        :param content: the new content that replaces the old one
        :raise InvalidNameException, CourseNotFoundException
        """
        path = self._get_template_descriptor_path(templateid)
        self._filesystem.put(path, get_json_or_yaml(path, content))

    def _get_template_descriptor_path(self, courseid):
        """
        [Source code integration]: generalise with get_course_descriptor_path
        :param courseid: the course id of the course
        :raise InvalidNameException, CourseNotFoundException
        :return: the path to the description of the template
        """
        if not id_checker(courseid):
            raise InvalidNameException("Template with invalid name: " + courseid)
        course_fs = self.get_course_fs(courseid)
        if course_fs.exists("template.yaml"):
            return courseid+"/template.yaml"
        raise CourseNotFoundException()

    def create_course(self, templateid, init_content, init_description=None):
        """
        :param init_description: initial template descriptor content
        :param templateid: the course id of the course
        :param init_content: initial descriptor content
        :param init_description: initial description of the template
        :raise InvalidNameException or CourseAlreadyExistsException
        Create a new course folder and set initial descriptor content, folder can already exist
        Set initial template description
        """
        super().create_course(templateid, init_content)
        template_fs = self.get_course_fs(templateid)
        if template_fs.exists("template.yaml"):
            raise CourseAlreadyExistsException("Template with id " + templateid + " already exists.")
        else:
            template_fs.put("template.yaml", get_json_or_yaml("template.yaml", init_description))

    def _cache_update_needed(self, courseid):
        """
        [Source code integration]: make function generic with list opf files
        :param courseid: the (valid) course id of the course
        :raise InvalidNameException, CourseNotFoundException
        :return: True if an update of the cache is needed, False else, also check for change in the template description
        """
        if courseid not in self._cache:
            return True

        try:
            descriptor_name = self._get_course_descriptor_path(courseid)
            template_descriptor_name = self._get_template_descriptor_path(courseid)
            last_update = {descriptor_name: self._filesystem.get_last_modification_time(descriptor_name),
                           template_descriptor_name: self._filesystem.get_last_modification_time(template_descriptor_name)}

            translations_fs = self._filesystem.from_subfolder("$i18n")
            if translations_fs.exists():
                for f in translations_fs.list(folders=False, files=True, recursive=False):
                    lang = f[0:len(f) - 3]
                    if translations_fs.exists(lang + ".mo"):
                        last_update["$i18n/" + lang + ".mo"] = translations_fs.get_last_modification_time(lang + ".mo")
        except:
            raise CourseNotFoundException()

        last_modif = self._cache[courseid][1]
        for filename, mftime in last_update.items():
            if filename not in last_modif or last_modif[filename] < mftime:
                return True

        return False

    def _update_cache(self, courseid):
        """
        Updates the cache, 1 more parameter to initialise Template
        :param courseid: the (valid) course id of the course
        :raise InvalidNameException, CourseNotFoundException, CourseUnreadableException
        """
        path_to_descriptor = self._get_course_descriptor_path(courseid)
        path_to_template_descriptor = self._get_template_descriptor_path(courseid)
        try:
            course_descriptor = loads_json_or_yaml(path_to_descriptor, self._filesystem.get(path_to_descriptor).decode("utf8"))
            template_descriptor = loads_json_or_yaml(path_to_descriptor, self._filesystem.get(path_to_template_descriptor).decode("utf8"))
        except Exception as e:
            raise CourseUnreadableException(str(e))

        last_modif = {path_to_descriptor: self._filesystem.get_last_modification_time(path_to_descriptor),
                      path_to_template_descriptor: self._filesystem.get_last_modification_time(path_to_template_descriptor)}
        translations_fs = self._filesystem.from_subfolder("$i18n")
        if translations_fs.exists():
            for f in translations_fs.list(folders=False, files=True, recursive=False):
                lang = f[0:len(f) - 3]
                if translations_fs.exists(lang + ".mo"):
                    last_modif["$i18n/" + lang + ".mo"] = translations_fs.get_last_modification_time(lang + ".mo")

        self._cache[courseid] = (
            self._course_class(courseid, course_descriptor, template_descriptor, self.get_course_fs(courseid),
                               self._task_factory, self._hook_manager),
            last_modif
        )

        self._task_factory.update_cache_for_course(courseid)


def create_factories(fs_provider, task_problem_types, hook_manager=None, course_class=Template, task_class=Task):
    """
    [Source code integration]: make function genral for course and template
    Shorthand for creating Factories
    :param fs_provider: A FileSystemProvider leading to the courses
    :param hook_manager: an Hook Manager instance. If None, a new Hook Manager is created
    :param course_class:
    :param task_class:
    :return: a tuple with two objects: the first being of type CourseFactory, the second of type TaskFactory
    """
    if hook_manager is None:
        hook_manager = HookManager()

    task_factory = TaskFactory(fs_provider, hook_manager, task_problem_types, task_class)
    return TemplateFactory(fs_provider, task_factory, hook_manager, course_class), task_factory