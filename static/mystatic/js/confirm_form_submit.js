$(document).ready(function(){
    $('.js-confirm-form-submit').submit(function(){
        return confirm($(this).attr('data-confirm-msg'));
    });
});