// Hämta recensioner för ett rum
async function hamtaRecensioner(rum_id) {
    try {
        const response = await fetch(`http://localhost:8000/api/rooms/${rum_id}/reviews`);
        const data = await response.json();
        return data.recensioner;
    } catch (error) {
        return [];
    }
}

// Visa recensioner i HTML
function visaRecensioner(recensioner) {
    if (recensioner.length === 0) {
        return '<p>Inga recensioner ännu</p>';
    }
    // Skapa HTML för recensionerna
    let html = '<h4>📝 Recensioner:</h4>';
    for (let r of recensioner) {
        let stjarnor = '';
        for (let i = 1; i <= 5; i++) {
            stjarnor += i <= r.betyg ? '⭐' : '☆';
        }
        // Skapa en ruta för varje recension
        html += '<div style="border-top:1px solid #ddd; padding:8px 0;">';
        html += '<strong>' + r.anvandare + '</strong> ' + stjarnor + '<br>';
        html += r.kommentar + '<br>';
        html += '<small>' + new Date(r.datum).toLocaleDateString() + '</small>';
        html += '</div>';
    }
    return html;
}

// Hämta data från vårt API
// 
fetch('http://localhost:8000/api/rooms')
    .then(function(svar) { 
        return svar.json();
    })
    .then(async function(rum) {
        let html = '';
        const user = JSON.parse(localStorage.getItem('user'));
        
        for (let i = 0; i < rum.length; i++) {
            const recensioner = await hamtaRecensioner(rum[i].id);
            const recensionerHtml = visaRecensioner(recensioner);
            
            html += '<div style="border:1px solid #ccc; margin:10px; padding:10px; border-radius:5px;">';
            html += '<h3>Rum ' + rum[i].nummer + '</h3>';
            html += '<p><strong>Pris:</strong> ' + rum[i].pris + ' kr/natt</p>';
            html += '<p><strong>Beskrivning:</strong> ' + rum[i].beskrivning + '</p>';
            html += '<p><strong>Max gäster:</strong> ' + rum[i].max_gaster + '</p>';
            html += '<div>' + recensionerHtml + '</div>';
            
            if (user) {
                html += '<button onclick="bokaRum(' + rum[i].id + ')" style="margin-top:10px;">📅 Boka</button>';
            } else {
                html += '<button disabled style="margin-top:10px; background:#ccc;">🔒 Logga in för att boka</button>';
            }
            html += '</div>';
        }
        
        document.getElementById('rum-container').innerHTML = html;
    })
    .catch(function(fel) {
        console.log('Fel vid hämtning:', fel);
        document.getElementById('rum-container').innerHTML = '<p style="color:red;">Kunde inte ladda rum. Kontrollera att API:et är igång.</p>';
    });

//  LOGGA IN 
async function login() {
    const email = document.getElementById('login-email').value;
    const losenord = document.getElementById('login-password').value;
    // Skicka inloggningsdata till servern
    try {
        const response = await fetch('http://localhost:8000/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, losenord })
        });
        
        const data = await response.json();
        // Om inloggningen lyckades, spara användardata i localStorage och visa inloggad vy
        if (data.status === 'ok') {
            localStorage.setItem('user', JSON.stringify({
                id: data.user_id,
                namn: data.namn,
                email: data.email,
                roll: data.roll
            }));
            visaInloggad(data.namn);
            location.reload();
        } else {
            alert('Fel email eller lösenord');
        }
    } catch (error) {
        alert('Kunde inte ansluta till servern');
    }
}

// REGISTRERA 

async function register() {
    const namn = document.getElementById('register-name').value;
    const email = document.getElementById('register-email').value;
    const losenord = document.getElementById('register-password').value;
    
    try {
        const response = await fetch('http://localhost:8000/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ namn, email, losenord })
        });
        
        const data = await response.json();
        // Om registreringen lyckades, visa inloggningsformuläret
        if (data.message) {
            alert('Registrering klar! Du kan nu logga in.');
            visaLogin();
        } else {
            alert('Något gick fel: ' + (data.error || 'Okänt fel'));
        }
    } catch (error) {
        alert('Kunde inte ansluta till servern');
    }
}

// BOKA RUM
async function bokaRum(rum_id) {
    const user = JSON.parse(localStorage.getItem('user'));
    
    if (!user) {
        alert('Du måste logga in för att boka');
        return;
    }
    
    const incheckning = prompt('Incheckningsdatum (ÅÅÅÅ-MM-DD):');
    const utcheckning = prompt('Utcheckningsdatum (ÅÅÅÅ-MM-DD):');
    
    if (!incheckning || !utcheckning) return;
    
    try {
        const response = await fetch('http://localhost:8000/api/book', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                rum_id: rum_id,
                anvandare_id: user.id,
                incheckning: incheckning,
                utcheckning: utcheckning
            })
        });
        
        const data = await response.json();
        alert(data.message || data.error);
        location.reload();
    } catch (error) {
        alert('Kunde inte boka rum');
    }
}

// MINA BOKNINGAR 
async function visaMinaBokningar() {
    const user = JSON.parse(localStorage.getItem('user'));
    
    if (!user) {
        alert('Du måste logga in');
        return;
    }
    
    try {
        const response = await fetch('http://localhost:8000/api/bookings');
        const allaBokningar = await response.json();
        const minaBokningar = allaBokningar.filter(b => b.gast === user.namn);
        
        let html = '';
        for (let b of minaBokningar) {
            html += '<div style="border:1px solid #ccc; margin:10px; padding:10px;">';
            html += '<h3>Rum ' + b.rum_nr + '</h3>';
            html += '<p>Pris: ' + b.pris + ' kr</p>';
            html += '<p>Incheckning: ' + b.incheckning + '</p>';
            html += '<p>Utcheckning: ' + b.utcheckning + '</p>';
            html += '<button onclick="avbokaRum(' + b.boknings_id + ')">Avboka</button>';
            html += '</div>';
        }
        
        document.getElementById('bokningar-lista').innerHTML = html || '<p>Inga bokningar</p>';
        document.getElementById('bokningar-container').style.display = 'block';
        document.getElementById('rum-main').style.display = 'none';
        document.getElementById('auth-container').style.display = 'none';
    } catch (error) {
        alert('Kunde inte hämta bokningar');
    }
}

// AVBOKA RUM 
async function avbokaRum(boknings_id) {
    if (!confirm('Avboka?')) return;
    
    const response = await fetch(`http://localhost:8000/api/bookings/${boknings_id}`, {
        method: 'DELETE'
    });
    
    const data = await response.json();
    alert(data.message);
    visaMinaBokningar();
}

//  STÄNG BOKNINGAR
function stangBokningar() {
    document.getElementById('bokningar-container').style.display = 'none';
    document.getElementById('rum-main').style.display = 'block';
    const user = JSON.parse(localStorage.getItem('user'));
    if (user) {
        document.getElementById('auth-container').style.display = 'none';
        document.getElementById('user-info').style.display = 'block';
    } else {
        document.getElementById('auth-container').style.display = 'block';
        document.getElementById('user-info').style.display = 'none';
    }
    location.reload();
}

// VISA FORMULÄR 
function visaLogin() {
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('register-form').style.display = 'none';
}

function visaRegister() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('register-form').style.display = 'block';
}

function visaInloggad(namn) {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('register-form').style.display = 'none';
    document.getElementById('user-info').style.display = 'block';
    document.getElementById('user-name').innerText = namn;
}

function logout() {
    localStorage.removeItem('user');
    location.reload();
}

// KÖR NÄR SIDAN LADDAS
window.onload = function() {
    const user = JSON.parse(localStorage.getItem('user'));
    if (user) {
        visaInloggad(user.namn);
    }
};