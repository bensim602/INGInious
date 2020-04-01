//
// This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
// more information about the licensing of this file.
//

//
// [Source code integration]: move file to inginious.frontend.static.js
//

var task_renamed = {};

/*****************************
 *     Renaming Elements     *
 *****************************/
function rename_section(element) {
    rename(element, function(element, value) {});
}

function rename_task(element) {
    endswith = function(element, value) {
        task_renamed[element.closest(".task").attr('id').to_taskid()] = value;
    };

    rename(element, endswith);
}

function rename(element, endswith) {
    element.hide();

    input = $("<input>").attr({value: element.text().trim(), class: "form-control"}).insertBefore(element);
    input.focus().select();

    quit = function () {
        element.text(input.val()).show();
        input.remove();
        endswith(element, input.val());
    };

    input.focusout(quit);
    input.keyup(function (e) {
        if (e.keyCode === 13) {
            quit();
        }
    });
}

/**********************
 *  Submit structure  *
 **********************/
function get_sections_list(element) {
    return element.children(".section").map(function (index) {
        const structure = {
            "id": this.id.to_section_id(), "rank": index,
            "title": $(this).find(".title").first().text().trim(),
        };

        const content = $(this).children(".content");
        if ($(this).hasClass("tasks_list")) {
            structure["tasks_list"] = get_tasks_list(content);
        } else if ($(this).hasClass("sections_list")) {
            structure["sections_list"] = get_sections_list(content);
        }
        return structure;
    }).get();
}

function get_tasks_list(element) {
    const tasks_list = {};
    element.children(".task").each(function (index) {
        tasks_list[this.id.to_taskid()] = index;
    });
    return tasks_list;
}

function submit() {
    const structure_json = JSON.stringify(get_sections_list($('#course_structure').children(".content")));
    const task_renamed_json = JSON.stringify(task_renamed);
    $("<form>").attr("method", "post").appendTo($("#course_structure")).hide()
        .append($("<input>").attr("name", "course_structure").val(structure_json))
        .append($("<input>").attr("name", "task_renamed").val(task_renamed_json)).submit();

}

/************************
 *  String manipulation  *
 ************************/

String.prototype.to_taskid = function () {
    return this.slice(5);
};
String.prototype.to_section_id = function () {
    return this.slice(8);
};