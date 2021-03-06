$(document).ready(function(){
    
    let csrfToken = $('input[name="csrfmiddlewaretoken"]').val();    
    $('.refresh').click(function(){                 
        $(".overlay").css('display', 'block');
        setInterval(function(){                     
            let url = '/database/';
                $.post(url, {csrfmiddlewaretoken: csrfToken}).done(function (json_repsonse){
                    if(json_repsonse){
                        percentage = json_repsonse.count/parseInt(json_repsonse.total_count) * 100
                        $('.loaded').html('Progress: ' + Math.round(percentage * 10) / 10 + '%');                        
                    }else{                        
                        $('.loaded').html('Progress: Unavailable');
                    }                    
                });
          }, 60000); 
    });
});