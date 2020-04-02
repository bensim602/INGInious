# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.
from inginious.frontend.tasks import WebAppTask
from inginious.common.filesystems.local import LocalFSProvider

from inginious.frontend.plugins.template.template_common import Template
from inginious.frontend.plugins.template.template_factory import create_factories
from inginious.frontend.plugins.template.template_frontend import WebAppTemplate

from inginious.frontend.plugins.template.pages.template_list import TemplateList


def main_menu(template_helper):
    return str(template_helper.get_custom_renderer('frontend/plugins/template', layout=False).main_menu())


def init(plugin_manager, course_factory, _, plugin_config):
    """ Init the plugin """
    template_filesystem = LocalFSProvider(plugin_config["template_directory"])

    template_factory, template_task_factory = create_factories(template_filesystem,
                                                               course_factory.get_task_factory().get_problem_types(),
                                                               plugin_manager,
                                                               WebAppTemplate,
                                                               WebAppTask)

    plugin_manager.add_hook("template_factory", lambda: template_factory)
    plugin_manager.add_hook("template_task_factory", lambda: template_task_factory)

    plugin_manager.add_hook("main_menu", main_menu)
    plugin_manager.add_page('/template', TemplateList)

