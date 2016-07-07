$(document).ready(function () {

    $('.remove_listing').click(function () {

        $(this).parent().parent().addClass('hidden');
        id = $(this).parent().parent().prop('id');
        qty_id = '#qty_'.concat(id);
        original_qty_id = '#original_qty_'.concat(id);
        price_id = '#price_'.concat(id);
        
        $(qty_id).val(0);
        calculate_total_price();

    });

    $('.reset').click(function () {
        $('tr').filter(function () {
            if ($(this).hasClass('sub_data')) {
                $(this).addClass('hidden');
            }

            if ($(this).hasClass('entries')) {
                $(this).removeClass('hidden');
            }
        });

        $('.remove_listing').each(function () {
            $(this).prop('checked', false);
        });

        calculate_total_price_and_reset_quantities();
    });

    $('.search_method').click(function () {

        if ($(this).hasClass('pressed')) {
            $(this).val('By Part Num');
        }

        else {
            $(this).val('By Title');
        }
        $(this).toggleClass('pressed');
    });

    $('.qty').change(function () {
        calculate_total_price();
    });

    $('.price').change(function () {
        calculate_total_price();
    });

    $('.view_sub_data').click(function () {
        $('.'.concat($(this).prop('id'))).toggleClass('hidden');
    });
    
    label_buttons();
    calculate_total_price();
});

var id, qty_id, original_qty_id, price_id, shipping_id, qty, total_price, total_qty;

function calculate_total_price() {
    console.log('here');
    total_price = 0;
    $('.remove_listing').each(function () {
        id = $(this).parent().parent().prop('id');
        qty_id = '#qty_'.concat(id);
        original_qty_id = '#original_qty_'.concat(id);
        price_id = '#price_'.concat(id);
        shipping_id = '#shipping_'.concat(id);

        if ($(this).parent().parent().hasClass('hidden')) {
            console.log('removing one: ' + id);
            $(qty_id).val(0);
        }

        qty = parseFloat($(qty_id).val());
        var float_price = parseFloat($(price_id).val().replace('$', '').replace(',', ''));
        var shipping_price = parseFloat($(shipping_id).val().replace('$', '').replace(',', ''));
        console.log('string float price:' + $(price_id).val().replace('$', ''));
        console.log('float price:' + float_price);
        var final_price = (float_price + shipping_price) * qty;

        total_price += final_price;
    });

    total_qty = 0;
    $('.qty').each(function () {
        total_qty += parseFloat($(this).val());
    });

    $('#total_price').text('$'.concat(total_price.toFixed(2)));
    $('#total_qty').text(total_qty);
}

function calculate_total_price_and_reset_quantities() {
    total_price = 0;
    $('.remove_listing').each(function () {
        id = $(this).parent().parent().prop('id');
        qty_id = '#qty_'.concat(id);
        original_qty_id = '#original_qty_'.concat(id);
        price_id = '#price_'.concat(id);
        shipping_id = '#shipping_'.concat(id);

        var original_qty = $(original_qty_id).val();
        $(qty_id).val(original_qty);

        qty = parseFloat($(qty_id).val());
        var float_price = parseFloat($(price_id).val().replace('$', '').replace(',', ''));
        var shipping_price = parseFloat($(shipping_id).val().replace('$', '').replace(',', ''));
        var final_price = (float_price + shipping_price) * qty;

        total_price += final_price;
    });

    total_qty = 0;
    $('.qty').each(function () {
        total_qty += parseFloat($(this).val());
    });

    $('#total_price').text('$'.concat(total_price.toFixed(2)));
    $('#total_qty').text(total_qty);
}

function label_buttons() {
    $('.search_method').each(function () {
        if ($(this).hasClass('by_part_num')) {
            $(this).val('By Part Num');
        }
        if ($(this).hasClass('by_title')) {
            $(this).val('By Title');
            $(this).addClass('pressed');
        }
    });
}

function submit_form() {
    var submission_data = {'item_dicts_by_id': {}};
    submission_data['request_url'] = $('#request_url').val();
    console.log('initial sub data: ' + submission_data);

    $('tr.entries').filter(function () {
        var id = $(this).prop('id');
        console.log('our id: ' + id);
        var qty = $('#qty_'.concat(id)).val();
        var price = $('#price_'.concat(id)).val();
        var part_num = $('#part_num_'.concat(id)).text();
        var title = $('#title_'.concat(id)).val();
        var search_method = $('#search_method_'.concat(id));

        var display_selection;
        if (search_method.hasClass('by_part_num') && search_method.hasClass('pressed')) {
            display_selection = ['completed_sale', 'by_title'];
        }
        else if (search_method.hasClass('by_title') && !search_method.hasClass('pressed')) {
            display_selection = ['completed_sale', 'by_part_num'];
        }
        else if (search_method.hasClass('by_part_num')) {
            display_selection = ['completed_sale', 'by_part_num'];
        }
        else {
            display_selection = ['completed_sale', 'by_title'];
        }

        console.log('our other stuff: ' + qty + ' ' + price + ' ' + part_num + ' ' + title + ' ' + search_method);

        submission_data['item_dicts_by_id'][id] = {'parsed_data': {'qty': qty,
                                                                    'partNum': part_num,
                                                                    'title': title},
                                                    'display_selection': display_selection};

    });
    
    $('#submission_data').text(JSON.stringify(submission_data));
    $('#submission_data').val(JSON.stringify(submission_data));
    console.log('our string data: ' + JSON.stringify(submission_data));
    $('#reload_data').submit();
}

