(function() {
    function startWhenReady() {
        if (typeof window.django !== "undefined" && typeof window.django.jQuery === "function") {
            window.django.jQuery(function($) {
                function updateEcart($row) {
                    // Ne traite que les lignes qui ont bien un champ mt_vers_virt
                    var $mt_vers_virt = $row.find('input[name$="-mt_vers_virt"]');
                    if ($mt_vers_virt.length === 0) {
                        console.debug('[updateEcart] Pas de champ mt_vers_virt trouvé dans la ligne');
                        return;
                    }
                    
                    // Récupère la valeur mt_bl depuis le <p> dans la cellule .field-mt_bl
                    // OU depuis l'input caché si disponible (plus fiable)
                    var mt_bl = 0;
                    var $inputMtBl = $row.find('input[name$="-mt_bl"]');
                    if ($inputMtBl.length) {
                        mt_bl = parseFloat($inputMtBl.val().replace(',', '.')) || 0;
                    } else {
                        var mt_bl_text = $row.find('td.field-mt_bl p').text();
                        mt_bl = parseFloat(mt_bl_text.replace(',', '.')) || 0;
                    }

                    var mt_vers_virt = parseFloat($mt_vers_virt.val().replace(',', '.')) || 0;

                    var ecart = mt_vers_virt - mt_bl;
                    var $ecartDisplay = $row.find('.js-ecart-dyn');
                    var color = ecart < 0 ? 'red' : (ecart > 0 ? 'green' : 'black');
                    
                    if ($ecartDisplay.length === 0) {
                        console.debug('[updateEcart] Pas de .js-ecart-dyn trouvé dans la ligne');
                    } else {
                        $ecartDisplay.text(ecart.toFixed(2)).css('color', color);
                        
                        // Mise à jour du champ ecart caché (pour la sauvegarde)
                        var $inputEcart = $row.find('input[name$="-ecart"]');
                        if ($inputEcart.length) {
                            $inputEcart.val(ecart.toFixed(2));
                        }
                    }
                    
                    // Debug visuel
                    console.debug('[updateEcart] mt_bl=' + mt_bl + ', mt_vers_virt=' + mt_vers_virt + ', ecart=' + ecart);
                }

                function updateMtBlAndEcart($row) {
                    // Récupère les quantités
                    var qte3 = parseFloat($row.find('input[name$="-qte_bd_3kg"]').val() || '0');
                    var qte6 = parseFloat($row.find('input[name$="-qte_bd_6kg"]').val() || '0');
                    var qte12 = parseFloat($row.find('input[name$="-qte_bd_12kg"]').val() || '0');

                    // Récupère les prix depuis les champs de prix (priorité) OU depuis les data-attributes
                    var prix3 = 0, prix6 = 0, prix12 = 0;
                    
                    // Essaie d'abord de lire depuis les champs de prix (s'ils sont présents)
                    var $prix3Input = $row.find('input[name$="-prix_3kg"]');
                    var $prix6Input = $row.find('input[name$="-prix_6kg"]');
                    var $prix12Input = $row.find('input[name$="-prix_12kg"]');
                    
                    if ($prix3Input.length) {
                        prix3 = parseFloat($prix3Input.val().replace(',', '.')) || 0;
                    } else {
                        prix3 = parseFloat($row.attr('data-prix-3kg') || '0');
                    }
                    
                    if ($prix6Input.length) {
                        prix6 = parseFloat($prix6Input.val().replace(',', '.')) || 0;
                    } else {
                        prix6 = parseFloat($row.attr('data-prix-6kg') || '0');
                    }
                    
                    if ($prix12Input.length) {
                        prix12 = parseFloat($prix12Input.val().replace(',', '.')) || 0;
                    } else {
                        prix12 = parseFloat($row.attr('data-prix-12kg') || '0');
                    }

                    // Calcule le nouveau montant BL
                    var mt_bl = (qte3 * prix3) + (qte6 * prix6) + (qte12 * prix12);
                    
                    // Met à jour la cellule mt_bl (affichage)
                    var $mtBlCell = $row.find('td.field-mt_bl');
                    if ($mtBlCell.find('p').length) {
                        $mtBlCell.find('p').text(mt_bl.toFixed(2));
                    } else if ($mtBlCell.length) {
                        // Si pas de <p>, on crée un élément pour l'affichage
                        $mtBlCell.html('<p>' + mt_bl.toFixed(2) + '</p>');
                    }
                    
                    // Met à jour la vraie valeur du champ caché mt_bl (pour la sauvegarde)
                    var $inputMtBl = $row.find('input[name$="-mt_bl"]');
                    if ($inputMtBl.length) {
                        $inputMtBl.val(mt_bl.toFixed(2));
                    }
                    
                    // Calcule aussi le tonnage
                    var tonnage = (qte3 * 3) + (qte6 * 6) + (qte12 * 12);
                    var $tonnageCell = $row.find('td.field-tonnage');
                    var $inputTonnage = $row.find('input[name$="-tonnage"]');
                    
                    if ($tonnageCell.find('p').length) {
                        $tonnageCell.find('p').text(tonnage.toFixed(2));
                    } else if ($tonnageCell.length) {
                        $tonnageCell.html('<p>' + tonnage.toFixed(2) + '</p>');
                    }
                    
                    if ($inputTonnage.length) {
                        $inputTonnage.val(tonnage.toFixed(2));
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
                    
                    // Met à jour l'écart
                    var $mt_vers_virt = $row.find('input[name$="-mt_vers_virt"]');
                    var mt_vers_virt = parseFloat($mt_vers_virt.val().replace(',', '.') || '0');
                    var ecart = mt_vers_virt - mt_bl;
                    var $ecartDisplay = $row.find('.js-ecart-dyn');
                    var color = ecart < 0 ? 'red' : (ecart > 0 ? 'green' : 'black');
                    
                    if ($ecartDisplay.length) {
                        $ecartDisplay.text(ecart.toFixed(2)).css('color', color);
                    }
                    
                    // Met à jour le champ ecart caché (pour la sauvegarde)
                    var $inputEcart = $row.find('input[name$="-ecart"]');
                    if ($inputEcart.length) {
                        $inputEcart.val(ecart.toFixed(2));
                    }
                    
                    // Debug visuel
                    console.debug('[updateMtBlAndEcart] qte3=' + qte3 + ', qte6=' + qte6 + ', qte12=' + qte12);
                    console.debug('[updateMtBlAndEcart] prix3=' + prix3 + ', prix6=' + prix6 + ', prix12=' + prix12);
                    console.debug('[updateMtBlAndEcart] mt_bl=' + mt_bl + ', tonnage=' + tonnage);
                }

                function attachEvents() {
                    // Sélectionne toutes les lignes du formulaire
                    var $rows = $('.dynamic-salamgaztabligne');
                    
                    // Pour chaque ligne
                    $rows.each(function() {
                        var $row = $(this);
                        
                        // Attache les événements aux champs de quantité
                        $row.find('input[name$="-qte_bd_3kg"], input[name$="-qte_bd_6kg"], input[name$="-qte_bd_12kg"]').on('input change', function() {
                            updateMtBlAndEcart($row);
                        });
                        
                        // Attache les événements aux champs de prix
                        $row.find('input[name$="-prix_3kg"], input[name$="-prix_6kg"], input[name$="-prix_12kg"]').on('input change', function() {
                            updateMtBlAndEcart($row);
                        });
                        
                        // Attache les événements au champ mt_vers_virt
                        $row.find('input[name$="-mt_vers_virt"]').on('input change', function() {
                            updateEcart($row);
                        });
                        
                        // Initialise les calculs pour cette ligne
                        updateMtBlAndEcart($row);
                    });
                    
                    // Attache un événement pour les nouvelles lignes ajoutées dynamiquement
                    $(document).on('formset:added', function(event, $row, formsetName) {
                        if (formsetName === 'salamgaztabligne_set') {
                            // Attache les événements à la nouvelle ligne
                            $row.find('input[name$="-qte_bd_3kg"], input[name$="-qte_bd_6kg"], input[name$="-qte_bd_12kg"]').on('input change', function() {
                                updateMtBlAndEcart($row);
                            });
                            
                            $row.find('input[name$="-prix_3kg"], input[name$="-prix_6kg"], input[name$="-prix_12kg"]').on('input change', function() {
                                updateMtBlAndEcart($row);
                            });
                            
                            $row.find('input[name$="-mt_vers_virt"]').on('input change', function() {
                                updateEcart($row);
                            });
                        }
                    });
                }
                
                // Initialise les événements au chargement de la page
                attachEvents();
                
                // Réinitialise les événements après un rechargement AJAX
                $(document).on('formset:added', function() {
                    setTimeout(attachEvents, 100);
                });
                
                console.log('[ecart_live_update] JS chargé et prêt.');
            });
        } else {
            setTimeout(startWhenReady, 50);
        }
    }
    startWhenReady();
})();
