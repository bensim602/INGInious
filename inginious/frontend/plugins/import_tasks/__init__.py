# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.
from inginious.frontend.plugins.import_tasks.export_tasks import ExportTasks, ExportTasksTemplate


def export_tasks(course):
    return "export_tasks", "<i class='fa fa-upload fa-fw'></i>&nbsp; " + _("Export tasks")


def init(plugin_manager, _, _2, _3):
    """ Init the plugin """
    plugin_manager.add_hook("course_admin_menu", export_tasks)
    plugin_manager.add_page('/admin/([^/]+)/export_tasks', ExportTasks)

    plugin_manager.add_hook("template_admin_menu", export_tasks)
    plugin_manager.add_page('/edit_template/([^/]+)/export_tasks', ExportTasksTemplate)
