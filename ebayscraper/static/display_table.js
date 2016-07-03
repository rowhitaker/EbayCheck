$(document).ready(function () {

    function calculate_total_price() {
        var total_price = 0;
        $('.price').each(function () {
            if (!$(this).parent().hasClass('hidden')) {
                var float_price = parseFloat($(this).text().replace('$', ''));
                total_price += float_price;
            }
        });
        $('#total_price').text('$'.concat(total_price.toFixed(2)));
    }

    $('.remove_listing').change(function () {
        if ($(this).prop("checked")) {
            $(this).parent().parent().addClass('hidden');
            calculate_total_price();
        }
    });

    $('#reload').click(function () {
        $('tr').filter(function () {
            $(this).removeClass('hidden');
        });

        $('.remove_listing').each(function () {
            $(this).prop('checked', false);
        });

        calculate_total_price();
    });

    calculate_total_price();
});