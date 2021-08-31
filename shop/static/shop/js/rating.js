$(document).ready(function(){
    const ratingInput = $('#id_rating');
    const stars = $('.js-star');

    stars.click(function(){
        const value = $(this).attr('data-value');
        ratingInput.val(value);

        stars.each(function(){
            if ($(this).attr('data-value') <= value){
                $(this).addClass('text-warning');
            }
            else {
                $(this).removeClass('text-warning');
            }
        });
    });

    $(`.js-star[data-value=${ratingInput.val()}]`).click();
});