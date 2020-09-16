names = []
currentname = ""
all_stats = {}
base_path = 'http://127.0.0.1:5000/'
$.get("names", (response) => {
    names = response.names;
    currentname = names[0]
    names.forEach(name => {
        $('#select-bar').append( `
            <div class="pure-u-1-6">
                <button id='${name}-selector' class="pure-button button-success name-selector">${name}</button>
            </div>
        `);
    })
})

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

function setpanelstats(stats) {
        time_hms = new Date(stats.operating_time * 1000).toISOString().substr(11, 8)
        $("#status-content").html(stats.status);
        $("#filled-content").html(stats.cans_filled);
        $("#runtime-content").html(time_hms);
}


function getstats() {
    names.forEach(name => {
        $.get(base_path + "stats/" + name,  (stats) => {
            all_stats[name] = stats
            $(`#${name}-selector`).css("background-color", status_colors[stats.status])
        });
    });

}



$(document).ready(() => {

    setInterval(getstats, 1000)
    setInterval(() => {setpanelstats(all_stats[currentname])}, 500);
    setInterval(() => {$("#filler-name").html(currentname)}, 500);
    $("#start-canning").on('click', () => {
        data = { 'status' : 'READY'};
        $.ajax({
            type : "POST",
            url : `${base_path}status/${currentname}`,
            data: JSON.stringify(data),
            contentType : "application/json; charset=utf-8",
            dataType : "json",
            success : (stats) => {
                all_stats[currentname] = stats;
            }
        })
    });

    $("#stop-canning").on('click', () => {
        data = { 'status' : 'OFFLINE'};
        $.ajax({
            type : "POST",
            url : `${base_path}status/${currentname}`,
            data: JSON.stringify(data),
            contentType : "application/json; charset=utf-8",
            dataType : "json",
            success : (stats) => {
                all_stats[currentname] = stats;
            }
        })
    });

    $(".name-selector").on('click', (event) => {
        currentname = $(event.target).text()
        //currentname = currentname
    })


})
