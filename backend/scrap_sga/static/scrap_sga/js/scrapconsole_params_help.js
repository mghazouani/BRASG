// Affichage dynamique de l'aide sur les paramètres selon le type de scrap sélectionné
(function() {
    // Table d'aide JS, doit correspondre au param_help Python
    const paramHelp = {
        'sync_BcLinbc': [
            {arg: 'batch_size', type: 'int', help: 'Taille du batch pour la synchro BC/Ligne BC (défaut: 100)'},
            {arg: 'last', type: 'int', help: 'Limiter aux X derniers BC (et leurs lignes)'},
            {arg: 'name', type: 'str', help: 'Filtrer sur le champ num carnet commande'},
            {arg: 'date', type: 'int', help: 'Limiter aux BC créés/modifiés dans les X dernières heures'},
        ],
        'sync_FounisseursCentres': [],
        'sync_products': [],
        'sync_user': [],
    };
    function getHelpHTML(scrapType) {
        const params = paramHelp[scrapType] || [];
        if (!params.length) return '';
        let html = '<div style="margin-top:8px;color:#666;font-size:90%">';
        html += '<b>Paramètres disponibles pour ce scrap :</b><ul style="margin-bottom:0">';
        params.forEach(p => {
            html += `<li><code>--${p.arg}</code> <span style="color:#888">(${p.type})</span> : ${p.help}</li>`;
        });
        html += '</ul>';
        // Exemple complet pour sync_BcLinbc
        if (scrapType === 'sync_BcLinbc') {
            html += '<div style="margin-top:6px;font-style:italic;color:#888">Exemple params&nbsp;:</div>';
            html += '<pre style="background:#f8f8f8;border:1px solid #eee;padding:5px 8px;">{"batch_size": 100, "last": 50, "name": "529371", "date": 1}</pre>';
        }
        html += '</div>';
        return html;
    }
    function updateHelp() {
        const scrapType = document.getElementById('id_scrap_type').value;
        const helpDiv = document.getElementById('params-dynamic-help');
        helpDiv.innerHTML = getHelpHTML(scrapType);
    }
    document.addEventListener('DOMContentLoaded', function() {
        const paramsField = document.getElementById('id_params');
        if (paramsField) {
            // Ajoute la div d'aide juste après le champ params
            let helpDiv = document.createElement('div');
            helpDiv.id = 'params-dynamic-help';
            paramsField.parentNode.appendChild(helpDiv);
            // Premier affichage
            updateHelp();
            // Rafraîchit à chaque changement de type
            const scrapTypeField = document.getElementById('id_scrap_type');
            if (scrapTypeField) {
                scrapTypeField.addEventListener('change', updateHelp);
            }
        }
    });
})();
