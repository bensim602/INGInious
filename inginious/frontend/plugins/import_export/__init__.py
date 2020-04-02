# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.
from inginious.frontend.plugins.import_export.import_export import ImportExport, ImportExportTemplate


def export_tasks(course):
    return "import_export", "<i class='fa fa-upload fa-fw'></i>&nbsp; " + _("Import/Export")


def init(plugin_manager, _, _2, _3):
    """ Init the plugin """
    plugin_manager.add_hook("course_admin_menu", export_tasks)
    plugin_manager.add_page('/admin/([^/]+)/import_export', ImportExport)

    plugin_manager.add_hook("template_admin_menu", export_tasks)
    plugin_manager.add_page('/edit_template/([^/]+)/import_export', ImportExportTemplate)