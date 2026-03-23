
// Hämta data från vårt API
fetch('http://localhost:8000/api/rooms')
    .then(function(svar) {
        // Konvertera svaret till JSON-format
        return svar.json();
    })
    .then(function(rum) {
        // rum = array med alla rum från databasen

        let html = ''; // Börja med tom HTML

        // Loopa igenom alla rum
        for (let i = 0; i < rum.length; i++) {
            // Bygg HTML för varje rum
            html = html + '<div style="border:1px solid #ccc; margin:10px; padding:10px; border-radius:5px;">';
            html = html + '<h3>Rum ' + rum[i].nummer + '</h3>';
            html = html + '<p><strong>Pris:</strong> ' + rum[i].pris + ' kr/natt</p>';
            html = html + '<p><strong>Beskrivning:</strong> ' + rum[i].beskrivning + '</p>';
            html = html + '<p><strong>Max gäster:</strong> ' + rum[i].max_gaster + '</p>';
            html = html + '</div>';
        }

        // Stoppa in HTML:en i sidan (i div:en med id "rum-container")
        document.getElementById('rum-container').innerHTML = html;
    })
    .catch(function(fel) {
        // Om något går fel (API:et nere, fel adress, etc.)
        console.log('Fel vid hämtning:', fel);
        document.getElementById('rum-container').innerHTML = '<p style="color:red;">Kunde inte ladda rum. Kontrollera att API:et är igång.</p>';
    });
