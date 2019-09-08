var today = new Date().toISOString().split('T')[0];
document.getElementsByName("ttl")[0].setAttribute('min', today);

$("#admin_counter_submit").submit(function(e){
    var tbl = $('table#slot tbody tr').get().map(function(row) {
        return $(row).find('td').get().map(function(cell) {
          return $(cell).find("input").val();
        });
      });
    $(this).append('<input type="hidden" name="slots" value=\''+ JSON.stringify(tbl) +'\' /> ');
    return true;
})


var counter = 0;

$("#addslot").on("click", function () {
    var newRow = $("<tr>");
    var cols = "";

    cols += '<td><input type="text" class="form-control" required/></td>';
    cols += '<td><input type="time" class="form-control" required/></td>';
    cols += '<td><input type="time" class="form-control" required/></td>';

    cols += '<td><input type="button" class="ibtnDel btn btn-md btn-danger "  value="Delete Slot"></td>';
    newRow.append(cols);
    $("table.order-list").append(newRow);
    counter++;
});



$("table.order-list").on("click", ".ibtnDel", function (event) {
    $(this).closest("tr").remove();       
    counter -= 1
});

$('input[name^="N"]').on("change", function(){
  var N = $("input[name=N]").val();
  var Non = $("input[name=Nonline]").val();
  var Noff = $("input[name=Noffline]").val();
  $('#real_non').val(N * Non / 100);
  $('#real_noff').val(N * Noff / 100);
});