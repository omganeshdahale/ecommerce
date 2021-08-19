$(document).ready(function(){
    const img = $('#product-image');
    const page_item = $('.js-image-pagination .page-item');

    page_item.click(function(){
        img.attr('src', $(this).attr('data-src'));
        page_item.removeClass('active');
        $(this).addClass('active');
        return false;
    });
});