$(document).ready(function () {
  // Razširitev jQuery za containsi, ki je neobčutljiv na velike/male črke
  $.extend($.expr[':'], {
    'containsi': function (elem, i, match, array) {
      return (elem.textContent || elem.innerText || '').toLowerCase().indexOf((match[3] || "").toLowerCase()) >= 0;
    }
  });

  // Funkcija za filtriranje tabele
  function filterTable(searchTerm) {
    var searchSplit = searchTerm.replace(/ /g, "'):containsi('");
    $('.searchtbl tbody tr').each(function () {
      var $this = $(this);
      if ($this.is(":containsi('" + searchSplit + "')")) {
        $this.attr('visible', 'true').show();
      } else {
        $this.attr('visible', 'false').hide();
      }
    });
  }

  // Dodajanje zakasnitve iskanja za boljšo učinkovitost
  var searchTimeout;
  $('.search').keyup(function () {
    clearTimeout(searchTimeout);
    var searchTerm = $(this).val();
    searchTimeout = setTimeout(function () {
      filterTable(searchTerm);
    }, 300); // zakasnitev 300 ms
  });
});
