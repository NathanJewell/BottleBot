names = []
all_stats = {}
base_path = 'http://127.0.0.1:5000/'
grid_elems = []

status_colors = {
    OFFLINE : "red",
    READY : "green",
    PURGING : "orange",
    FILLING : "orange",
    COMPLETE : "green", //TODO make this flashing
    CALIBRATING : "purple",
    CLEANING : "blue", 
    ERROR : "red" //TODO make this flashing and use it

}

function setpanelstats(stats, name) {
        time_hms = new Date(stats.operating_time * 1000).toISOString().substr(11, 8)
        $(`#status-content-${name}`).html(stats.status);
        $(`#filled-content-${name}`).html(stats.cans_filled.toString();
        $(`#runtime-content-${name}`).html(time_hms);
        $(`#message-content-${name}`).html(stats.message_content);
}

function gridheaders() {
    return [ 
        "Name",
        "Current Status",
        "Cans Filled",
        "Runtime",
        "Start",
        "Stop",
        "Clean",
        "Test",
        "Message"
    ]
}

function gridrow(name) {
    return [
        `<p>${name}</p>`,
        `<p id="status-content-${name}" class="${name}-row"></p>`,
        `<p id="filled-content-${name} class="${name}-row""></p>`,
        `<p id="runtime-content-${name}" class="${name}-row"></p>`,
        `<button class="start-canning pure-button button-success ${name}-row" name="${name}">Start</button>`,
        `<button class="stop-canning pure-button button-error ${name}-row" name="${name}">Stop</button>`,
        `<button class="clean-canning pure-button button-secondary ${name}-row" name="${name}">Clean</button>`,
        `<button class="test-canning pure-button button-secondary${name}-row" name="${name}">Test</button>`,
        `<p id="message-content-${name}" class="${name}-row"></p>`
    ]

}


function getstats() {
    var cell_cnt;
    names.forEach(name => {
        $.get(base_path + "stats/" + name,  (stats) => {
            all_stats[name] = stats
            //$(`.${name}-row`).css("background-color", `${status_colors[stats.status]}`)
            setpanelstats(stats, name)
        });
    });

}

function statuspost(status, name) {
    data = {'status' : status} 
    $.ajax({
        type : "POST",
        url : `${base_path}status/${name}`,
        headers : {
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': '*',
            'Access-Control-Allow-Origin' : '*'
        },
        data: JSON.stringify(data),
        contentType : "application/json; charset=utf-8",
        dataType : "json",
        success : (stats) => {
            all_stats[currentname] = stats;
            setpanelstats(stats, name)
        }
    });
}

$.get("names", (response) => {
    names = response.names;
    currentname = names[0]
    var cell_cnt = 0;
    headers = gridheaders()
    $("#data-grid").css('display', 'grid');
    $("#data-grid").css(`grid-template-columns`, `${"auto ".repeat(headers.length)}`);
    $("#data-grid").css(`grid-template-rows`, `${"auto ".repeat(names.length+1)}`);
    headers.forEach(header => {
        $("#data-grid").append(`<div class="header-cell" id="cell-${cell_cnt++}">${header}</div>`)
    });
    names.forEach(name => {
        row = gridrow(name)
        row.forEach(html => {
            $("#data-grid").append(`<div id="cell-${cell_cnt++} class="${name}-row">${html}</div>`)
        })
    });

    for (const x of Array(cell_cnt).keys()) {
        id= `#cell-${x}`
        row = Math.floor(x/headers.length)
        col = x % headers.length
        $(id).css("grid-column-start", `${col + 1}`)
        $(id).css("grid-row-start", `${row + 1}`)
    }
    $(".start-canning").on('click', (event) => {
        statuspost("READY", $(event.target).attr("name"))
    });

    $(".stop-canning").on('click', (event) => {
        statuspost("OFFLINE", $(event.target).attr("name"))
    });
    
    $(".clean-canning").on('click', (event) => {
        statuspost("CLEANING", $(event.target).attr("name"))
    });

    $(".test-canning").on('click', (event) => {
        statuspost("TESTING", $(event.target).attr("name"))
    });
})

const sleep = (ms) => {
    new Promise(resolve => setTimeout(resolve, ms));
}
//sleep(100)

$(document).ready(() => {

    setInterval(getstats, 1000)
})
