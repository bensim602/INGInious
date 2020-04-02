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

    get_sections_ids_and_make_unique(content)

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


# [Source code integration]: move to WebAppCourse as instance method, replace course by self
def get_ids_and_make_unique(course):
    """
    :param course: the course in which the toc is
    :return: all the ids of the sections and modify the structure such that there is no duplicated ids
    """
    return get_sections_ids_and_make_unique(get_toc(course))


# [Source code integration]: move to WebAppCourse
def get_sections_ids_and_make_unique(sections, ids=None):
    """
    :param ids:
    :param sections: the sections to inspect
    :return: the ids of the sections and their subsections and modify the structure such that there is no duplicated ids
    """
    if ids is None:
        ids = []
    for section in sections:
        section["id"] = make_id_unique(section["id"], ids)
        ids.append(section["id"])
        if "sections_list" in section:
            ids = get_sections_ids_and_make_unique(section["sections_list"], ids)
    return ids


# [Source code integration]: move to WebAppCourse as instance method, replace course by self
def get_tasks_id(course):
    """
    :param course: the course in which the toc is
    :return: all the ids of the tasks
    """
    return get_sections_tasks_ids(get_toc(course))


# [Source code integration]: move to WebAppCourse
def get_sections_tasks_ids(sections):
    """
    :param sections: the sections to inspect
    :return: the ids of the tasks and the one of their subsections
    """
    ids = []
    for section in sections:
        if "sections_list" in section:
            ids += get_sections_tasks_ids(section["sections_list"])
        elif "tasks_list" in section:
            ids += section["tasks_list"].keys()
    return ids


# [Source code integration]: move to WebAppCourse as instance method, replace course by self
def replace_tasks_id(course, rename_table):
    """
    Replace all the tasks ids in the toc according to the rename_table
    :param course: the course in which the toc is
    :param rename_table: a dictionary mapping initial ids and new ids
    """
    return replace_sections_tasks_ids(get_toc(course), rename_table)


# [Source code integration]: move to WebAppCourse
def replace_sections_tasks_ids(sections, rename_table):
    """
    Replace all the tasks ids in the sections according to the rename_table
    :param sections: the sections to inspect
    :param rename_table: a dictionary mapping initial ids and new ids
    """
    for section in sections:
        if "sections_list" in section:
            replace_sections_tasks_ids(section["sections_list"], rename_table)
        elif "tasks_list" in section:
            tasks_list = section["tasks_list"]
            for old_id, new_id in rename_table.items():
                if old_id in tasks_list:
                    tasks_list[new_id] = tasks_list.pop(old_id)


# [Source code integration]: move to frontend.pages.utils
def make_id_unique(old_id, list_of_ids):
    """ Return an id corresponding to old id but unique with respect to the ids in list_of_ids """
    new_id, i = old_id, 1
    while new_id in list_of_ids:
        new_id = old_id + "_" + str(i)
        i += 1
    return new_id
