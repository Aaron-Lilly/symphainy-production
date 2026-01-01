#!/usr/bin/env python3
"""
Test Data Generator for Content Pillar E2E Tests

Generates realistic test data files for testing file upload and parsing functionality.
"""

import os
import json
import csv
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any


class TestDataGenerator:
    """Generates test data files for E2E testing."""
    
    def __init__(self, output_dir: str = "test_data"):
        self.output_dir = output_dir
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        """Ensure the output directory exists."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_customer_data(self, num_customers: int = 100) -> List[Dict[str, Any]]:
        """Generate realistic customer data."""
        customers = []
        
        first_names = [
            "John", "Jane", "Michael", "Sarah", "David", "Lisa", "Robert", "Emily",
            "William", "Jessica", "James", "Ashley", "Christopher", "Amanda", "Daniel",
            "Jennifer", "Matthew", "Michelle", "Anthony", "Kimberly", "Mark", "Donna",
            "Donald", "Carol", "Steven", "Sandra", "Paul", "Ruth", "Andrew", "Sharon"
        ]
        
        last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
            "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
            "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"
        ]
        
        cities = [
            "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
            "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
            "Fort Worth", "Columbus", "Charlotte", "San Francisco", "Indianapolis",
            "Seattle", "Denver", "Washington", "Boston", "El Paso", "Nashville",
            "Detroit", "Oklahoma City", "Portland", "Las Vegas", "Memphis", "Louisville"
        ]
        
        states = [
            "NY", "CA", "IL", "TX", "AZ", "PA", "TX", "CA", "TX", "CA", "TX", "FL",
            "TX", "OH", "NC", "CA", "IN", "WA", "CO", "DC", "MA", "TX", "TN", "MI",
            "OK", "OR", "NV", "TN", "KY"
        ]
        
        for i in range(num_customers):
            customer = {
                "customer_id": f"CUST_{i+1:04d}",
                "first_name": random.choice(first_names),
                "last_name": random.choice(last_names),
                "email": f"customer{i+1}@example.com",
                "phone": f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
                "address": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Maple', 'Cedar'])} St",
                "city": random.choice(cities),
                "state": random.choice(states),
                "zip_code": f"{random.randint(10000, 99999)}",
                "registration_date": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d"),
                "total_orders": random.randint(0, 50),
                "total_spent": round(random.uniform(0, 5000), 2),
                "last_order_date": (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d") if random.random() > 0.3 else None,
                "customer_tier": random.choice(["Bronze", "Silver", "Gold", "Platinum"]),
                "is_active": random.choice([True, True, True, False])  # 75% active
            }
            customers.append(customer)
        
        return customers
    
    def generate_payment_data(self, num_payments: int = 200) -> List[Dict[str, Any]]:
        """Generate realistic payment data."""
        payments = []
        
        payment_methods = ["Credit Card", "Debit Card", "PayPal", "Bank Transfer", "Cash"]
        statuses = ["Completed", "Pending", "Failed", "Refunded"]
        
        for i in range(num_payments):
            payment = {
                "payment_id": f"PAY_{i+1:06d}",
                "customer_id": f"CUST_{random.randint(1, 100):04d}",
                "order_id": f"ORD_{random.randint(1, 150):06d}",
                "amount": round(random.uniform(10, 500), 2),
                "payment_method": random.choice(payment_methods),
                "status": random.choice(statuses),
                "payment_date": (datetime.now() - timedelta(days=random.randint(1, 180))).strftime("%Y-%m-%d %H:%M:%S"),
                "transaction_id": f"TXN_{random.randint(100000, 999999)}",
                "currency": "USD",
                "processing_fee": round(random.uniform(0.5, 5.0), 2)
            }
            payments.append(payment)
        
        return payments
    
    def generate_mainframe_data(self, num_records: int = 50) -> bytes:
        """Generate mainframe binary data for COBOL2CSV testing."""
        # This is a simplified binary format for testing
        # In reality, this would be proper EBCDIC-encoded data
        data = bytearray()
        
        for i in range(num_records):
            # Customer ID (8 bytes)
            customer_id = f"CUST{i+1:04d}".encode('ascii').ljust(8, b'\x00')
            data.extend(customer_id)
            
            # Customer Name (30 bytes)
            name = f"Customer {i+1}".encode('ascii').ljust(30, b'\x00')
            data.extend(name)
            
            # Amount (8 bytes, packed decimal)
            amount = random.randint(100, 9999)
            amount_bytes = amount.to_bytes(4, 'big')
            data.extend(amount_bytes)
            data.extend(b'\x00' * 4)  # Padding
            
            # Date (8 bytes, YYYYMMDD)
            date = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y%m%d")
            data.extend(date.encode('ascii'))
            
            # Status (1 byte)
            status = random.choice([b'A', b'I', b'D'])  # Active, Inactive, Deleted
            data.extend(status)
            
            # Record terminator
            data.extend(b'\x0D\x0A')  # CRLF
        
        return bytes(data)
    
    def generate_copybook(self) -> str:
        """Generate COBOL copybook for mainframe data."""
        copybook = """       01 CUSTOMER-RECORD.
           05 CUSTOMER-ID           PIC X(8).
           05 CUSTOMER-NAME         PIC X(30).
           05 AMOUNT                PIC 9(8).
           05 DATE                  PIC X(8).
           05 STATUS                PIC X(1).
        """
        return copybook
    
    def generate_csv_file(self, filename: str, data: List[Dict[str, Any]]) -> str:
        """Generate CSV file from data."""
        filepath = os.path.join(self.output_dir, filename)
        
        if not data:
            return filepath
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        return filepath
    
    def generate_json_file(self, filename: str, data: List[Dict[str, Any]]) -> str:
        """Generate JSON file from data."""
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
        
        return filepath
    
    def generate_binary_file(self, filename: str, data: bytes) -> str:
        """Generate binary file from data."""
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'wb') as binaryfile:
            binaryfile.write(data)
        
        return filepath
    
    def generate_text_file(self, filename: str, content: str) -> str:
        """Generate text file from content."""
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as textfile:
            textfile.write(content)
        
        return filepath
    
    def generate_all_test_files(self):
        """Generate all test files for E2E testing."""
        print("🔄 Generating test data files...")
        
        # Generate customer data
        customers = self.generate_customer_data(100)
        self.generate_csv_file("test_customers.csv", customers)
        self.generate_json_file("test_customers.json", customers)
        
        # Generate payment data
        payments = self.generate_payment_data(200)
        self.generate_csv_file("test_payments.csv", payments)
        self.generate_json_file("test_payments.json", payments)
        
        # Generate mainframe data
        mainframe_data = self.generate_mainframe_data(50)
        self.generate_binary_file("test_mainframe.dat", mainframe_data)
        
        # Generate copybook
        copybook = self.generate_copybook()
        self.generate_text_file("test_copybook.cpy", copybook)
        
        # Generate invalid files for error testing
        self.generate_text_file("invalid_file.txt", "This is not a valid data file")
        
        # Generate corrupted CSV
        corrupted_csv = "This is not a valid CSV file\nwith,invalid,structure"
        self.generate_text_file("corrupted.csv", corrupted_csv)
        
        print(f"✅ Generated test files in {self.output_dir}/")
        print("   - test_customers.csv (100 customer records)")
        print("   - test_customers.json (100 customer records)")
        print("   - test_payments.csv (200 payment records)")
        print("   - test_payments.json (200 payment records)")
        print("   - test_mainframe.dat (50 mainframe records)")
        print("   - test_copybook.cpy (COBOL copybook)")
        print("   - invalid_file.txt (for error testing)")
        print("   - corrupted.csv (for error testing)")


if __name__ == "__main__":
    generator = TestDataGenerator()
    generator.generate_all_test_files()





