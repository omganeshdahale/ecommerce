$(document).ready(function(){
    $('#id_description').removeAttr('required');

    ClassicEditor
        .create( document.querySelector( '#id_description' ) )
        .catch( error => {
            console.error( error );
        } );
});