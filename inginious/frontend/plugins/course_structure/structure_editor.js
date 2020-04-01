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
function rename_section(element, new_section = false) {
    endswith = function(element, value) {
        if(new_section) {
            $(element).closest(".section").attr("id","section_"+string_to_id(value));
        }
    };

    rename(element, endswith);
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

/**************************
 *  Create a new section  *
 **************************/
function create_section(parent) {
    const level = Number(parent.attr("data-level"));

    const section = $("#empty_section").clone().show().appendTo(parent.children(".content"));
    section.attr("data-level", level + 1);

    rename_section(section.find(".title"), true);
}

/*****************************
 *  Adding task to sections  *
 *****************************/
function open_task_modal(target) {
    $('#submit_new_tasks').attr('data-target', target.closest('.section').id);

    var placed_task = [];
    $('.task').each(function () {
        placed_task.push(this.id.to_taskid());
    });

    $("#modal_task_list .modal_task").filter(function () {
        // remove task already placed in the structure
        const is_placed = placed_task.includes($(this).children("input").val());
        $(this).toggle(!is_placed);
        $(this).toggleClass("disable", is_placed);

        // reset the selection
        $(this).children("input").attr("checked", false);
        $(this).removeClass("bg-primary text-white");
    });
    $("#searchTask").val("")
}

function search_task(search_field) {
    var value = $(search_field).val().toLowerCase();
    $("#modal_task_list .modal_task").filter(function () {
        const match_search = $(this).children(".task_name").text().toLowerCase().indexOf(value) > -1;
        const is_unplaced = !$(this).hasClass("disable");
        $(this).toggle(match_search && is_unplaced);
    });
}

function click_modal_task(task) {
    $(task).toggleClass("bg-primary text-white");
    const input = $(task).find("input");
    input.attr("checked", !input.attr("checked"));
}

function add_tasks_to_section(button) {
    var selected_tasks = [];
    $.each($("input[name='task']:checked"), function () {
        selected_tasks.push($(this).val());
    });

    const section = $("#" + $(button).attr('data-target'));
    const content = section.children(".content");

    for (var i = 0; i < selected_tasks.length; i++) {
        content.append($("#task_" + selected_tasks[i] + "_clone").clone().attr("id", 'task_' + selected_tasks[i]));
    }
}

/*********************
 *  Delete elements  *
 *********************/
function delete_section(button) {
    const section = $("#" + button.getAttribute('data-target'));

    section.parent().closest(".sections_list");
    section.remove();
}

function delete_task(button) {
    button.mouseleave().focusout();

    button.closest(".tasks_list");
    button.closest(".task").remove();
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
function string_to_id(string) {
    var ID = string.toLowerCase().replace(/\s/g, '_');
    ID = ID.replace(/\W/g, '');
    ID = ID.replace(/_+/g, '_');

    if ($("#section_" + ID).length) {
        for (i = 1; $("#section_" + ID + "_" + i).length; i++) {
        }
        ID = ID + "_" + i;
    }
    return ID ;
}

String.prototype.to_taskid = function () {
    return this.slice(5);
};
String.prototype.to_section_id = function () {
    return this.slice(8);
};