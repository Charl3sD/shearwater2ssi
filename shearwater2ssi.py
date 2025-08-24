#!/usr/bin/env python3
"""
Shearwater to SSI QR Code Generator
Extracts dive information from Shearwater database files and generates SSI-compatible QR codes

DISCLAIMER: This software is for DEMONSTRATION AND EDUCATIONAL PURPOSES ONLY.
Not affiliated with Shearwater Research Inc., SSI, or any diving organization.
USE AT YOUR OWN RISK. See DISCLAIMER.md for full legal disclaimer.
"""

import sqlite3
import qrcode
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import os
from PIL import Image, ImageTk
import io
import json


class ShearwaterToSSI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Shearwater to SSI QR Code Generator")
        self.root.geometry("1450x850")
        
        self.db_path = None
        self.db_files = {}
        self.dives_data = []
        self.selected_dives = []
        self.dive_regions = {}  # Available regions from JSON files
        self.current_region = None
        self.dive_sites = {}
        self.dive_settings = {}
        self.generated_qr_codes = []
        self.validation_qr_codes = []
        self.validation_qr_files = []  # List of validation QR filenames
        self.existing_dive_qr_codes = []  # Existing dive QR codes
        self.current_qr_index = 0
        self.qr_display_mode = 'dives'  # 'dives', 'existing_dives' or 'validations'
        self.config = {}
        
        self.load_config()
        self.scan_dive_regions()
        self.setup_ui()
        self.scan_for_db_files()
        self.load_latest_db()
        self.scan_validation_qrs()
        self.scan_existing_dive_qrs()
    
    def scan_dive_regions(self):
        """Scan for region JSON files in ssi_dive_sites directory"""
        sites_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ssi_dive_sites')
        self.dive_regions = {}
        
        if os.path.exists(sites_dir):
            for filename in os.listdir(sites_dir):
                if filename.lower().endswith('.json'):
                    region_name = os.path.splitext(filename)[0]
                    region_name = region_name.replace('_', ' ').title()
                    self.dive_regions[region_name] = os.path.join(sites_dir, filename)
        
        # Sort regions alphabetically
        self.dive_regions = dict(sorted(self.dive_regions.items()))
        
        # Load first region if available
        if self.dive_regions:
            first_region = list(self.dive_regions.keys())[0]
            self.load_region_sites(first_region)
        else:
            self.dive_sites = {"No Site (0)": "0"}
    
    def load_region_sites(self, region_name):
        """Load dive sites from a specific region JSON file"""
        self.current_region = region_name
        self.dive_sites = {}
        
        if region_name not in self.dive_regions:
            self.dive_sites = {"No Site (0)": "0"}
            return
        
        try:
            json_path = self.dive_regions[region_name]
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'result' in data and 'elements' in data['result']:
                    for site in data['result']['elements']:
                        if 'data' in site and 'properties' in site['data']:
                            props = site['data']['properties']
                            site_id = props.get('id', '')
                            site_name = props.get('name', '')
                            if site_id and site_name:
                                self.dive_sites[f"{site_name} ({site_id})"] = site_id
                print(f"Loaded {len(self.dive_sites)} dive sites from {region_name}")
        except Exception as e:
            print(f"Could not load dive sites from {region_name}: {e}")
            self.dive_sites = {"No Site (0)": "0"}
        
        if not self.dive_sites:
            self.dive_sites = {"No Site (0)": "0"}
        
        # Sort dive sites alphabetically
        self.dive_sites = dict(sorted(self.dive_sites.items()))
        
        # Update site combo if UI is initialized
        if hasattr(self, 'site_combo'):
            self.site_combo['values'] = list(self.dive_sites.keys())
            if self.dive_sites:
                self.site_combo.set(list(self.dive_sites.keys())[0])
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Top section: Database and User Info in one row with equal sizing
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        top_frame.columnconfigure(0, weight=1, uniform="top")
        top_frame.columnconfigure(1, weight=1, uniform="top")
        
        # Database section
        db_frame = ttk.LabelFrame(top_frame, text="Database", padding="5")
        db_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 2))
        
        self.db_combo = ttk.Combobox(db_frame, width=50, state='readonly')
        self.db_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.db_combo.bind('<<ComboboxSelected>>', self.on_db_selected)
        
        ttk.Button(db_frame, text="Browse", command=self.select_file, width=7).pack(side=tk.RIGHT, padx=2)
        ttk.Button(db_frame, text="Refresh", command=self.refresh_db_list, width=7).pack(side=tk.RIGHT, padx=2)
        self.file_label = ttk.Label(db_frame, text="", font=('TkDefaultFont', 8))
        self.file_label.pack(side=tk.RIGHT, padx=2)
        
        # User info section
        user_frame = ttk.LabelFrame(top_frame, text="Buddy Information (for QR codes)", padding="5")
        user_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(2, 0))
        
        # Display current user info
        user_info = f"User: {self.config.get('user', {}).get('firstname', 'Unknown')} {self.config.get('user', {}).get('lastname', 'Unknown')} (ID: {self.config.get('user', {}).get('master_id', '0')})"
        ttk.Label(user_frame, text=user_info, font=('TkDefaultFont', 9)).grid(row=0, column=0, columnspan=6, sticky=tk.W, padx=2, pady=2)
        
        # Buddy info - compact layout
        ttk.Label(user_frame, text="First:").grid(row=1, column=0, sticky=tk.W, padx=2)
        self.buddy_firstname_entry = ttk.Entry(user_frame, width=12)
        self.buddy_firstname_entry.grid(row=1, column=1, padx=2)
        self.buddy_firstname_entry.insert(0, self.config.get('buddy', {}).get('firstname', ''))
        self.buddy_firstname_entry.bind('<FocusOut>', self.save_config)
        
        ttk.Label(user_frame, text="Last:").grid(row=1, column=2, sticky=tk.W, padx=(10,2))
        self.buddy_lastname_entry = ttk.Entry(user_frame, width=12)
        self.buddy_lastname_entry.grid(row=1, column=3, padx=2)
        self.buddy_lastname_entry.insert(0, self.config.get('buddy', {}).get('lastname', ''))
        self.buddy_lastname_entry.bind('<FocusOut>', self.save_config)
        
        ttk.Label(user_frame, text="ID:").grid(row=1, column=4, sticky=tk.W, padx=(10,2))
        self.buddy_userid_entry = ttk.Entry(user_frame, width=8)
        self.buddy_userid_entry.grid(row=1, column=5, sticky=tk.W, padx=(2,10))
        self.buddy_userid_entry.insert(0, self.config.get('buddy', {}).get('master_id', ''))
        self.buddy_userid_entry.bind('<FocusOut>', self.save_config)
        
        # Dive list section - more compact
        dive_list_frame = ttk.LabelFrame(main_frame, text="Select Dives", padding="5")
        dive_list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=2)
        
        columns = ('Date', 'Time', 'Depth (m)', 'Duration (min)', 'Site', 'Entry Type')
        self.dive_tree = ttk.Treeview(dive_list_frame, columns=columns, show='tree headings', height=8)
        
        # Set column widths for better space usage
        self.dive_tree.column('#0', width=0, stretch=False)  # Hide tree column
        self.dive_tree.column('Date', width=85)
        self.dive_tree.column('Time', width=55)
        self.dive_tree.column('Depth (m)', width=75)
        self.dive_tree.column('Duration (min)', width=95)
        self.dive_tree.column('Site', width=180)
        self.dive_tree.column('Entry Type', width=85)
        
        for col in columns:
            self.dive_tree.heading(col, text=col)
        
        scrollbar = ttk.Scrollbar(dive_list_frame, orient=tk.VERTICAL, command=self.dive_tree.yview)
        self.dive_tree.configure(yscrollcommand=scrollbar.set)
        
        self.dive_tree.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=2, sticky=(tk.N, tk.S))
        
        # Settings frame - compact single row
        settings_frame = ttk.LabelFrame(dive_list_frame, text="Apply to Selected Dives", padding="3")
        settings_frame.grid(row=1, column=0, columnspan=2, pady=3, sticky=(tk.W, tk.E))
        
        # All settings in one row
        ttk.Label(settings_frame, text="Region:").pack(side=tk.LEFT, padx=2)
        self.region_combo = ttk.Combobox(settings_frame, values=list(self.dive_regions.keys()), width=12, state='readonly')
        self.region_combo.pack(side=tk.LEFT, padx=2)
        if self.dive_regions:
            self.region_combo.set(list(self.dive_regions.keys())[0])
        self.region_combo.bind('<<ComboboxSelected>>', self.on_region_selected)
        
        ttk.Label(settings_frame, text="Site:").pack(side=tk.LEFT, padx=(8,2))
        self.site_combo = ttk.Combobox(settings_frame, values=list(self.dive_sites.keys()), width=25)
        self.site_combo.pack(side=tk.LEFT, padx=2)
        if self.dive_sites:
            self.site_combo.set(list(self.dive_sites.keys())[0])
        
        ttk.Label(settings_frame, text="Entry:").pack(side=tk.LEFT, padx=(8,2))
        self.entry_combo = ttk.Combobox(settings_frame, values=['Boat (22)', 'Shore (21)'], width=10)
        self.entry_combo.pack(side=tk.LEFT, padx=2)
        self.entry_combo.set('Boat (22)')
        
        ttk.Button(settings_frame, text="Apply to Selected", command=self.apply_settings_to_selected).pack(side=tk.LEFT, padx=8)
        
        self.dive_tree.bind('<<TreeviewSelect>>', self.on_dive_select)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=3)
        
        ttk.Button(button_frame, text="Generate QR Codes", command=self.generate_qr_codes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Select All", command=self.select_all_dives).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Deselect All", command=self.deselect_all_dives).pack(side=tk.LEFT, padx=5)
        
        # QR management options
        ttk.Separator(button_frame, orient='vertical').pack(side=tk.LEFT, fill='y', padx=10)
        
        self.overwrite_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(button_frame, text="Overwrite existing", variable=self.overwrite_var).pack(side=tk.LEFT, padx=5)
        
        self.existing_qr_label = ttk.Label(button_frame, text="")
        self.existing_qr_label.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(button_frame, text="Clean Dive QRs", command=self.cleanup_dive_qrs).pack(side=tk.LEFT, padx=5)
        
        # Bottom section: Output and QR display
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=3)
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=2)
        
        # Output frame (smaller)
        output_frame = ttk.LabelFrame(bottom_frame, text="Output", padding="5")
        output_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0,2))
        
        self.output_text = tk.Text(output_frame, height=12, width=35, font=('TkDefaultFont', 9))
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # QR Code display frame (larger)
        qr_frame = ttk.LabelFrame(bottom_frame, text="QR Code Preview", padding="5")
        qr_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(2,0))
        
        # QR mode selection
        mode_frame = ttk.Frame(qr_frame)
        mode_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        ttk.Label(mode_frame, text="Display:").pack(side=tk.LEFT, padx=5)
        self.qr_mode_var = tk.StringVar(value="dives")
        ttk.Radiobutton(mode_frame, text="Generated Dive QRs", variable=self.qr_mode_var, value="dives",
                       command=self.switch_qr_mode).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Existing Dive QRs", variable=self.qr_mode_var, value="existing_dives", 
                       command=self.switch_qr_mode).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Validation QR Codes", variable=self.qr_mode_var, value="validations", 
                       command=self.switch_qr_mode).pack(side=tk.LEFT, padx=5)
        
        # Validation QR dropdown
        ttk.Label(mode_frame, text="Validation:").pack(side=tk.LEFT, padx=(20, 5))
        self.validation_combo = ttk.Combobox(mode_frame, width=30, state='readonly')
        self.validation_combo.pack(side=tk.LEFT, padx=5)
        self.validation_combo.bind('<<ComboboxSelected>>', self.on_validation_selected)
        
        ttk.Button(mode_frame, text="Refresh", command=self.scan_validation_qrs).pack(side=tk.LEFT, padx=5)
        
        # QR navigation controls
        nav_frame = ttk.Frame(qr_frame)
        nav_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        self.prev_btn = ttk.Button(nav_frame, text="◀ Previous", command=self.show_previous_qr, state='disabled')
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.qr_info_label = ttk.Label(nav_frame, text="No QR codes generated")
        self.qr_info_label.pack(side=tk.LEFT, expand=True)
        
        self.next_btn = ttk.Button(nav_frame, text="Next ▶", command=self.show_next_qr, state='disabled')
        self.next_btn.pack(side=tk.RIGHT, padx=5)
        
        # QR code display label
        self.qr_display = ttk.Label(qr_frame, text="QR codes will appear here\nafter generation", anchor='center')
        self.qr_display.pack(expand=True, fill=tk.BOTH)
        
        # Configure grid weights for proper resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)  # Dive list gets normal space
        main_frame.grid_rowconfigure(3, weight=1)  # Bottom section gets equal space
        main_frame.grid_columnconfigure(0, weight=1)
    
    def load_config(self):
        """Load configuration from config.json"""
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                # Create default config
                self.config = {
                    'user': {
                        'firstname': '',
                        'lastname': '',
                        'master_id': ''
                    },
                    'buddy': {
                        'firstname': '',
                        'lastname': '',
                        'master_id': ''
                    },
                    'defaults': {
                        'entry_type': 'Boat (22)',
                        'auto_load_latest_db': True
                    }
                }
                self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = {}
    
    def save_config(self, event=None):
        """Save configuration to config.json"""
        # Update config with current values if UI is initialized
        if hasattr(self, 'buddy_firstname_entry'):
            self.config['buddy']['firstname'] = self.buddy_firstname_entry.get()
            self.config['buddy']['lastname'] = self.buddy_lastname_entry.get()
            self.config['buddy']['master_id'] = self.buddy_userid_entry.get()
        
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def on_region_selected(self, event):
        """Handle region selection from dropdown"""
        selected_region = self.region_combo.get()
        if selected_region:
            self.load_region_sites(selected_region)
    
    def scan_for_db_files(self):
        """Scan the shearwater_databases directory for .db files"""
        self.db_files = {}
        db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shearwater_databases')
        
        # Create directory if it doesn't exist
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        try:
            for filename in os.listdir(db_dir):
                if filename.lower().endswith('.db'):
                    filepath = os.path.join(db_dir, filename)
                    # Get file modification time for sorting
                    mtime = os.path.getmtime(filepath)
                    self.db_files[filename] = {'path': filepath, 'mtime': mtime}
            
            # Sort by modification time (newest first)
            sorted_files = sorted(self.db_files.keys(), 
                                key=lambda x: self.db_files[x]['mtime'], 
                                reverse=True)
            
            # Update combo box
            self.db_combo['values'] = sorted_files
            
            if sorted_files:
                self.file_label.config(text=f"Found {len(sorted_files)} database(s)")
            else:
                self.file_label.config(text="No .db files found in directory")
                
        except Exception as e:
            print(f"Error scanning for DB files: {e}")
            self.file_label.config(text="Error scanning directory")
    
    def load_latest_db(self):
        """Automatically load the most recent .db file"""
        if self.config.get('defaults', {}).get('auto_load_latest_db', True) and self.db_combo['values']:
            latest_db = self.db_combo['values'][0]
            self.db_combo.set(latest_db)
            self.db_path = self.db_files[latest_db]['path']
            self.load_dives()
            self.file_label.config(text="Auto-loaded latest DB")
            # Rescan validation QRs when DB changes
            self.scan_validation_qrs()
            self.scan_existing_dive_qrs()
    
    def on_db_selected(self, event):
        """Handle database selection from dropdown"""
        selected = self.db_combo.get()
        if selected and selected in self.db_files:
            self.db_path = self.db_files[selected]['path']
            self.load_dives()
            self.file_label.config(text="")
            # Rescan validation QRs when DB changes
            self.scan_validation_qrs()
            self.scan_existing_dive_qrs()
    
    def refresh_db_list(self):
        """Refresh the list of database files"""
        self.scan_for_db_files()
        if self.db_combo['values']:
            # If there's a new latest file, optionally load it
            latest_db = self.db_combo['values'][0]
            if self.db_combo.get() != latest_db:
                response = messagebox.askyesno("New Database Found", 
                                              f"Found newer database: {latest_db}\nLoad it now?")
                if response:
                    self.db_combo.set(latest_db)
                    self.db_path = self.db_files[latest_db]['path']
                    self.load_dives()
                    self.scan_validation_qrs()
            self.scan_existing_dive_qrs()
        
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Shearwater Database File",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        
        if file_path:
            self.db_path = file_path
            # Add to db_files if not already there
            filename = os.path.basename(file_path)
            if filename not in self.db_files:
                mtime = os.path.getmtime(file_path)
                self.db_files[filename] = {'path': file_path, 'mtime': mtime}
                # Refresh combo box
                sorted_files = sorted(self.db_files.keys(), 
                                    key=lambda x: self.db_files[x]['mtime'], 
                                    reverse=True)
                self.db_combo['values'] = sorted_files
            
            self.db_combo.set(filename)
            self.file_label.config(text="Manually selected")
            self.load_dives()
            # Rescan validation QRs when DB changes
            self.scan_validation_qrs()
            self.scan_existing_dive_qrs()
            
    def load_dives(self):
        if not self.db_path:
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = """
            SELECT DiveId, DiveDate, Depth, DiveLengthTime, Site, Location,
                   AverageDepth, AverageTemp, Weather, Visibility
            FROM dive_details
            ORDER BY DiveDate DESC
            """
            
            cursor.execute(query)
            self.dives_data = cursor.fetchall()
            conn.close()
            
            for item in self.dive_tree.get_children():
                self.dive_tree.delete(item)
            
            dive_idx = 0
            for dive in self.dives_data:
                dive_id, dive_date, depth, duration, site, location, avg_depth, avg_temp, weather, visibility = dive
                
                if dive_date:
                    try:
                        dt = datetime.strptime(dive_date, "%Y-%m-%d %H:%M:%S")
                        date_str = dt.strftime("%Y-%m-%d")
                        time_str = dt.strftime("%H:%M")
                    except:
                        date_str = dive_date[:10] if len(dive_date) >= 10 else "N/A"
                        time_str = dive_date[11:16] if len(dive_date) >= 16 else "N/A"
                else:
                    date_str = "N/A"
                    time_str = "N/A"
                
                depth_m = f"{float(depth):.1f}" if depth else "0.0"
                duration_min = f"{int(duration)/60:.1f}" if duration else "0.0"
                
                default_site = list(self.dive_sites.keys())[0] if self.dive_sites else "No Site (0)"
                default_entry = self.config.get('defaults', {}).get('entry_type', 'Boat (22)')
                
                self.dive_settings[dive_idx] = {
                    'site': default_site,
                    'entry_type': default_entry
                }
                
                self.dive_tree.insert('', 'end', values=(
                    date_str, time_str, depth_m, duration_min, default_site, default_entry
                ))
                dive_idx += 1
                
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Loaded {len(self.dives_data)} dives from database\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dives: {str(e)}")
            
    def on_dive_select(self, event):
        """Update settings controls when a dive is selected"""
        selected_items = self.dive_tree.selection()
        if selected_items:
            item = selected_items[0]
            item_index = self.dive_tree.index(item)
            if item_index in self.dive_settings:
                settings = self.dive_settings[item_index]
                self.site_combo.set(settings['site'])
                self.entry_combo.set(settings['entry_type'])
    
    def apply_settings_to_selected(self):
        """Apply current settings to all selected dives"""
        selected_items = self.dive_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select at least one dive")
            return
        
        site = self.site_combo.get()
        entry_type = self.entry_combo.get()
        
        for item in selected_items:
            item_index = self.dive_tree.index(item)
            self.dive_settings[item_index] = {
                'site': site,
                'entry_type': entry_type
            }
            
            values = list(self.dive_tree.item(item, 'values'))
            values[4] = site
            values[5] = entry_type
            self.dive_tree.item(item, values=values)
        
        messagebox.showinfo("Success", f"Applied settings to {len(selected_items)} dive(s)")
    
    def select_all_dives(self):
        for item in self.dive_tree.get_children():
            self.dive_tree.selection_add(item)
            
    def deselect_all_dives(self):
        for item in self.dive_tree.get_children():
            self.dive_tree.selection_remove(item)
            
    def generate_qr_codes(self):
        selected_items = self.dive_tree.selection()
        
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select at least one dive")
            return
            
        # Use buddy info from config for QR codes
        firstname = self.config.get('buddy', {}).get('firstname', '') or 'Unknown'
        lastname = self.config.get('buddy', {}).get('lastname', '') or 'Unknown'
        user_id = self.config.get('buddy', {}).get('master_id', '') or '0'
        
        output_dir = os.path.join(os.path.dirname(self.db_path) if self.db_path else ".", "ssi_dives_qr_codes")
        os.makedirs(output_dir, exist_ok=True)
        
        # Clean existing QRs if overwrite mode is selected
        if self.overwrite_var.get() and os.path.exists(output_dir):
            for file in os.listdir(output_dir):
                if file.endswith('.png'):
                    try:
                        os.remove(os.path.join(output_dir, file))
                    except:
                        pass
            self.output_text.insert(tk.END, "Cleaned existing QR codes\n")
        
        self.output_text.delete(1.0, tk.END) if self.overwrite_var.get() else None
        self.generated_qr_codes = [] if self.overwrite_var.get() else self.generated_qr_codes
        generated_count = 0
        
        for item in selected_items:
            item_index = self.dive_tree.index(item)
            dive_data = self.dives_data[item_index]
            settings = self.dive_settings.get(item_index, {'site': 'No Site (0)', 'entry_type': 'Boat (22)'})
            
            qr_payload = self.create_ssi_payload(dive_data, firstname, lastname, user_id, settings)
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_payload)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            dive_date = dive_data[1]
            if dive_date:
                try:
                    dt = datetime.strptime(dive_date, "%Y-%m-%d %H:%M:%S")
                    filename = f"dive_{dt.strftime('%Y%m%d_%H%M%S')}.png"
                    date_str = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    filename = f"dive_{generated_count:03d}.png"
                    date_str = f"Dive {generated_count + 1}"
            else:
                filename = f"dive_{generated_count:03d}.png"
                date_str = f"Dive {generated_count + 1}"
                
            filepath = os.path.join(output_dir, filename)
            img.save(filepath)
            
            # Store QR code for display
            site_name = settings.get('site', 'Unknown')
            entry_type = settings.get('entry_type', 'Unknown')
            depth = dive_data[2]
            duration = dive_data[3]
            
            self.generated_qr_codes.append({
                'image': img,
                'filename': filename,
                'date': date_str,
                'site': site_name,
                'entry': entry_type,
                'depth': f"{float(depth):.1f}m" if depth else "0.0m",
                'duration': f"{int(duration)/60:.1f}min" if duration else "0.0min"
            })
            
            self.output_text.insert(tk.END, f"Generated QR code: {filename}\n")
            generated_count += 1
            
        self.output_text.insert(tk.END, f"\nSuccessfully generated {generated_count} QR codes in {output_dir}\n")
        
        # Display first QR code
        if self.generated_qr_codes:
            self.current_qr_index = 0
            self.display_qr_code()
            self.update_navigation_buttons()
        
        # Refresh existing QR count
        self.scan_existing_dive_qrs()
        
        messagebox.showinfo("Success", f"Generated {generated_count} QR codes in {output_dir}")
        
    def create_ssi_payload(self, dive_data, firstname, lastname, user_id, settings):
        dive_id, dive_date, depth, duration, site, location, avg_depth, avg_temp, weather, visibility = dive_data
        
        if dive_date:
            try:
                dt = datetime.strptime(dive_date, "%Y-%m-%d %H:%M:%S")
                datetime_str = dt.strftime("%Y%m%d%H%M")
            except:
                datetime_str = "202501010000"
        else:
            datetime_str = "202501010000"
            
        depth_m = float(depth) if depth else 0.0
        divetime = float(duration) / 60.0 if duration else 0.0
        
        site_name = settings.get('site', 'No Site (0)')
        site_code = self.dive_sites.get(site_name, "0")
        
        entry_type = settings.get('entry_type', 'Boat (22)')
        var_entry_id = "21" if "Shore" in entry_type else "22"
        
        var_weather_id = "1"
        var_water_body_id = "13"
        var_watertype_id = "5"
        var_current_id = "6"
        var_surface_id = "10"
        var_divetype_id = "24"
        
        airtemp_c = float(avg_temp) if avg_temp else 0.0
        vis_m = float(visibility) if visibility else 0.0
        
        payload = (
            f"dive;noid;"
            f"dive_type:0;"
            f"divetime:{divetime:.1f};"
            f"datetime:{datetime_str};"
            f"depth_m:{depth_m:.1f};"
            f"site:{site_code};"
            f"var_weather_id:{var_weather_id};"
            f"var_entry_id:{var_entry_id};"
            f"var_water_body_id:{var_water_body_id};"
            f"var_watertype_id:{var_watertype_id};"
            f"var_current_id:{var_current_id};"
            f"var_surface_id:{var_surface_id};"
            f"var_divetype_id:{var_divetype_id};"
            f"var_divetype_id:{var_divetype_id};"
            f"user_master_id:{user_id};"
            f"user_firstname:{firstname};"
            f"user_lastname:{lastname};"
            f"user_leader_id:;"
            f"airtemp_c:{airtemp_c:.1f};"
            f"vis_m:{vis_m:.1f}"
        )
        
        return payload
    
    def scan_validation_qrs(self):
        """Scan for validation QR codes in ssi_validations_qr_codes folder"""
        base_dir = os.path.dirname(self.db_path) if self.db_path else os.path.dirname(os.path.abspath(__file__))
        validation_dir = os.path.join(base_dir, "ssi_validations_qr_codes")
        
        self.validation_qr_files = []
        
        if os.path.exists(validation_dir):
            # Get all PNG files sorted by modification time (newest first)
            png_files = []
            for filename in os.listdir(validation_dir):
                if filename.lower().endswith('.png'):
                    filepath = os.path.join(validation_dir, filename)
                    mtime = os.path.getmtime(filepath)
                    png_files.append((filename, mtime))
            
            # Sort by modification time (newest first)
            png_files.sort(key=lambda x: x[1], reverse=True)
            self.validation_qr_files = [f[0] for f in png_files]
            
            # Update combo box
            self.validation_combo['values'] = self.validation_qr_files
            
            if self.validation_qr_files:
                # Set to latest file
                self.validation_combo.set(self.validation_qr_files[0])
    
    def on_validation_selected(self, event):
        """Handle validation QR selection from dropdown"""
        if self.qr_display_mode == 'validations':
            self.load_selected_validation_qr()
    
    def load_selected_validation_qr(self):
        """Load the selected validation QR code"""
        selected = self.validation_combo.get()
        if not selected:
            return
        
        base_dir = os.path.dirname(self.db_path) if self.db_path else os.path.dirname(os.path.abspath(__file__))
        validation_dir = os.path.join(base_dir, "ssi_validations_qr_codes")
        filepath = os.path.join(validation_dir, selected)
        
        if os.path.exists(filepath):
            try:
                img = Image.open(filepath)
                # Find if this QR is already loaded
                existing_index = None
                for i, qr in enumerate(self.validation_qr_codes):
                    if qr['filename'] == selected:
                        existing_index = i
                        break
                
                if existing_index is not None:
                    # Update existing
                    self.validation_qr_codes[existing_index]['image'] = img
                    self.current_qr_index = existing_index
                else:
                    # Add new
                    self.validation_qr_codes = [{
                        'image': img,
                        'filename': selected,
                        'type': 'validation'
                    }]
                    self.current_qr_index = 0
                
                self.display_qr_code()
                self.update_navigation_buttons()
            except Exception as e:
                print(f"Could not load {selected}: {e}")
    
    def load_all_validation_qrs(self):
        """Load all validation QR codes from dropdown list"""
        base_dir = os.path.dirname(self.db_path) if self.db_path else os.path.dirname(os.path.abspath(__file__))
        validation_dir = os.path.join(base_dir, "ssi_validations_qr_codes")
        
        self.validation_qr_codes = []
        
        for filename in self.validation_qr_files:
            filepath = os.path.join(validation_dir, filename)
            try:
                img = Image.open(filepath)
                self.validation_qr_codes.append({
                    'image': img,
                    'filename': filename,
                    'type': 'validation'
                })
            except Exception as e:
                print(f"Could not load {filename}: {e}")
        
        if self.validation_qr_codes:
            self.current_qr_index = 0
            self.display_qr_code()
            self.update_navigation_buttons()
    
    def scan_existing_dive_qrs(self):
        """Scan for existing dive QR codes in ssi_dives_qr_codes folder"""
        base_dir = os.path.dirname(self.db_path) if self.db_path else os.path.dirname(os.path.abspath(__file__))
        dive_qr_dir = os.path.join(base_dir, "ssi_dives_qr_codes")
        
        self.existing_dive_qr_codes = []
        
        if os.path.exists(dive_qr_dir):
            # Get all PNG files sorted by modification time (newest first)
            png_files = []
            for filename in os.listdir(dive_qr_dir):
                if filename.lower().endswith('.png'):
                    filepath = os.path.join(dive_qr_dir, filename)
                    mtime = os.path.getmtime(filepath)
                    png_files.append((filename, filepath, mtime))
            
            # Sort by modification time (newest first)
            png_files.sort(key=lambda x: x[2], reverse=True)
            
            # Load images
            for filename, filepath, mtime in png_files:
                try:
                    img = Image.open(filepath)
                    self.existing_dive_qr_codes.append({
                        'image': img,
                        'filename': filename,
                        'type': 'existing_dive',
                        'path': filepath
                    })
                except Exception as e:
                    print(f"Could not load {filename}: {e}")
        
        # Update existing QR count label
        if hasattr(self, 'existing_qr_label'):
            count = len(self.existing_dive_qr_codes)
            if count > 0:
                self.existing_qr_label.config(text=f"Existing: {count} QRs")
            else:
                self.existing_qr_label.config(text="No existing QRs")
    
    def cleanup_dive_qrs(self):
        """Delete all existing dive QR codes after confirmation"""
        if not self.existing_dive_qr_codes:
            messagebox.showinfo("Info", "No existing dive QR codes to clean up")
            return
        
        count = len(self.existing_dive_qr_codes)
        response = messagebox.askyesno("Confirm Cleanup", 
                                      f"Delete all {count} existing dive QR codes?\nThis cannot be undone.")
        
        if response:
            deleted = 0
            for qr in self.existing_dive_qr_codes:
                try:
                    os.remove(qr['path'])
                    deleted += 1
                except Exception as e:
                    print(f"Could not delete {qr['filename']}: {e}")
            
            self.existing_dive_qr_codes = []
            self.existing_qr_label.config(text="No existing QRs")
            
            # If currently viewing existing dives, switch to generated
            if self.qr_display_mode == 'existing_dives':
                self.qr_mode_var.set('dives')
                self.switch_qr_mode()
            
            messagebox.showinfo("Success", f"Deleted {deleted} QR code files")
            self.output_text.insert(tk.END, f"\nCleaned up {deleted} existing QR codes\n")
    
    def switch_qr_mode(self):
        """Switch between dive and validation QR code display"""
        self.qr_display_mode = self.qr_mode_var.get()
        self.current_qr_index = 0
        
        # If switching to validations and we have files but no loaded QRs, load them
        if self.qr_display_mode == 'validations':
            if self.validation_qr_files and not self.validation_qr_codes:
                # Load all validation QRs
                self.load_all_validation_qrs()
            elif self.validation_combo.get():
                # Load selected validation QR
                self.load_selected_validation_qr()
        elif self.qr_display_mode == 'existing_dives':
            # Refresh existing dive QRs
            self.scan_existing_dive_qrs()
        
        self.display_qr_code()
        self.update_navigation_buttons()
    
    def display_qr_code(self):
        """Display the current QR code in the UI"""
        # Select appropriate QR code list based on mode
        if self.qr_display_mode == 'validations':
            qr_list = self.validation_qr_codes
        elif self.qr_display_mode == 'existing_dives':
            qr_list = self.existing_dive_qr_codes
        else:
            qr_list = self.generated_qr_codes
        
        if not qr_list:
            if self.qr_display_mode == 'validations':
                text = "No validation QR codes available"
            elif self.qr_display_mode == 'existing_dives':
                text = "No existing dive QR codes found"
            else:
                text = "No generated QR codes available"
            self.qr_display.configure(image='', text=text)
            self.qr_info_label.config(text="No QR codes")
            return
        
        qr_data = qr_list[self.current_qr_index]
        
        # Resize QR code for display
        img = qr_data['image']
        img_resized = img.resize((300, 300), Image.Resampling.NEAREST)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(img_resized)
        
        # Update display
        self.qr_display.configure(image=photo, text="")
        self.qr_display.image = photo  # Keep a reference
        
        # Update info label based on QR type
        if self.qr_display_mode == 'validations':
            qr_list = self.validation_qr_codes
        elif self.qr_display_mode == 'existing_dives':
            qr_list = self.existing_dive_qr_codes
        else:
            qr_list = self.generated_qr_codes
        
        if qr_data.get('type') == 'validation':
            info_text = f"Validation QR {self.current_qr_index + 1}/{len(qr_list)}: {qr_data['filename']}"
        elif qr_data.get('type') == 'existing_dive':
            info_text = f"Existing Dive QR {self.current_qr_index + 1}/{len(qr_list)}: {qr_data['filename']}"
        else:
            info_text = f"Dive QR {self.current_qr_index + 1}/{len(qr_list)}: {qr_data.get('date', 'Unknown')}\n"
            if 'site' in qr_data:
                info_text += f"Site: {qr_data['site']}\n"
                info_text += f"Entry: {qr_data['entry']}, Depth: {qr_data['depth']}, Duration: {qr_data['duration']}"
        self.qr_info_label.config(text=info_text)
    
    def show_previous_qr(self):
        """Show the previous QR code"""
        if self.current_qr_index > 0:
            self.current_qr_index -= 1
            self.display_qr_code()
            self.update_navigation_buttons()
    
    def show_next_qr(self):
        """Show the next QR code"""
        if self.qr_display_mode == 'validations':
            qr_list = self.validation_qr_codes
        elif self.qr_display_mode == 'existing_dives':
            qr_list = self.existing_dive_qr_codes
        else:
            qr_list = self.generated_qr_codes
        if self.current_qr_index < len(qr_list) - 1:
            self.current_qr_index += 1
            self.display_qr_code()
            self.update_navigation_buttons()
    
    def update_navigation_buttons(self):
        """Update the state of navigation buttons"""
        if self.qr_display_mode == 'validations':
            qr_list = self.validation_qr_codes
        elif self.qr_display_mode == 'existing_dives':
            qr_list = self.existing_dive_qr_codes
        else:
            qr_list = self.generated_qr_codes
        
        if not qr_list:
            self.prev_btn.config(state='disabled')
            self.next_btn.config(state='disabled')
        else:
            self.prev_btn.config(state='normal' if self.current_qr_index > 0 else 'disabled')
            self.next_btn.config(state='normal' if self.current_qr_index < len(qr_list) - 1 else 'disabled')
        
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ShearwaterToSSI()
    app.run()
