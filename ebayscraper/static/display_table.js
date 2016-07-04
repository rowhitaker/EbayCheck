$(document).ready(function () {

    $('.remove_listing').change(function () {
        if ($(this).prop("checked")) {
            $(this).parent().parent().addClass('hidden');
            calculate_total_price();
        }
    });

    $('#reset').click(function () {
        $('tr').filter(function () {
            $(this).removeClass('hidden');
        });

        $('.remove_listing').each(function () {
            $(this).prop('checked', false);
        });

        calculate_total_price_and_reset_quantities();
    });

    $('.qty').change(function () {
        calculate_total_price();
    });

    calculate_total_price();
});

var id, qty_id, original_id, qty, total_price;

function calculate_total_price() {
    console.log('here');
    total_price = 0;
    $('.price').each(function () {
        id = $(this).prop('id');
        qty_id = '#qty_'.concat(id);
        original_id = '#original_'.concat(id);

        if ($(this).parent().parent().hasClass('hidden')) {
            console.log('removing one: ' + id);
            $(qty_id).val(0);
        }

        qty = parseFloat($(qty_id).val());
        var float_price = parseFloat($(this).val().replace('$', ''));
        var final_price = float_price * qty;

        total_price += final_price;

    });

    $('#total_price').text('$'.concat(total_price.toFixed(2)));

}

function calculate_total_price_and_reset_quantities() {
    total_price = 0;
    $('.price').each(function () {
        id = $(this).prop('id');
        qty_id = '#qty_'.concat(id);
        original_id = '#original_'.concat(id);

        var original_qty = $(original_id).val();
        $(qty_id).val(original_qty);

        qty = parseFloat($(qty_id).val());
        var float_price = parseFloat($(this).val().replace('$', ''));
        var final_price = float_price * qty;

        total_price += final_price;

        $('#total_price').text('$'.concat(total_price.toFixed(2)));

    });
}