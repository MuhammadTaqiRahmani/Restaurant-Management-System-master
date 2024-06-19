function searchTable() {
    var input, filter, table, tr;
    input = document.getElementById("searchInput");
    filter = input.value.toUpperCase();
    table = document.querySelector(".table");
    tr = table.getElementsByTagName("tr");
  
    for (let i = 0; i < tr.length; i++) {
      let txtValue = Array.from(tr[i].getElementsByTagName("td"))
                          .map(td => td.textContent || td.innerText)
                          .join(' ');
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
        tr[i].classList.add("highlight");
      } else {
        tr[i].style.display = "none";
        tr[i].classList.remove("highlight");
      }
    }
  }