$(document).ready(function(){
    $('.js-keep-params').click(function(){
        const urlParams = new URLSearchParams(window.location.search);
        const aUrlParams = new URLSearchParams($(this).attr('href'));

        for (const [key, value] of aUrlParams){
            urlParams.set(key, value);
        }

        window.location.search = urlParams;
        return false;
    })
});