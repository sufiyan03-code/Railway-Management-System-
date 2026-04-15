import json
import os
import uuid
import random

DATA_FILE = "data.json"

def initialize_data():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "trains": {},
            "tickets": {},
            "users": {
                "admin": {"password": "admin", "role": "admin"}
            }
        }
        _save_data(default_data)

def _load_data():
    if not os.path.exists(DATA_FILE):
        initialize_data()
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        
    if "users" not in data:
        data["users"] = {}
    if "admin" not in data["users"]:
        data["users"]["admin"] = {"password": "admin", "role": "admin"}
        _save_data(data)
        
    return data

def _save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_train(train_id, name, source, destination, total_seats, price=500):
    data = _load_data()
    if train_id in data["trains"]:
        raise ValueError(f"Train with ID {train_id} already exists.")
    
    # Initialize near some rough coordination for realistic live location mock
    lat = 28.6139 + random.uniform(-5.0, 5.0)
    lng = 77.2090 + random.uniform(-5.0, 5.0)

    data["trains"][train_id] = {
        "name": name,
        "source": source,
        "destination": destination,
        "total_seats": int(total_seats),
        "available_seats": int(total_seats),
        "price": float(price),
        "lat": lat,
        "lng": lng
    }
    _save_data(data)

def get_trains():
    data = _load_data()
    return data["trains"]

def update_train_locations():
    # Simulate movement for live location tracking
    data = _load_data()
    for t_id in data["trains"]:
        if "lat" not in data["trains"][t_id]:
            data["trains"][t_id]["lat"] = 28.6139 + random.uniform(-5.0, 5.0)
            data["trains"][t_id]["lng"] = 77.2090 + random.uniform(-5.0, 5.0)
            
        data["trains"][t_id]["lat"] += random.uniform(-0.05, 0.05)
        data["trains"][t_id]["lng"] += random.uniform(-0.05, 0.05)
    _save_data(data)

def book_ticket(train_id, passenger_name, age):
    data = _load_data()
    
    if train_id not in data["trains"]:
        raise ValueError("Invalid Train ID.")
        
    train = data["trains"][train_id]
    
    if train["available_seats"] <= 0:
        raise ValueError("No seats available on this train.")
        
    seat_number = train["total_seats"] - train["available_seats"] + 1
    
    pnr = "PNR" + str(uuid.uuid4().hex[:6]).upper()
    
    ticket = {
        "passenger_name": passenger_name,
        "age": age,
        "train_id": train_id,
        "seat_number": seat_number,
        "status": "CONFIRMED"
    }
    
    data["tickets"][pnr] = ticket
    data["trains"][train_id]["available_seats"] -= 1
    
    _save_data(data)
    return pnr

def get_tickets():
    data = _load_data()
    return data["tickets"]

def cancel_ticket(pnr):
    data = _load_data()
    
    if pnr not in data["tickets"]:
        raise ValueError("Invalid PNR.")
        
    ticket = data["tickets"][pnr]
    train_id = ticket["train_id"]
    
    if train_id in data["trains"]:
        data["trains"][train_id]["available_seats"] += 1
        
    del data["tickets"][pnr]
    _save_data(data)

def register_user(username, password, role="user"):
    data = _load_data()
    if "users" not in data:
        data["users"] = {}
    if username in data["users"]:
        raise ValueError("Username already exists.")
        
    data["users"][username] = {
        "password": password,
        "role": role
    }
    _save_data(data)

def verify_user(username, password):
    data = _load_data()
    users = data.get("users", {})
    if username in users:
        # Backward compatibility for old admin string
        if isinstance(users[username], str):
            if users[username] == password:
                return "admin" if username == "admin" else "user"
        elif users[username]["password"] == password:
            return users[username].get("role", "user")
    return None
