let map;
let trainMarkers = {};

document.addEventListener('DOMContentLoaded', () => {
    initMap();
    fetchTrains();
    setInterval(fetchTrains, 5000); // Live location polling

    document.getElementById('book-form').addEventListener('submit', handleBook);
});

function initMap() {
    // Center roughly around New Delhi
    map = L.map('map').setView([28.6139, 77.2090], 5);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
}

async function fetchTrains() {
    const res = await fetch('/api/trains');
    const trains = await res.json();
    
    const list = document.getElementById('train-list');
    const select = document.getElementById('train-select');
    
    // Only update select if it's empty to prevent resetting user selection continually
    const shouldUpdateSelect = select.options.length <= 1;

    list.innerHTML = '';
    
    for (const [id, t] of Object.entries(trains)) {
        // UI List Update
        list.innerHTML += `
            <div class="train-item">
                <div class="train-item-info">
                    <strong>${t.name} (${id})</strong>
                    <span>${t.source} &rarr; ${t.destination}</span>
                </div>
                <div class="seats-badge">${t.available_seats}/${t.total_seats} Seats</div>
            </div>
        `;

        // Update Dropdown
        if (shouldUpdateSelect && t.available_seats > 0) {
            const opt = document.createElement('option');
            opt.value = id;
            opt.setAttribute('data-price', t.price || 0);
            opt.textContent = `${t.name} (₹${t.price || 0}) - Seats: ${t.available_seats}`;
            select.appendChild(opt);
        }

        // Live Map Update
        if (!trainMarkers[id]) {
            trainMarkers[id] = L.circleMarker([t.lat, t.lng], {
                color: '#6366f1',
                radius: 8,
                fillOpacity: 0.8
            }).addTo(map).bindPopup(`<b>${t.name}</b><br>ID: ${id}`);
        } else {
            trainMarkers[id].setLatLng([t.lat, t.lng]);
        }
    }
}

function showToast(msg, type='success') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = msg;
    container.appendChild(toast);
    
    setTimeout(() => { toast.remove(); }, 4500);
}

async function handleBook(e) {
    e.preventDefault();
    const resultDiv = document.getElementById('booking-result');
    resultDiv.className = 'result-msg';
    resultDiv.textContent = 'Automating booking...';

    const payload = {
        train_id: document.getElementById('train-select').value,
        passenger_name: document.getElementById('passenger-name').value,
        age: parseInt(document.getElementById('passenger-age').value)
    };

    try {
        const res = await fetch('/api/book', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (data.success) {
            resultDiv.textContent = '';
            
            const selectedOpt = document.getElementById('train-select').options[document.getElementById('train-select').selectedIndex];
            const price = selectedOpt ? selectedOpt.getAttribute('data-price') : 0;
            
            showToast(`Success! Your Ticket PNR is ${data.pnr} (Billed: ₹${price})`, 'success');
            document.getElementById('book-form').reset();
            fetchTrains(); // instant refresh
            
            // force re-populate select next fetch
            document.getElementById('train-select').innerHTML = '<option value="">Select a Train...</option>';
        } else {
            resultDiv.classList.add('error');
            resultDiv.textContent = `Error: ${data.message}`;
            showToast(data.message, 'error');
        }
    } catch(err) {
        resultDiv.classList.add('error');
        resultDiv.textContent = `Connection failed.`;
        showToast('Connection failed.', 'error');
    }
}
