function checkDuration() {
   var inputValue = parseInt(document.getElementById('id_how_long').value, 10);

   if(isNaN(inputValue) || inputValue < 1 || inputValue > 5) {
        document.getElementById('id_how_long').style.border = "2px solid #8B0000";
   } else {
        document.getElementById('id_how_long').style.border = "none";
        document.getElementById('id_how_long').style.borderBottom = "2px solid #2b4e32";
   }
}

document.addEventListener("DOMContentLoaded", function() {
    var today = new Date().toISOString().split('T')[0];
    document.getElementById('id_start_date').setAttribute('min', today);

    document.getElementById('id_start_date').addEventListener('change', function () {
        var selectedDate = this.value;
        if (selectedDate < today) {
            this.classList.add('disabled-date');
        } else {
            this.classList.remove('disabled-date');
        }
    });

    var howLongInput = document.getElementById('id_how_long');
    howLongInput.setAttribute('min', '1');
    howLongInput.setAttribute('max', '5');

    howLongInput.addEventListener('blur', function() {
        checkDuration();
    });

});