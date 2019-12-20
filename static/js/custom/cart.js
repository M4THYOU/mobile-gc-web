$(function() {

    let csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

    const defaultQuantity = 1;

    // Quantity ////////////////
    $('.items-count').on('click', function () {
        let isIncrease = $(this).hasClass('increase');

        let field = $(this).siblings('.qty')[0];
        incOrDec(field, isIncrease);
    });

    $('.qty').on('input', function () {
        console.log('changed');
    });

    // increment should be a Bool. If true, increment the value. Else, decrement it.
    // field is the jquery text field that should be incremented or decremented.
    function incOrDec(field, increment) {

        if( isNaN( field.value ) || field.value <= 0 || (parseInt(field.value, 10) == 1 && !increment) ) {
            field.value = defaultQuantity;
        } else {
            if (increment) {
                field.value++;
            } else {
                field.value--;
            }
        }

        let quantity = $(field).val();
        let value = $(field).parent().parent().parent().find('.card-val').val();
        let totalRowCost = $(field).parent().parent().parent().find('.total-cost');
        updateTotals(quantity, value, totalRowCost);

    }

    // Value ////////////////

    $('.card-val').on('input', function () {

        if ( isNaN($(this).val()) ) {
            $(this).val(25.00);
        }

        let quantity = $(this).parent().parent().find('.qty').val();
        let value = $(this).val();
        let totalRowCost = $(this).parent().parent().find('.total-cost');

        updateTotals(quantity, value, totalRowCost);

    });

    // Total ////////////////

    function updateTotals(quantity, value, totalCostElement) {

        if ( quantity < 1 ) quantity = 1;
        if ( value < 5 ) value = 5;

        let quantityInt = parseInt(quantity);
        let newTotalCost = quantityInt * value;

        let roundedTotalCost = (Math.round(newTotalCost*Math.pow(10,2))/Math.pow(10,2)).toFixed(2);
        let formattedTotalCost = roundedTotalCost.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");

        totalCostElement.text(formattedTotalCost);
        updateSubTotal();

    }

    // Subtotal ////////////////

    function updateSubTotal() {

        let subtotal = 0;
        $('.total-cost').each(function (index) {
            let val = $(this).text();
            let valNum = parseFloat(val);

            subtotal += valNum;
        });

        let roundedSubtotal = (Math.round(subtotal*Math.pow(10,2))/Math.pow(10,2)).toFixed(2);
        let formattedSubtotal = roundedSubtotal.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");

        $('#subtotal').text('$' + formattedSubtotal);

    }

    // Email ////////////////

    $('.receiver-email').on('input', function () {
        let email = $(this).val().trim();
        let isValid = validateEmail(email);

        if (isValid || email === "") {
            $(this).siblings('.email-error').text('');
        } else {
            $(this).siblings('.email-error').text('Invalid email address');
        }

    });

    function validateEmail(email) {
        let re = /\S+@\S+\.\S+/;
        return re.test(email);
    }

    // POST ////////////////

    $('#checkout-button').on('click', function () {

        $('#shop-button').prop('disabled', true);
        $('#checkout-button').prop('disabled', true);

        $('body').prepend('<div class="loader-container"><div class="loader"></div></div>');

        let data = {
            'data': []
        };

        $('#all-cards').children('.card-row').each(function (i) {

            let quantity = $(this).find('.qty').val();
            let value = $(this).find('.card-val').val();

            let email = $(this).find('.receiver-email').val().trim();

            if ( !validateEmail(email) && !(email == "") ) {
                email = '';
            }

            let row = {
                'quantity': quantity,
                'value': value,
                'receiver_email': email
            };

            data['data'].push(row);

        });

        let jsonCleanedData = JSON.stringify(data);
        ajaxUpdateCart(jsonCleanedData);
    });

    function ajaxUpdateCart(data) {

        console.log(data);

        $.ajax({
            url: "/account/ajax/update-cart/",
            type: "POST",
            data: data,
            timeout: 15000,
            success: function (data) {
                window.location.replace('http://' + window.location.host + '/checkout/')
            },
            error: function (xhr, textStatus, errorThrown) {
                console.log(textStatus, errorThrown);
                $('.loader-container').remove()
            },
            beforeSend: function (xhr, settings) {
                if (!this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrfToken);
                }
            }
        })

    }

    // Remove Card ////////////////
    $('.remove-card').on('click', function () {
        console.log($(this));
    });

    // Initial Start ////////////////

    function init() {

        $('#all-cards').children('.card-row').each(function (i) {

            let quantity = $(this).find('.qty').val();
            let value = $(this).find('.card-val').val();
            let totalRowCost = $(this).find('.total-cost');

            updateTotals(quantity, value, totalRowCost);

        });

    }

    init();

});