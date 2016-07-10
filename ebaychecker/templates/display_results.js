function loadDoc() {


    $('.search_by_title').each(function () {
        
        var ids_to_reload = {};
        id = $(this).parent().parent().prop('id');
        qty_id = '#qty_'.concat(id);
        original_qty_id = '#original_qty_'.concat(id);
        price_id = '#price_'.concat(id);
        var title_id = '#title_'.concat(id);
        
        if ($(this).hasClass('pressed')) {
            
            
            ids_to_reload[id] = {'title': $(title_id).val(), 'searchType': 'findAvailableItemsByTitle'};
        }
    });


    $.ajax({
        url: "{{ url_for('resubmit') }}",
        data: $('#reload_data').serialize(),
        type: 'POST',
        success: function (response) {
            console.log(response);
        },
        error: function (error) {
            console.log(error);
        }
    });
}
