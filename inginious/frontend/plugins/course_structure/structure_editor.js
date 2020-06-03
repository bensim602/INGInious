//
// This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
// more information about the licensing of this file.
//

//
// [Source code integration]: move file to inginious.frontend.static.js
//

var dragged_from;
var draggable_sections = {};
var draggable_tasks = {};
var task_renamed = {};
var timeouts = [],  lastenter;
var warn_before_exit = false;

/*****************************
 *     Renaming Elements     *
 *****************************/
function rename_section(element, new_section = false) {
    endswith = function(element, value) {
        if(new_section) {
            var section = $(element).closest(".section").attr("id","section_"+string_to_id(value));

            draggable_sections[section[0].id] = make_sections_list_sortable(section);
            draggable_tasks[section[0].id] = make_tasks_list_sortable(section);
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
    handle = $(element).closest(".handle").removeClass("handle");
    element.hide();

    input = $("<input>").attr({value: element.text().trim(), class: "form-control"}).insertBefore(element);
    input.focus().select();

    quit = function () {
        element.text(input.val()).show();
        input.remove();
        handle.addClass("handle");
        endswith(element, input.val());
        warn_before_exit = true;
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
    warn_before_exit = true;
    section.attr("data-level", level + 1);

    content_modified(parent);
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
        warn_before_exit = true;
        content.append($("#task_" + selected_tasks[i] + "_clone").clone().attr("id", 'task_' + selected_tasks[i]));
    }

    content_modified(section);
}

/*********************
 *  Delete elements  *
 *********************/
function delete_section(button) {
    const section = $("#" + button.getAttribute('data-target'));
    const parent = section.parent().closest(".sections_list");
    section.remove();
    warn_before_exit = true;
    content_modified(parent);
}

function delete_task(button) {
    button.mouseleave().focusout();

    const parent = button.closest(".tasks_list");
    button.closest(".task").remove();
    warn_before_exit = true;
    content_modified(parent);
}

/*******************************
 *  Adapt structure to change  *
 *******************************/
function adapt_size(element) {
    const level = Number($(element).parent().closest(".sections_list").attr("data-level")) + 1;
    $(element).attr("data-level", level);

    const title = $(element).children(".section_header").find(".title");
    if (/h\d/.test(title.attr("class"))) {
        title.attr("class", "title h" + level + " mr-3")
    }

    $(element).children(".content").children(".section").each(function () {
        adapt_size(this, level + 1)
    });
}

function content_modified(section) {
    if(section.hasClass("sections_list") && section.hasClass("tasks_list")){
        if(section.children(".content").children(".section").length){
            empty_to_subsections(section);
            draggable_tasks[section[0].id].option("disabled", true);
        }
        if(section.children(".content").children(".task").length){
            empty_to_tasks(section);
            draggable_sections[section[0].id].option("disabled", true);
        }
    } else if (section.hasClass("section") && section.children(".content").children().length === 0){
        if(section.hasClass("sections_list")) {
            draggable_tasks[section[0].id] = make_tasks_list_sortable(section);
        }
        if(section.hasClass("tasks_list")) {
            draggable_sections[section[0].id] = make_sections_list_sortable(section);
        }
        section_to_empty(section);
    }
}

function section_to_empty(section) {
    section.addClass("sections_list tasks_list card");
    const header = section.children(".section_header").removeClass("divided").addClass("card-header");
    header.children(".title").attr("class", "title");
    header.children(".divider").hide();

    const text_placeholder = $("#empty_section").find(".section_placeholder").html().trim();
    const para = $("<p>").attr("class", "section_placeholder text-center align-middle m-2").html(text_placeholder);
    section.children(".content").removeClass("ml-4").addClass("list-group list-group-flush").append(para);
}

function empty_to_subsections(section) {
    const  level = Number($(section).attr("data-level"));

    section.removeClass("tasks_list card");
    const section_header = section.children(".section_header").removeClass("card-header").addClass("divided");
    section_header.children(".title").attr("class", "title h" + level + " mr-3");
    section_header.children(".divider").show();

    section.children(".content").removeClass("list-group list-group-flush").addClass("ml-4").children(".section_placeholder").remove();
}

function empty_to_tasks(section) {
    section.removeClass("sections_list");
    section.find(".section_placeholder").remove();
}


/****************************
 *  Drag and drop elements  *
 ****************************/
$(function () {
    $(".tasks_list").each(function(){
        draggable_tasks[this.id] = make_tasks_list_sortable($(this));
    });

    $(".sections_list").each(function(){
        draggable_sections[this.id] = make_sections_list_sortable($(this));
    });
});

function make_tasks_list_sortable(element) {
    return new Sortable(element.children(".content")[0], {
        group: 'tasks_list',
        animation: 150,
        fallbackOnBody: false,
        swapThreshold: 0.1,
        dragoverBubble: true,
        handle: ".handle",
        onStart: function (evt) {
            dragged_from = evt.from;

            // open sections when exo hover it for more than 0.7s
            $('.tasks_list').children('.section_header').on({
                dragenter: function(event){
                    const list = $(this).closest(".section").children('.content');
                    lastenter = event.target;
                    timeouts.push(setTimeout(function(){
                        list.slideDown('fast');
                    }, 700));

                },
                dragleave: function(event){
                    // dragleave is fired when hover child
                    if(event.target == lastenter) {
                        for (var i=0; i<timeouts.length; i++) {
                          clearTimeout(timeouts[i]);
                        }
                    }
                }});
        },
        onChange: function (evt) {
            content_modified($(dragged_from).closest(".section"));
            content_modified($(evt.to).closest(".section"));

            $('.tasks_list').children('.content').each(function(){
                if(this != evt.to ){
                    $(this).slideUp('fast');
                }
            });

            dragged_from = evt.to;
        },
        onEnd: function (evt) {
            $('.tasks_list').children('.content').slideDown('fast');
            $('.tasks_list').children('.section_header').off('dragenter').off('dragleave');
            warn_before_exit = true;
            evt.to.parentElement.scrollIntoView();
        },
    });
}

function make_sections_list_sortable(element) {
    return new Sortable(element.children(".content")[0], {
        group: 'sections_list',
        animation: 150,
        fallbackOnBody: false,
        swapThreshold: 0.1,
        dragoverBubble: true,
        handle: ".handle",
        onStart: function (evt) {
            $(evt.item).children('.content').slideUp('fast');
            $('.tasks_list').children('.content').slideUp('fast');
            dragged_from = evt.from;
        },
        onEnd: function (evt) {
            $(evt.item).children('.content').slideDown('fast');
            $('.tasks_list').children('.content').slideDown('fast');
            warn_before_exit = true;
            evt.item.scrollIntoView();
        },
        onChange: function (evt) {
            adapt_size(evt.item);
            content_modified($(dragged_from).closest(".section"));
            content_modified($(evt.to).closest(".section"));

            dragged_from = evt.to;
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
    warn_before_exit = false;
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


/************************
 *   Warn before exit   *
 ************************/
$(window).bind('beforeunload', function(){
    if(warn_before_exit){
        return 'All change will be lost! Are you sure you want to leave?';
    } else {
        return undefined;
    }
});