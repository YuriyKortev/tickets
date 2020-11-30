

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
                    $('#range_stats').attr('src', 'data:image/png;base64,'+ data) // display the returned data in the console.
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
                    $('#img_seats').attr('src', 'data:image/png;base64,'+ data)  // display the returned data in the console.
                }
            });
            e.preventDefault(); // block the traditional submission of the form.
        });
    });