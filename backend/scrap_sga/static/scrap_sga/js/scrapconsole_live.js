// Rafraîchit automatiquement le log/resultat et le statut toutes les 2s
(function() {
    function refreshScrapConsole() {
        var resultField = document.querySelector('[data-scrap-id]');
        if (!resultField) return;
        var scrapId = resultField.getAttribute('data-scrap-id');
        var url = window.location.pathname;
        // Appel AJAX sur la page courante (change form)
        fetch(url, {headers: {'X-Requested-With': 'XMLHttpRequest'}})
            .then(resp => resp.text())
            .then(html => {
                // Parse le HTML retourné et met à jour le champ log/result et le statut
                var parser = new DOMParser();
                var doc = parser.parseFromString(html, 'text/html');
                var newResult = doc.querySelector('[data-scrap-id]');
                if (newResult) {
                    resultField.value = newResult.value;
                }
                // Statut
                var statusField = document.getElementById('id_status');
                var newStatus = doc.getElementById('id_status');
                if (statusField && newStatus) {
                    statusField.value = newStatus.value;
                }
            });
    }
    setInterval(refreshScrapConsole, 2000);
})();
