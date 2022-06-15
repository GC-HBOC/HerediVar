$(document).ready(function(){
    $("input").focus(function(){
        $(this).parent().removeClass("was-validated");
    });
    $("input").blur(function(){
        if ($(this).attr('type') !== 'checkbox'){ // do not show validation colors for checkboxes as they should be fine no matter what you tick!
            $(this).parent().addClass("was-validated");
            $(".form-control:valid").parent().removeClass("was-validated");
        }
    });
  });