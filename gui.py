import tkinter as tk
from tkinter import ttk, messagebox
import data_manager

class RailwayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Railway Management System")
        self.root.geometry("800x600")

        # Initialize data
        data_manager.initialize_data()

        # Styles
        style = ttk.Style()
        style.configure("TNotebook.Tab", padding=[10, 5])
        style.configure("TFrame", background="#f0f0f0")
        
        # Main Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Tabs
        self.tab_trains = ttk.Frame(self.notebook, style="TFrame")
        self.tab_book = ttk.Frame(self.notebook, style="TFrame")
        self.tab_tickets = ttk.Frame(self.notebook, style="TFrame")

        self.notebook.add(self.tab_trains, text="Train Management")
        self.notebook.add(self.tab_book, text="Book Ticket")
        self.notebook.add(self.tab_tickets, text="Passenger/Ticket Info")

        # Setup Tabs
        self.setup_trains_tab()
        self.setup_book_tab()
        self.setup_tickets_tab()
        
        # Bind tab change event to refresh data
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_tab_changed(self, event):
        self.refresh_train_list()
        self.refresh_ticket_list()
        self.refresh_train_dropdown()

    # --- Train Management Tab ---
    def setup_trains_tab(self):
        # Form Frame
        form_frame = ttk.LabelFrame(self.tab_trains, text="Add New Train", padding=(10, 10))
        form_frame.pack(side="top", fill="x", padx=10, pady=10)

        ttk.Label(form_frame, text="Train ID:").grid(row=0, column=0, sticky="w", pady=5)
        self.train_id_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.train_id_var).grid(row=0, column=1, padx=5)

        ttk.Label(form_frame, text="Name:").grid(row=0, column=2, sticky="w", pady=5)
        self.train_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.train_name_var).grid(row=0, column=3, padx=5)

        ttk.Label(form_frame, text="Source:").grid(row=1, column=0, sticky="w", pady=5)
        self.train_src_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.train_src_var).grid(row=1, column=1, padx=5)

        ttk.Label(form_frame, text="Destination:").grid(row=1, column=2, sticky="w", pady=5)
        self.train_dest_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.train_dest_var).grid(row=1, column=3, padx=5)

        ttk.Label(form_frame, text="Total Seats:").grid(row=2, column=0, sticky="w", pady=5)
        self.train_seats_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.train_seats_var).grid(row=2, column=1, padx=5)

        ttk.Button(form_frame, text="Add Train", command=self.add_train).grid(row=2, column=3, sticky="e", pady=10)

        # List Frame
        list_frame = ttk.LabelFrame(self.tab_trains, text="Available Trains", padding=(10, 10))
        list_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        columns = ("ID", "Name", "Source", "Destination", "Total Seats", "Available Seats")
        self.train_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.train_tree.heading(col, text=col)
            self.train_tree.column(col, anchor="center", width=100)
        self.train_tree.pack(fill="both", expand=True)

        self.refresh_train_list()

    def add_train(self):
        try:
            data_manager.add_train(
                self.train_id_var.get(),
                self.train_name_var.get(),
                self.train_src_var.get(),
                self.train_dest_var.get(),
                self.train_seats_var.get()
            )
            messagebox.showinfo("Success", "Train added successfully!")
            self.train_id_var.set("")
            self.train_name_var.set("")
            self.train_src_var.set("")
            self.train_dest_var.set("")
            self.train_seats_var.set("")
            self.refresh_train_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_train_list(self):
        for item in self.train_tree.get_children():
            self.train_tree.delete(item)
        
        trains = data_manager.get_trains()
        for t_id, t_info in trains.items():
            self.train_tree.insert("", "end", values=(
                t_id, t_info["name"], t_info["source"], t_info["destination"], 
                t_info["total_seats"], t_info["available_seats"]
            ))

    # --- Book Ticket Tab ---
    def setup_book_tab(self):
        form_frame = ttk.LabelFrame(self.tab_book, text="Book Ticket", padding=(10, 10))
        form_frame.pack(side="top", fill="x", padx=10, pady=10)

        ttk.Label(form_frame, text="Select Train:").grid(row=0, column=0, sticky="w", pady=5)
        self.book_train_var = tk.StringVar()
        self.train_dropdown = ttk.Combobox(form_frame, textvariable=self.book_train_var, state="readonly")
        self.train_dropdown.grid(row=0, column=1, padx=5, pady=5)
        self.refresh_train_dropdown()

        ttk.Label(form_frame, text="Passenger Name:").grid(row=1, column=0, sticky="w", pady=5)
        self.pass_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.pass_name_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Age:").grid(row=2, column=0, sticky="w", pady=5)
        self.pass_age_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.pass_age_var).grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(form_frame, text="Book Ticket", command=self.book_ticket).grid(row=3, column=1, sticky="w", pady=10)

    def refresh_train_dropdown(self):
        trains = data_manager.get_trains()
        self.train_dropdown['values'] = [f"{t_id} - {t_info['name']}" for t_id, t_info in trains.items()]

    def book_ticket(self):
        selected = self.book_train_var.get()
        if not selected:
            messagebox.showerror("Error", "Please select a train.")
            return
            
        train_id = selected.split(" - ")[0]
        name = self.pass_name_var.get()
        age = self.pass_age_var.get()
        
        if not name or not age:
            messagebox.showerror("Error", "Please enter passenger details.")
            return
            
        try:
            pnr = data_manager.book_ticket(train_id, name, int(age))
            messagebox.showinfo("Success", f"Ticket booked successfully!\nPNR: {pnr}")
            self.pass_name_var.set("")
            self.pass_age_var.set("")
            self.book_train_var.set("")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --- Passenger/Ticket Info Tab ---
    def setup_tickets_tab(self):
        cancel_frame = ttk.LabelFrame(self.tab_tickets, text="Cancel Ticket", padding=(10, 10))
        cancel_frame.pack(side="top", fill="x", padx=10, pady=10)

        ttk.Label(cancel_frame, text="Enter PNR to Cancel:").grid(row=0, column=0, sticky="w", pady=5)
        self.cancel_pnr_var = tk.StringVar()
        ttk.Entry(cancel_frame, textvariable=self.cancel_pnr_var).grid(row=0, column=1, padx=5)
        ttk.Button(cancel_frame, text="Cancel Ticket", command=self.cancel_ticket).grid(row=0, column=2, padx=5)

        list_frame = ttk.LabelFrame(self.tab_tickets, text="Booked Tickets", padding=(10, 10))
        list_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        columns = ("PNR", "Passenger Name", "Age", "Train ID", "Seat Number")
        self.ticket_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.ticket_tree.heading(col, text=col)
            self.ticket_tree.column(col, anchor="center", width=120)
        self.ticket_tree.pack(fill="both", expand=True)

        self.refresh_ticket_list()

    def cancel_ticket(self):
        pnr = self.cancel_pnr_var.get()
        if not pnr:
            messagebox.showerror("Error", "Please enter a valid PNR.")
            return
            
        try:
            data_manager.cancel_ticket(pnr)
            messagebox.showinfo("Success", f"Ticket {pnr} cancelled successfully.")
            self.cancel_pnr_var.set("")
            self.refresh_ticket_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_ticket_list(self):
        for item in self.ticket_tree.get_children():
            self.ticket_tree.delete(item)
            
        tickets = data_manager.get_tickets()
        for pnr, t_info in tickets.items():
            self.ticket_tree.insert("", "end", values=(
                pnr, t_info["passenger_name"], t_info["age"], 
                t_info["train_id"], t_info["seat_number"]
            ))
