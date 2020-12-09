$(document).ready(function() {
        $('.range_date').on('change',function(e) {
            var url = "/admin/get_range_stats"; // send the form data here.
            let start_date = $('#start_date').val()
            let end_date = $('#end_date').val()
            let dict = {'start_date': start_date, 'end_date': end_date}
            $.ajax({
                type: "get",
                url: url,
                data: dict, // serializes the form's elements.
                success: function (data) {
                    $('#range_stats').attr('src', data) // display the returned data in the console.
                }
            });
        });

        $('#pie_form').submit(function (e) {
            var url = "/admin/get_pie"; // send the form data here.
            $.ajax({
                type: "get",
                url: url,
                data: $(this).serialize(), // serializes the form's elements.
                success: function (data) {
                    if (typeof data !== 'string' && 'data' in data){
                        for (const [key, value] of Object.entries(data['data'])) {
                              value.forEach(function (item) {
                                    $('#'+key+'_errors').append(`<span>[${item}]</span>`)
                              })
                        }
                    }
                    else {
                        console.log('suc')
                        $('#img_seats').attr('src', data)  // display the returned data in the console.
                    }
                }
            });
            e.preventDefault(); // block the traditional submission of the form.
        });

        $('#create_ride').submit(function (e) {
            var url = "/admin/create_ride"; // send the form data here.
            $.ajax({
                type: "post",
                url: url,
                data: $(this).serialize(), // serializes the form's elements.
                success: (data) => {
                    if(data === 'True'){
                        $(this).append('<p> Рейс успешно добавлен!!!!!! </p>')  // display the returned data in the console.
                    }
                    else{
                        for (const [key, value] of Object.entries(data['data'])) {
                              value.forEach(function (item) {
                                    $('#'+key+'_errors').append(`<span>[${item}]</span>`)
                              })
                        }
                    }
                }
            });
            e.preventDefault(); // block the traditional submission of the form.
        });

        $('#create_city').submit(function (e) {
            var url = "/admin/create_city"; // send the form data here.
            $.ajax({
                type: "post",
                url: url,
                data: $(this).serialize(), // serializes the form's elements.
                success: (data) => {
                    if(data === 'True'){
                        $(this).append('<p> Город успешно добавлен!!!!!! </p>')  // display the returned data in the console.
                    }
                    else{
                        for (const [key, value] of Object.entries(data['data'])) {
                              value.forEach(function (item) {
                                    $('#'+key+'_errors').append(`<span>[${item}]</span>`)
                              })
                        }
                    }
                }
            });
            e.preventDefault(); // block the traditional submission of the form.
        });

        $('#create_station').submit(function (e) {
            var url = "/admin/create_station"; // send the form data here.
            $.ajax({
                type: "post",
                url: url,
                data: $(this).serialize(), // serializes the form's elements.
                success: (data) => {
                    if(data === 'True'){
                        $(this).append('<p> Станция успешно добавлена!!!!!! </p>')  // display the returned data in the console.
                    }
                    else{
                        for (const [key, value] of Object.entries(data['data'])) {
                              value.forEach(function (item) {
                                    $('#'+key+'_errors').append(`<span>[${item}]</span>`)
                              })
                        }
                    }
                }
            });
            e.preventDefault(); // block the traditional submission of the form.
        });

        $('#export_button').click(function (e) {
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = '/uploads/db.csv';
            // the filename you want
            a.download = 'db.csv';
            document.body.appendChild(a);
            a.click();
        })

        $('#import_file').change(function () {
            var form_data = new FormData();
            form_data.append('file', $(this).prop('files')[0])

            $.ajax({
                type: "post",
                url: '/import_db',
                data: form_data,
                contentType: false,
                cache: false,
                processData: false,
                success: function(data) {
                    $('.files').append('<p style="font-size: 7px">Импорт успешно совершен!!!</p>')
                },
            });
        })


    });