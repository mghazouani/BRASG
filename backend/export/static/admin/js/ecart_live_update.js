(function() {
    function startWhenReady() {
        if (typeof window.django !== "undefined" && typeof window.django.jQuery === "function") {
            window.django.jQuery(function($) {
                function updateEcart($row) {
                    // Récupère la valeur mt_bl depuis le <p> dans la cellule .field-mt_bl
                    var mt_bl_text = $row.find('td.field-mt_bl p').text();
                    var mt_bl = parseFloat(mt_bl_text.replace(',', '.')) || 0;

                    // Récupère la valeur mt_vers_virt depuis l'input
                    var $mt_vers_virt = $row.find('input[name$="-mt_vers_virt"]');
                    if ($mt_vers_virt.length === 0) {
                        console.warn('[ecart_live_update] Champ mt_vers_virt manquant, calcul ignoré.', $row.get(0));
                        return;
                    }
                    var mt_vers_virt = parseFloat($mt_vers_virt.val().replace(',', '.')) || 0;

                    var ecart = mt_vers_virt - mt_bl;
                    var $ecartDisplay = $row.find('.js-ecart-dyn');
                    var color = ecart < 0 ? 'red' : (ecart > 0 ? 'green' : 'black');
                    if ($ecartDisplay.length === 0) {
                        console.warn('[ecart_live_update] Pas de .js-ecart-dyn trouvé dans la ligne suivante :', $row.get(0));
                    } else {
                        $ecartDisplay.text(ecart.toFixed(2)).css('color', color);
                    }
                }

                function bindEcartListeners() {
                    window.django.jQuery('tr.form-row, .form-row').each(function() {
                        updateEcart(window.django.jQuery(this));
                    });
                    window.django.jQuery(document).on('input', 'input[name$="-mt_vers_virt"]', function() {
                        var $row = window.django.jQuery(this).closest('tr.form-row, .form-row');
                        updateEcart($row);
                    });
                    window.django.jQuery(document).on('formset:added', function(event, $row, formsetName) {
                        updateEcart($row);
                        $row.find('input[name$="-mt_vers_virt"]').on('input', function() {
                            updateEcart($row);
                        });
                    });
                }

                console.log('[ecart_live_update] JS chargé et prêt.');
                bindEcartListeners();
            });
        } else {
            setTimeout(startWhenReady, 50);
        }
    }
    startWhenReady();
})();
