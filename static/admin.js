document.addEventListener('DOMContentLoaded', () => {
    fetchTickets();
    document.getElementById('refresh-db').addEventListener('click', fetchTickets);
    document.getElementById('add-train-form').addEventListener('submit', handleAddTrain);
    document.getElementById('cancel-ticket-form').addEventListener('submit', handleCancel);
});

async function fetchTickets() {
    const res = await fetch('/api/tickets');
    const tickets = await res.json();

    const tbody = document.querySelector('#tickets-table tbody');
    tbody.innerHTML = '';

    for (const [pnr, t] of Object.entries(tickets)) {
        tbody.innerHTML += `
            <tr>
                <td><strong>${pnr}</strong></td>
                <td>${t.passenger_name} (Age: ${t.age})</td>
                <td>${t.train_id}</td>
                <td>${t.seat_number}</td>
            </tr>
        `;
    }
}

function showToast(msg, type = 'success') {
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

async function handleAddTrain(e) {
    e.preventDefault();
    const resultDiv = document.getElementById('add-result');

    const payload = {
        train_id: document.getElementById('add-id').value,
        name: document.getElementById('add-name').value,
        source: document.getElementById('add-source').value,
        destination: document.getElementById('add-dest').value,
        total_seats: parseInt(document.getElementById('add-seats').value),
        price: parseFloat(document.getElementById('add-price').value)
    };

    try {
        const res = await fetch('/api/trains', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        resultDiv.className = 'result-msg';
        if (data.success) {
            showToast('Train added successfully to fleet!', 'success');
            document.getElementById('add-train-form').reset();
        } else {
            showToast(data.message, 'error');
        }
    } catch (err) {
        showToast('Connection error.', 'error');
    }
}

async function handleCancel(e) {
    e.preventDefault();
    const resultDiv = document.getElementById('cancel-result');
    const pnrInput = document.getElementById('cancel-pnr').value;
    const payload = { pnr: pnrInput };

    try {
        const res = await fetch('/api/cancel', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        resultDiv.className = 'result-msg';
        if (data.success) {
            showToast(`Ticket ${pnrInput} has been revoked successfully.`, 'success');
            document.getElementById('cancel-ticket-form').reset();
            fetchTickets();
        } else {
            showToast(data.message, 'error');
        }
    } catch (err) {
        showToast('Connection error.', 'error');
    }
}
