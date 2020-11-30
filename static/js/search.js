$(document).on("click",".ticket", function () {
    var params = new URLSearchParams();
    $(this).find('.path li').each(function(i){
        let el =  $(this).attr('ac_id'); // This is your rel value
        params.append('id' ,el)
    });

    document.location.href = '/'+$(this).attr('type')+'/buy_ticket?'+params.toString()

});