$(document).ready(function($){
    $("*[data-href]").on('click', function () {
        window.location = $(this).data("href");
    });
});

