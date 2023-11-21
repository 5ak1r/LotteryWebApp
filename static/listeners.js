// checkbox implementation to show or hide password when logging in
window.addEventListener('load', function() {
    var current_password = document.getElementById('password');
    var show_password = document.getElementById('check');

    show_password.addEventListener('change', function() {
        // if checkbox is ticked/selected
        if(this.checked) {
            current_password.type = 'text';
        } else {
            current_password.type = 'password';
        }
    });
});