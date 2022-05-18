$(function(){
    $(".toggle-btn").click(function(event) {
        event.preventDefault();
        $(this).closest('.main-div').find('.children').toggle();
        if ($(this).closest('.main-div').find('.children').css('display') === 'none'){
            $(this).text('показать ответы');
        }
        else ($(this).text('скрыть ответы'));
    });
});


