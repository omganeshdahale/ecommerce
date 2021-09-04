$(document).ready(function(){
    const formsetForms = $(".formset-form");
    const container = $("#formset-container");
    const addButton = $("#btn-add-form");
    const totalForms = $("#id_form-TOTAL_FORMS");

    const formRegex = RegExp('form-\\d+-','g');
    let formIndex = formsetForms.length-1;
    addButton.click(addForm);

    function addForm(e){
        const newForm = formsetForms[0].cloneNode(true);
        formIndex++;
        newForm.innerHTML = newForm.innerHTML.replace(formRegex, `form-${formIndex}-`);
        container.append(newForm);
        
        totalForms.attr('value', `${formIndex+1}`);
    }
});