from inginious.common.tags import Tag
from inginious.frontend.parsable_text import ParsableText
from inginious.frontend.plugins.template import Template


class WebAppTemplate(Template):
    def __init__(self, courseid, content, template_content, course_fs, task_factory, hook_manager):
        super(WebAppTemplate, self).__init__(courseid, content, template_content, course_fs, task_factory, hook_manager)

        try:
            self._name = self._content['name']
        except:
            raise Exception("Template has an invalid name: " + self.get_id())

        if self._content.get('nofrontend', False):
            raise Exception("That template is not allowed to be displayed directly in the webapp")

        try:
            self._editors = self._content.get("editors", [])
            self._description = self._content.get('description', '')
            self._private = self._content.get("private", True)
            self._tags = {key: Tag(key, tag_dict, self.gettext) for key, tag_dict in self._content.get("tags", {}).items()}
        except:
            raise Exception("Template has an invalid YAML spec: " + self.get_id())

        try:
            short_desc = self._template_content.get("short_description", "No description available.")
            self._short_description = short_desc[:250] if len(short_desc) > 250 else short_desc
            self._template_description = self._template_content.get("description", "No description available.")
            self._template_skills = self._template_content.get("skills", [])
        except:
            raise Exception("Template has an invalid description: " + self.get_id())

        self.course_page = "template"
        self.admin_page = "edit_template"
        self.has_student = False

    def get_admins(self):
        """ Returns a list containing the usernames of the administrators of this course """
        return self._editors

    def get_staff(self):
        return self.get_admins()

    def get_name(self, language):
        """ Return the name of this course """
        return self.gettext(language, self._name) if self._name else ""

    def get_admin_menu(self, plugin_manager, user_manager):
        """ Return the element to display in the admin menu of the template """
        default_entries = [("settings", "<i class='fa fa-cog fa-fw'></i>&nbsp; " + _("Template settings")),
                           ("description", "<i class='fa fa-info fa-fw'></i>&nbsp; " + _("Template description")),
                           ("tasks", "<i class='fa fa-tasks fa-fw'></i>&nbsp; " + _("Tasks")),
                           ("tags", "<i class='fa fa-tags fa-fw'></i>&nbsp;" + _("Tags")),
                           ("danger", "<i class='fa fa-bomb fa-fw'></i>&nbsp; " + _("Danger zone"))]

        # Hook should return a tuple (link,name) where link is the relative link from the index of the course administration.
        additional_entries = [entry for entry in plugin_manager.call_hook('template_admin_menu', course=self) if
                              entry is not None]

        return default_entries + additional_entries

    def is_private(self):
        return self._private

    def get_template_short_descriptor(self, language):
        """ Returns the short description of the template (rax text max 250 char """
        return self.gettext(language, self._short_description) if self._short_description else ''

    def get_template_description(self, language):
        """ Returns the description of the template """
        description = self.gettext(language, self._template_description) if self._template_description else ''
        return ParsableText(description, "rst", translation=self.get_translation_obj(language))

    def get_template_skills(self, language):
        """ Returns the skills of the template """
        return [self.gettext(language, skill) for skill in self._template_skills]

    def get_section_description(self, language, section_id):
        """ Returns the skills for the section section_id of the template """
        description = self._template_content.get("structure_description", {}).get(section_id,
                                                                                  "No description available.")
        return ParsableText(self.gettext(language, description), "rst", translation=self.get_translation_obj(language))

    def get_section_skills(self, language, section_id):
        """ Returns the skills for the section section_id of the template """
        return [self.gettext(language, skill) for skill in
                self._template_content.get("structure_skills", {}).get(section_id, [])]

    def get_description(self, language):
        """Returns the course description """
        description = self.gettext(language, self._description) if self._description else ''
        return ParsableText(description, "rst", translation=self.get_translation_obj(language))
