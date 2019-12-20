$(function() {

    let isLoginMode = true;

    $('#switch-mode-button').on('click', function () {
        isLoginMode = !isLoginMode;

        if (isLoginMode) {
            $(this).text('Create an account');
            $('#other-option-text').text('New to Qwaked?');

            $('#form-title').text('Log in to enter');
            $('#form-submit-button').text('Log in');

            $('#first-name-container').remove();
            $('#last-name-container').remove();
        } else {
            $(this).text('Sign in');
            $('#other-option-text').text('Already a Member?');

            $('#form-title').text('Create an account');
            $('#form-submit-button').text('Register');

            $('#login-form').prepend(
                '<div class="col-md-12 form-group" id="first-name-container">' +
                    '<input type="text" class="form-control" id="id_first_name" name="first_name" placeholder="First Name" maxlength="200" onfocus="this.placeholder = \'\'" onblur="this.placeholder = \'First Name\'" required>' +
                '</div>' +
                '<div class="col-md-12 form-group" id="last-name-container">' +
                    '<input type="text" class="form-control" id="id_last_name" name="last_name" placeholder="Last Name" maxlength="200" onfocus="this.placeholder = \'\'" onblur="this.placeholder = \'Last Name\'" required>' +
                '</div>'
            );

        }

    })

})