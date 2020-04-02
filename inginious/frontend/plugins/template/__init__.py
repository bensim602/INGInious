# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.
import web

from inginious.frontend.tasks import WebAppTask
from inginious.common.filesystems.local import LocalFSProvider
from inginious.frontend.pages.utils import INGIniousAuthPage

from inginious.frontend.plugins.template.template_common import Template
from inginious.frontend.plugins.template.template_factory import create_factories
from inginious.frontend.plugins.template.template_frontend import WebAppTemplate

from inginious.frontend.plugins.template.pages.template_list import TemplateList
from inginious.frontend.plugins.template.pages.template import TemplatePage

from inginious.frontend.plugins.template.pages.template_admin.settings import TemplateSettings
from inginious.frontend.plugins.template.pages.template_admin.description import TemplateDescription
from inginious.frontend.plugins.template.pages.template_admin.danger_zone import TemplateDangerZonePage
from inginious.frontend.plugins.template.pages.template_admin.utils import CourseRedirect, TemplateTaskListPage, \
    TemplateEditTask, TemplateTaskFiles, TemplateTaskFileUpload, TemplateTagsPage, template_structure_editor_page

from inginious.frontend.plugins.template.pages.course_admin.templates import CourseAdminTemplates

from inginious.frontend.plugins.template.pages.course_admin.import_template_tasks import ImportTemplateTasks


def main_menu(template_helper):
    return str(template_helper.get_custom_renderer('frontend/plugins/template', layout=False).main_menu())


# [Source code integration]: move as part of the import_tasks extension
def import_tasks(template_helper, plugin_manager, user_manager, course):
    template_factory = plugin_manager.call_hook("template_factory")[0]
    template_filter = lambda elem: not elem[1].is_private() or user_manager.has_staff_rights_on_course(elem[1])
    templates = dict(filter(template_filter, template_factory.get_all_courses().items()))
    return _("Import from templates"), str(template_helper.get_custom_renderer('frontend/plugins/template', layout=False).import_tasks(templates, course))


def course_admin_menu(course):
    return "templates", "<i class='fa fa-file fa-fw'></i>&nbsp; " + _("Templates")


def init(plugin_manager, course_factory, _, plugin_config):
    """ Init the plugin """
    template_filesystem = LocalFSProvider(plugin_config["template_directory"])
    template_repo = plugin_config.get("template_repo", "https://github.com/bensim602/INGInious-templates.git")

    template_factory, template_task_factory = create_factories(template_filesystem,
                                                               course_factory.get_task_factory().get_problem_types(),
                                                               template_repo,
                                                               plugin_manager,
                                                               WebAppTemplate,
                                                               WebAppTask)

    plugin_manager.add_hook("template_factory", lambda: template_factory)
    plugin_manager.add_hook("template_task_factory", lambda: template_task_factory)

    plugin_manager.add_hook("main_menu", main_menu)
    plugin_manager.add_page('/template', TemplateList)
    plugin_manager.add_page('/template/([^/]+)', TemplatePage)

    plugin_manager.add_page('/edit_template/([^/]+)', CourseRedirect)
    plugin_manager.add_page('/edit_template/([^/]+)/settings', TemplateSettings)
    plugin_manager.add_page('/edit_template/([^/]+)/description', TemplateDescription)
    plugin_manager.add_page('/edit_template/([^/]+)/tasks', TemplateTaskListPage)
    plugin_manager.add_page('/edit_template/([^/]+)/edit/task/([^/]+)', TemplateEditTask)
    plugin_manager.add_page('/edit_template/([^/]+)/edit/task/([^/]+)/files', TemplateTaskFiles)
    plugin_manager.add_page('/edit_template/([^/]+)/edit/task/([^/]+)/dd_upload', TemplateTaskFileUpload)
    plugin_manager.add_page('/edit_template/([^/]+)/tags', TemplateTagsPage)
    plugin_manager.add_page('/edit_template/([^/]+)/danger', TemplateDangerZonePage)
    plugin_manager.add_page('/edit_template/([^/]+)/structure_editor', template_structure_editor_page())

    plugin_manager.add_hook("course_admin_menu", course_admin_menu)
    plugin_manager.add_page('/admin/([^/]+)/templates', CourseAdminTemplates)

    # [Source code integration]: move as part of the import_tasks extension
    plugin_manager.add_hook("import_tasks", import_tasks)
    plugin_manager.add_page('/admin/([^/]+)/import_tasks/template/([^/]+)', ImportTemplateTasks)
