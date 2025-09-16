import json
import csv
import pandas as pd
import os
from datetime import datetime
from src.utils import setup_logger

class Exporter:
    def __init__(self, output_dir="data/combined"):
        self.output_dir = output_dir
        self.logger = setup_logger('exporter', 'logs/export.log')
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize files if they don't exist
        self.json_file = os.path.join(output_dir, "listings.json")
        self.csv_file = os.path.join(output_dir, "listings.csv")
        self.excel_file = os.path.join(output_dir, "listings.xlsx")
        
        # Initialize JSON file with empty array if it doesn't exist
        if not os.path.exists(self.json_file):
            with open(self.json_file, 'w') as f:
                json.dump([], f)
    
    def export_listings(self, listings, site_name):
        """Export listings to all formats"""
        if not listings:
            self.logger.warning(f"No listings to export for {site_name}")
            return
        
        # Add site name and timestamp to each listing
        for listing in listings:
            listing['site'] = site_name
            listing['scraped_at'] = datetime.now().isoformat()
        
        try:
            self._export_to_json(listings)
            self._export_to_csv(listings)
            self._export_to_excel(listings)
            self.logger.info(f"Exported {len(listings)} listings from {site_name}")
        except Exception as e:
            self.logger.error(f"Error exporting listings: {e}")
    
    def _export_to_json(self, listings):
        """Append listings to JSON file"""
        try:
            # Read existing data
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r') as f:
                    existing_data = json.load(f)
            else:
                existing_data = []
            
            # Append new listings
            existing_data.extend(listings)
            
            # Write back to file
            with open(self.json_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error exporting to JSON: {e}")
            raise
    
    def _export_to_csv(self, listings):
        """Append listings to CSV file"""
        try:
            # Flatten the listings for CSV
            flattened = []
            for listing in listings:
                flat_listing = {
                    'site': listing.get('site', ''),
                    'title': listing.get('title', ''),
                    'price': listing.get('price', ''),
                    'location': listing.get('location', ''),
                    'url': listing.get('url', ''),
                    'scraped_at': listing.get('scraped_at', ''),
                    'beds': listing.get('details', {}).get('beds', ''),
                    'baths': listing.get('details', {}).get('baths', ''),
                    'sqft': listing.get('details', {}).get('sqft', ''),
                    'acres': listing.get('details', {}).get('acres', ''),
                    'property_type': listing.get('details', {}).get('property_type', ''),
                    'parking': listing.get('details', {}).get('parking', ''),
                    'garage': listing.get('details', {}).get('garage', ''),
                    'agent_name': listing.get('agent', {}).get('name', ''),
                    'agent_license': listing.get('agent', {}).get('license', ''),
                    'agent_office': listing.get('agent', {}).get('office', ''),
                    'agent_phone': listing.get('agent', {}).get('phone', '')
                }
                flattened.append(flat_listing)
            
            # Write to CSV
            fieldnames = [
                'site', 'title', 'price', 'location', 'beds', 'baths', 'sqft', 
                'acres', 'property_type', 'parking', 'garage', 'agent_name', 
                'agent_license', 'agent_office', 'agent_phone', 'url', 'scraped_at'
            ]
            
            file_exists = os.path.exists(self.csv_file)
            
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerows(flattened)
                
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {e}")
            raise
    
    def _export_to_excel(self, listings):
        """Export listings to Excel file (overwrites existing file)"""
        try:
            # Read existing CSV and convert to Excel
            if os.path.exists(self.csv_file):
                df = pd.read_csv(self.csv_file)
                df.to_excel(self.excel_file, index=False)
                
        except Exception as e:
            self.logger.error(f"Error exporting to Excel: {e}")
            raise