# Aurthor Bhabishya Koirala

"""
Core operations for the Shoes Wholesale System
Handles inventory management, sales, and reporting
ADDED 13% VAT on all transactions
"""
from datetime import datetime
from read import read_inventory
from write import write_inventory, write_invoice

class ShoesWholesaleSystem:
    """
    This is the main class that manages all core operations of the system.
    It loads and saves inventory.
    It handles purchase and restocks the products.
    """
    def __init__(self, inventory_path="inventory.txt", 
                 sales_log_path="sales_log.txt",
                 purchase_log_path="purchase_log.txt"):
        """
        It initialize the system with file paths.
        It loads inventory data and sets up ales and purchase logs.
        """
        self.inventory_path = inventory_path
        self.inventory = {}
        self.sales_log_path = sales_log_path
        self.purchase_log_path = purchase_log_path
        self._load_inventory()

    def _load_inventory(self):
        """
        It help to load inventory from the text file.
        If file does not exist, start with empty inventory.
        """
        try:
            self.inventory = read_inventory(self.inventory_path)
        except FileNotFoundError:
            # If the inventory file doesn't exist, we start with an empty inventory.
            # The file will be created on the first save.
            self.inventory = {}
        except Exception as e:
            print(f"Error loading inventory: {e}")
            self.inventory = {}

    def _save_inventory(self):
        """
        It help to save current inventory to file
        It ensures to continous after updates.      
        """
        write_inventory(self.inventory_path, self.inventory)

    def _new_invoice_id(self, prefix):
        """
        It generate a unique invoice ID with timestamp
        like: SALE-20250826-142530
        """
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d-%H%M%S")
        return f"{prefix}-{timestamp}"

    def _calc_discounts(self, origin, qty, unit_price):
        """
        It calculate discounts based on quantity and origin in time of purchase.
        It allow 5% discount for > 10 items
        Additional 7% for domestic items > 10
        """
        discount_rate = 0.0
        if qty > 10:
            discount_rate += 0.05
            if origin.lower() == "domestic":
                discount_rate += 0.07
                
        subtotal = qty * unit_price
        discount_amount = round(subtotal * discount_rate, 2)
        total = round(subtotal - discount_amount, 2)
        
        return {
            "subtotal": subtotal,
            "discount_rate": discount_rate,
            "discount_amount": discount_amount,
            "total": total
        }

    def _append_log(self, path, record_dict):
        """
        It help to appends a record to a plain text log file.
        It store key value paies line by line.
        It handle both sales and purchase records.
        """
        try:
            with open(path, "a", encoding="utf-8") as f:
                for key, value in record_dict.items():
                    if key == 'items':
                        # Handle list of items separately
                        for item in value:
                            # Convert item dict to a string format
                            item_str = ";".join(f"{k}={v}" for k, v in item.items())
                            f.write(f"item:{item_str}\n")
                    else:
                        f.write(f"{key}:{value}\n")
                f.write("---\n")  # Separator for records
        except Exception as e:
            print(f"Error writing to log file {path}: {e}")

    def _read_log(self, path):
        """
        It help to read transaction records back from a log file.
        It also reconstructs data into dicitionaries for later reporting.
        It returs a list of records.
        """
        records = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                current_record = {}
                for line in f:
                    line = line.strip()
                    if line == '---':
                        if current_record:
                            records.append(current_record)
                            current_record = {}
                        continue
                    
                    if ':' in line:
                        key, value = line.split(':', 1)
                        if key == 'item':
                            # Handle item lines
                            if 'items' not in current_record:
                                current_record['items'] = []
                            item_dict = {}
                            parts = value.split(';')
                            for part in parts:
                                if '=' in part:
                                    k, v = part.split('=', 1)
                                    # Convert numerical values back from string
                                    try:
                                        item_dict[k] = float(v) if '.' in v else int(v)
                                    except ValueError:
                                        item_dict[k] = v # Keep as string if conversion fails
                            current_record['items'].append(item_dict)
                        else:
                            # Convert numerical values back from string
                            try:
                                current_record[key] = float(value) if '.' in value else int(value)
                            except ValueError:
                                current_record[key] = value
        except FileNotFoundError:
            return [] # Return empty list if log file doesn't exist
        except Exception as e:
            print(f"Error reading log file {path}: {e}")
        return records

    def list_products(self):
        """
        It return all products in inventory sorted by brand and model.
        It help to make browsing consistent for users.
        """
        return sorted(
            list(self.inventory.values()),
            key=lambda x: (x["brand"].lower(), x["model"].lower())
        )

    def low_stock(self, threshold=20):
        """
        It returns a list of products with quantity less than or equal to threshold.
        It helps to identify items that shuld urgently restock.
        """
        return [v for v in self.inventory.values() if v["quantity"] <= threshold]

    def purchase(self, customer_name, cart):
        """
        It Process a sale transaction like :
        It validates cart items and stock.
        It apply  discounts and VAT in each transaction
        It updates inventory after sale and purchase.
        It generates invoice file and saves in log.
        It returns a sale record dictionary.
        """
        if not customer_name.strip():
            raise ValueError("Customer name cannot be empty.")
        if not cart:
            raise ValueError("Cart cannot be empty.")

        for model, brand, qty in cart:
            key = f"{model}|{brand}"
            if key not in self.inventory:
                raise KeyError(f"Item not found: {model} ({brand})")
            if qty <= 0:
                raise ValueError(f"Quantity must be positive for {model} ({brand}).")
            if self.inventory[key]["quantity"] < qty:
                raise ValueError(f"Insufficient stock for {model} ({brand}).")

        line_items = []
        grand_subtotal = 0.0
        grand_discount = 0.0
        total_after_discount = 0.0

        for model, brand, qty in cart:
            key = f"{model}|{brand}"
            item = self.inventory[key]
            
            disc = self._calc_discounts(item["origin"], qty, item["price"])
            self.inventory[key]["quantity"] -= qty

            line_items.append({
                "model": model, "brand": brand, "origin": item["origin"], "qty": qty,
                "unit_price": item["price"], "subtotal": disc["subtotal"],
                "discount_rate": disc["discount_rate"], "discount_amount": disc["discount_amount"],
                "total": disc["total"]
            })
            
            grand_subtotal += disc["subtotal"]
            grand_discount += disc["discount_amount"]
            total_after_discount += disc["total"]

        # --- VAT Calculation ---
        vat_amount = round(total_after_discount * 0.13, 2)
        grand_total = round(total_after_discount + vat_amount, 2)
        # --- End VAT Calculation ---

        self._save_inventory()

        invoice_id = self._new_invoice_id("SALE")
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        invoice_lines = [
            "=" * 60, "SHOES WHOLESALE SYSTEM - SALES INVOICE", "=" * 60,
            f"Invoice ID: {invoice_id}", f"Date: {date_str}", f"Customer: {customer_name}",
            "=" * 60,
            f"{'Item':<25} {'Qty':<6} {'Price':<10} {'Subtotal':<12} {'Discount':<10} {'Total':<12}",
            "-" * 60
        ]
        
        for li in line_items:
            item_desc = f"{li['model']} ({li['brand']})"
            invoice_lines.append(
                f"{item_desc:<25} {li['qty']:<6} {li['unit_price']:<10.2f} "
                f"{li['subtotal']:<12.2f} {li['discount_amount']:<10.2f} {li['total']:<12.2f}"
            )
        
        invoice_lines.extend([
            "-" * 60,
            f"Grand Subtotal: {'':<38} Rs. {grand_subtotal:>10.2f}",
            f"Total Discount: {'':<38} Rs. {grand_discount:>10.2f}",
            f"Amount after Discount:{'':<32} Rs. {total_after_discount:>10.2f}",
            f"VAT (13%): {'':<42} Rs. {vat_amount:>10.2f}",
            "=" * 60,
            f"AMOUNT PAYABLE: {'':<36} Rs. {grand_total:>10.2f}",
            "=" * 60, "Thank you for your business!", "=" * 60
        ])
        
        invoice_content = "\n".join(invoice_lines)
        invoice_path = write_invoice(invoice_id, invoice_content)

        sale_record = {
            "invoice_id": invoice_id, "date": date_str, "customer": customer_name,
            "items": line_items, "grand_subtotal": round(grand_subtotal, 2),
            "grand_discount": round(grand_discount, 2), 
            "vat_amount": vat_amount,
            "grand_total": grand_total,
            "invoice_path": invoice_path
        }
        
        self._append_log(self.sales_log_path, sale_record)
        return sale_record

    def restock(self, vendor_name, items):
        """
        It process a restock transaction like:
        It adds new items or updates existing items.
        It apply VaT to total cost.
        It saves invoice and log transaction.
        It returs a restock record dictionary
        """
        if not vendor_name.strip():
            raise ValueError("Vendor name cannot be empty.")
        if not items:
            raise ValueError("No items to restock.")

        line_items = []
        subtotal = 0.0

        for model, brand, qty, price, origin in items:
            key = f"{model}|{brand}"
            if key in self.inventory:
                self.inventory[key]["quantity"] += qty
                self.inventory[key]["price"] = price
            else:
                self.inventory[key] = {
                    "model": model, "brand": brand, "quantity": qty,
                    "price": price, "origin": origin.lower()
                }
            
            line_total = round(qty * price, 2)
            subtotal += line_total
            line_items.append({
                "model": model, "brand": brand, "qty": qty, "unit_price": price, 
                "origin": origin, "line_total": line_total
            })
        
        # VAT Calculation
        vat_amount = round(subtotal * 0.13, 2)
        grand_total = round(subtotal + vat_amount, 2)
        # End VAT Calculation

        self._save_inventory()
        invoice_id = self._new_invoice_id("RSTK")
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        invoice_lines = [
            "=" * 60, "SHOES WHOLESALE SYSTEM - RESTOCK INVOICE", "=" * 60,
            f"Invoice ID: {invoice_id}", f"Date: {date_str}", f"Vendor: {vendor_name}",
            "=" * 60,
            f"{'Item':<25} {'Qty':<6} {'Price':<10} {'Total':<12}",
            "-" * 60
        ]
        
        for li in line_items:
            item_desc = f"{li['model']} ({li['brand']})"
            invoice_lines.append(
                f"{item_desc:<25} {li['qty']:<6} {li['unit_price']:<10.2f} {li['line_total']:<12.2f}"
            )
        
        invoice_lines.extend([
            "-" * 60,
            f"Total before VAT: {'':<35} Rs. {subtotal:>10.2f}",
            f"VAT (13%): {'':<42} Rs. {vat_amount:>10.2f}",
            f"Total after VAT: {'':<37} Rs. {grand_total:>10.2f}",
            "=" * 60,
            "Inventory updated successfully", "=" * 60
        ])
        
        invoice_content = "\n".join(invoice_lines)
        invoice_path = write_invoice(invoice_id, invoice_content)

        restock_record = {
            "invoice_id": invoice_id, "date": date_str, "vendor": vendor_name,
            "items": line_items, "subtotal": subtotal, "vat_amount": vat_amount,
            "grand_total": grand_total,
            "invoice_path": invoice_path
        }
        
        self._append_log(self.purchase_log_path, restock_record)
        return restock_record

    def sales_summary(self):
        """It generate a summary of all sales from the text log.
        It generates total invoices, revenue, discount, 
        and the top 5 selling items.
        It return summary as dictionary.
        """
        sales = self._read_log(self.sales_log_path)

        total_invoices = len(sales)
        total_revenue = sum(s.get("grand_total", 0) for s in sales)
        total_discount = sum(s.get("grand_discount", 0) for s in sales)

        item_counter = {}
        for sale in sales:
            for item in sale.get("items", []):
                key = f"{item['model']}|{item['brand']}"
                item_counter[key] = item_counter.get(key, 0) + item.get("qty", 0)

        top_items = sorted(
            [{"key": k, "qty": v} for k, v in item_counter.items()],
            key=lambda x: x["qty"], reverse=True
        )[:5]

        return {
            "total_invoices": total_invoices, "total_revenue": round(total_revenue, 2),
            "total_discount": round(total_discount, 2), "top_items": top_items
        }

    def customer_history(self, customer_name):
        """
        It help to get purchase history for a specific customer from the text log.
        It look up sales log for case insensitive matches
        """
        if not customer_name.strip():
            raise ValueError("Customer name cannot be empty.")
            
        sales = self._read_log(self.sales_log_path)
        
        # Ensure customer names are compared case-insensitively
        return [s for s in sales if str(s.get("customer", "")).lower() == customer_name.lower()]
