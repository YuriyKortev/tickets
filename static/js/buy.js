$('#buy_button').on('click', function () {
    $.post('').done(function (data) {
        console.log(data)
        if (data==='True'){
            $(this).prop('disabled', true);
            $('.result').html('Билеты куплены!!!')
        }else{
            $('.result').html('Хммм, что-то не так :(')
        }
    })
})