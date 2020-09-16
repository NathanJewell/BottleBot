function setstats(stats) {
        time_hms = new Date(stats.operating_time * 1000).toISOString().substr(11, 8)
        $("#status-content").html(stats.status);
        $("#filled-content").html(stats.cans_filled);
        $("#runtime-content").html(time_hms);
}

function getstats(cb) {
    $.get("stats", setstats)
}

function postStatus(status) {
        data = {'status' : status};
        $.ajax({
            type : "POST",
            url : "status",
            data: JSON.stringify(data),
            contentType : "application/json; charset=utf-8",
            dataType : "json",
            success : setstats
        });
}

$(document).ready(() => {

    setInterval(() => {getstats(setstats)}, 1000)
    $("#start-canning").on('click', () => {
        postStatus('canning')
    });

    $("#stop-canning").on('click', () => {
        postStatus('ready')
    });

    $("#clean-canning").on('click', () => {
        postStatus('cleaning')
    });

})
