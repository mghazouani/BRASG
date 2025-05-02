(function() {
    function startWhenReady() {
        if (typeof window.django !== "undefined" && typeof window.django.jQuery === "function") {
            window.django.jQuery(function($) {
                function updateEcart($row) {
                    // Ne traite que les lignes qui ont bien un champ mt_vers_virt
                    var $mt_vers_virt = $row.find('input[name$="-mt_vers_virt"]');
                    if ($mt_vers_virt.length === 0) {
                        // Ne log plus, on ignore silencieusement
                        return;
                    }
                    // Récupère la valeur mt_bl depuis le <p> dans la cellule .field-mt_bl
                    var mt_bl_text = $row.find('td.field-mt_bl p').text();
                    var mt_bl = parseFloat(mt_bl_text.replace(',', '.')) || 0;

                    var mt_vers_virt = parseFloat($mt_vers_virt.val().replace(',', '.')) || 0;

                    var ecart = mt_vers_virt - mt_bl;
                    var $ecartDisplay = $row.find('.js-ecart-dyn');
                    var color = ecart < 0 ? 'red' : (ecart > 0 ? 'green' : 'black');
                    if ($ecartDisplay.length === 0) {
                        // Ne log plus, on ignore silencieusement
                    } else {
                        $ecartDisplay.text(ecart.toFixed(2)).css('color', color);
                    }
                }

                function updateMtBlAndEcart($row) {
                    // Récupère les quantités
                    var qte3 = parseFloat($row.find('input[name$="-qte_bd_3kg"]').val() || '0');
                    var qte6 = parseFloat($row.find('input[name$="-qte_bd_6kg"]').val() || '0');
                    var qte12 = parseFloat($row.find('input[name$="-qte_bd_12kg"]').val() || '0');

                    // Récupère les prix stockés (en data-attribute sur la ligne)
                    var prix3 = parseFloat($row.attr('data-prix-3kg') || '0');
                    var prix6 = parseFloat($row.attr('data-prix-6kg') || '0');
                    var prix12 = parseFloat($row.attr('data-prix-12kg') || '0');

                    // Calcule le nouveau montant BL
                    var mt_bl = (qte3 * prix3) + (qte6 * prix6) + (qte12 * prix12);
                    // Met à jour la cellule mt_bl (affichage)
                    var $mtBlCell = $row.find('td.field-mt_bl');
                    $mtBlCell.find('p').text(mt_bl.toFixed(2));
                    // Met à jour la vraie valeur du champ caché mt_bl (pour la sauvegarde)
                    var $inputMtBl = $row.find('input[name$="-mt_bl"]');
                    if ($inputMtBl.length) {
                        $inputMtBl.val(mt_bl.toFixed(2));
                    }
                    // Ajoute un badge "modifié" à côté de chaque champ quantité modifiée
                    var badgeHtml = '<span class="badge-modified" style="background:#ffc107;color:#222;border-radius:4px;padding:2px 6px;font-size:11px;margin-left:4px;vertical-align:middle;">M</span>';
                    // Pour chaque champ quantité
                    ['qte_bd_3kg','qte_bd_6kg','qte_bd_12kg'].forEach(function(field) {
                        var $input = $row.find('input[name$="-' + field + '"]');
                        if ($input.length && $input.next('.badge-modified').length === 0) {
                            $input.after(badgeHtml);
                        }
                    });
                    // Pour le montant BL (affichage)
                    var $badgeMtBl = $mtBlCell.find('.badge-modified');
                    if ($badgeMtBl.length === 0) {
                        $mtBlCell.append(badgeHtml);
                    }
                    // Les badges restent affichés (pas de timeout)

                    // Met à jour l'écart
                    var $mt_vers_virt = $row.find('input[name$="-mt_vers_virt"]');
                    var mt_vers_virt = parseFloat($mt_vers_virt.val().replace(',', '.') || '0');
                    var ecart = mt_vers_virt - mt_bl;
                    var $ecartDisplay = $row.find('.js-ecart-dyn');
                    var color = ecart < 0 ? 'red' : (ecart > 0 ? 'green' : 'black');
                    $ecartDisplay.text(ecart.toFixed(2)).css('color', color);
                }

                function bindEcartListeners() {
                    window.django.jQuery('tr.form-row, .form-row').each(function() {
                        updateEcart(window.django.jQuery(this));
                    });
                    window.django.jQuery(document).on('input', 'input[name$="-mt_vers_virt"]', function() {
                        var $row = window.django.jQuery(this).closest('tr.form-row, .form-row');
                        updateEcart($row);
                    });
                    // Ajout listeners sur les quantités pour recalcul du montant BL ET de l'écart
                    window.django.jQuery(document).on('input', 'input[name$="-qte_bd_3kg"], input[name$="-qte_bd_6kg"], input[name$="-qte_bd_12kg"]', function() {
                        var $row = window.django.jQuery(this).closest('tr.form-row, .form-row');
                        updateMtBlAndEcart($row);
                        updateEcart($row); // recalcul l'écart aussi, pour être sûr
                    });
                    window.django.jQuery(document).on('formset:added', function(event, $row, formsetName) {
                        if (!$row || !$row.length) {
                            // Essaie de le retrouver à partir de l’event.target
                            $row = window.django.jQuery(event.target).closest('tr.form-row, .form-row');
                        }
                        if ($row && $row.length) {
                            updateEcart($row);
                            $row.find('input[name$="-mt_vers_virt"]').on('input', function() {
                                updateEcart($row);
                            });
                            $row.find('input[name$="-qte_bd_3kg"], input[name$="-qte_bd_6kg"], input[name$="-qte_bd_12kg"]').on('input', function() {
                                updateMtBlAndEcart($row);
                                updateEcart($row);
                            });
                        }
                    });
                }

                // Injection des prix unitaires dans chaque ligne (data-attribute)
                window.django.jQuery('tr.form-row, .form-row').each(function() {
                    var $row = window.django.jQuery(this);
                    var prix3 = $row.find('input[name$="-prix_3kg"]').val() || '0';
                    var prix6 = $row.find('input[name$="-prix_6kg"]').val() || '0';
                    var prix12 = $row.find('input[name$="-prix_12kg"]').val() || '0';
                    $row.attr('data-prix-3kg', prix3);
                    $row.attr('data-prix-6kg', prix6);
                    $row.attr('data-prix-12kg', prix12);
                });

                console.log('[ecart_live_update] JS chargé et prêt.');
                bindEcartListeners();
            });
        } else {
            setTimeout(startWhenReady, 50);
        }
    }
    startWhenReady();
})();
