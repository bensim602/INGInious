# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

# [Source code integration]: load in function _update_cache of CourseFactory and pass to Course in constructor,
# update _cache_update_needed accordingly, add getter for _toc instance variable
from inginious.common.base import loads_json_or_yaml, get_json_or_yaml, id_checker
from inginious.common.exceptions import InvalidNameException


# [Source code integration]: load in function _update_cache of CourseFactory and pass to Course in constructor,
# update _cache_update_needed accordingly, add getter for _toc instance variable
def get_toc(course):
    """
    :param course: the course containing the toc
    :return: the content of the file toc.yaml if the file exist [] otherwise
    """
    course_fs = course.get_fs()
    if course_fs.exists("toc.yaml"):
        return loads_json_or_yaml("toc.yaml", course_fs.get("toc.yaml").decode("utf-8"))
    else:
        return []


# [Source code integration]: move to CourseFactory as instance method, replace course_factory by self
def update_toc_content(course_factory, courseid, content):
    """
    Updates the content of the structure that describes the course
    :param course_factory: the course factory
    :param courseid: the course id of the course
    :param content: the new structure that replaces the old content
    :raise InvalidNameException, CourseNotFoundException
    """
    if not id_checker(courseid):
        raise InvalidNameException("Course with invalid name: " + courseid)

    course_factory.get_course_fs(courseid).put("toc.yaml", get_json_or_yaml("toc.yaml", content))


# [Source code integration]: move to WebAppCourse as instance method, replace course by self and
# toc by _toc instance variable
def check_toc(course, toc):
    """
    :param course: the course in which the toc is
    :param toc: the raw content of the table of content
    :return: (True, "Valid TOC") if the toc has a valid format and (False, The error message) otherwise
    """
    try:
        tasks = course.get_tasks()
        for section in toc:
            if "id" not in section:
                return False, "Invalid TOC: No id for section"
            if "rank" not in section:
                return False, "Invalid TOC: No rank for section"
            if "title" not in section:
                return False, "Invalid TOC: No title for section"

            if "sections_list" in section:
                valid, message = check_toc(course, section["sections_list"])
                if not valid:
                    return False, message
            elif "tasks_list" in section:
                for task in section["tasks_list"]:
                    if task not in tasks:
                        return False, "Invalid TOC: Invalid taskID (" + task + ")"
            else:
                return False, "Invalid TOC: Section don't contain a sections list nor a tasks list"
    except:
        return False, "Invalid TOC"
    return True, "Valid TOC"


# [Source code integration]: move to WebAppCourse as instance method, replace toc by _toc instance variable
def order(toc):
    """
    Reorder the structure according to the ranks
    :param toc: the toc to reorder
    """
    toc.sort(key=lambda k: k['rank'])
    for section in toc:
        if "sections_list" in section:
            order(section["sections_list"])
        elif "tasks_list" in section:
            section["tasks_list"] = sorted(section["tasks_list"], key=section["tasks_list"].get)


# [Source code integration]: move to WebAppCourse as instance method, replace course by self and
# get_toc by _toc instance variable
def get_course_structure(course, orelse=None):
    """
    :param course: the course in which the toc is
    :return: the structure of the course
    """
    course_structure = get_toc(course)
    valid, _ = check_toc(course, course_structure)
    if not (course_structure and valid):
        course_structure = orelse if orelse is not None else [{"id": "tasks-list", "title": "List of exercises",
                                                               "tasks_list": course.get_tasks()}]
    else:
        order(course_structure)
    return course_structure
