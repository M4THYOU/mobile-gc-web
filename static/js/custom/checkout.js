const stripe = Stripe('pk_test_E2dbCPnsiUsGJeqSbMK0g87a00VnGjd2bV');
const elements = stripe.elements();

$(function() {

    let csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

    const style = {
        base: {
            iconColor: '#666ee8',
            color: '#31325f',
            fontWeight: 400,
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif',
            fontSmoothing: 'antialiased',
            fontSize: '15px',
            '::placeholder': {
                color: '#aab7c4'
            },
            ':-webkit-autofill': {
                color: '#666ee8'
            },
        },
    };

    const card = elements.create('card', {style});

    card.mount('#card-element');
    
    card.on('change', function (error) {
        const cardErrors = document.getElementById('card-errors');

        if (error) {
            cardErrors.textContent = error.message;
            cardErrors.classList.add('visible');
        } else {
            cardErrors.classList.remove('visible');
        }

    });

    $('#pay-button').on('click', function () {

        if (validPaymentForm()) {

            toggleLoader(true);

            let paymentIntent = $('#pay-button').data('secret');
            let clientSecret = paymentIntent['client_secret'];

            let firstName = $('#first').val().trim();
            let lastName = $('#last').val().trim();
            let name = firstName + ' ' + lastName;

            let email = $('#email').val().trim();

            stripe.handleCardPayment(
                clientSecret,
                card,

                {
                    payment_method_data: {
                        billing_details: {
                            name: name,
                            email: email
                        }
                    },
                    receipt_email: email
                }

            ).then(function (result) {

                if (result.error) {
                    // Show error, remove loading indicator.
                    toggleLoader(false);
                    $('#errors').text(result.error.message);
                } else {
                    $('#errors').text('');

                    let intentObj = result['paymentIntent'];
                    let jsonCleanedData = JSON.stringify(intentObj);

                    ajaxSendPaymentIntent(jsonCleanedData);

                }

            })

        } else {
            console.log('INVALID FORM');
        }

    });

    function ajaxSendPaymentIntent(data) {
        /*
        * With the current implementation, we do not need charge data on the backend. Thus, we can use a GET ajax request
        * since we do not need to send the backend the pi_id.
        *
        * However, in the case that this may change, we are keeping data as a parameter to make the switch to a POST
        * trivial.
        * */

        $.ajax({
            url: "/account/ajax/make-payment/",
            type: "GET", // Don't actually need to send the pi, so just use get instead.
            //data: data,
            timeout: 15000,
            success: function (data) {
                window.location.replace('http://' + window.location.host + data);
            },
            error: function (xhr, textStatus, errorThrown) {
                $('.loader-container').remove();
                $('#errors').text(errorThrown);
            },
            beforeSend: function (xhr, settings) {
                if (!this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrfToken);
                }
            }
        })

    }

    ///////////// STUFF /////////////////////////////////////////////////////////////////////////////////////

    function validateEmail(email) {
        let re = /\S+@\S+\.\S+/;
        return re.test(email);
    }
    
    function validPaymentForm() {

        // Just make sure all the stuff isn't empty.
        // Literally all of the form fields are for show. Makes the user feel confident in the platform.
        let $first = $('#first');
        let $last = $('#last');
        let $email = $('#email');
        let $country = $('#country');
        let $termsCheck = $('#f-option4');

        let firstName = $first.val().trim();
        let lastName = $last.val().trim();
        let email = $email.val().trim();
        let country = $country.val().trim();
        let termsChecked = $termsCheck.is(':checked');

        let valid = true;
        if (!firstName.length) {
            valid = false;
            $first.css('border-color', 'red');
        } else {
            $first.css('border-color', '#eeeeee');
        }

        if (!lastName.length) {
            valid = false;
            $last.css('border-color', 'red');
        } else {
            $last.css('border-color', '#eeeeee');
        }

        if (!email.length || !validateEmail(email)) {
            valid = false;
            $email.css('border-color', 'red');
        } else {
            $email.css('border-color', '#eeeeee');
        }

        if (!country.length) {
            valid = false;
            $country.css('border-color', 'red');
        } else {
            $country.css('border-color', '#eeeeee');
        }

        if (!termsChecked) {
            valid = false;
            $('#checkbox-container').css('border', 'red solid 1px');
        } else {
            $('#checkbox-container').css('border', '');
        }

        return valid;

    }

    function toggleLoader(shouldShow) {

        if (shouldShow) {
            $('body').prepend('<div class="loader-container"><div class="loader"></div></div>');
        } else {
            $('.loader-container').remove();
        }

    }

});