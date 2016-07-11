$(document).ready(function(){
    var size_options = $("#size option");

    $("#size > option").each(function() {
        if (this.value != 3) {
            this.remove();
        }

    });

    $("#rule").on('change', function (e) {
        var valueSelected = this.value;
        $("#size option").remove();
        $("#size").append(size_options);
        $("#size > option").each(function() {
            if (valueSelected == 3) {
                if (this.value != 3) {
                    this.remove();
                }
            } else {
                if (parseInt(this.value) < parseInt(valueSelected)) {
                    console.log(this.value);
                    this.remove();
                }
            }

        });
    });
});
