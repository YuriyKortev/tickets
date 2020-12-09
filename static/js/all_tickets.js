$(document).on("click",".ticket", function () {

    document.location.href = '/'+$(this).attr('type')+'/buy_ticket?'+'id='+$(this).attr('id')

});