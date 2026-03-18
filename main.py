# Aurthor Bhabishya Koirala

"""
This the main interface of Shoes Wholesale System.
A simple text based system for managing shoe inventory and sales.
"""
from Operation import ShoesWholesaleSystem

def clear_screen():
    """
    It restore and clear the screen by printing many new lines.
    It helps to refresh interface during repated menu display.
    """
    print("\n" * 50)

def display_header(title):
    """It use to display a formatted header with a given title.
    It create a similar look for all the section in the program. 
    """
    print("=" * 60)
    print(f"{title:^60}")
    print("=" * 60)

def valid_int(message, min_val=None, max_val=None):
    """It gets a valid input from the user.
    It keep asking until input valid.
    It help to restrict input within minimum and maxium value.
    """
    while True:
        try:
            value = int(input(message).strip())
            if min_val is not None and value < min_val:
                print(f"Value must be at least {min_val}.")
                continue
            if max_val is not None and value > max_val:
                print(f"Value must be at most {max_val}.")
                continue
            return value
        except ValueError:
            print("Please enter a valid whole number.")

def valid_float(message, min_val=None):
    """ It help to  gets a valid float  input from the user. 
    It Can enforce a minimum allowed value.
    """
    while True:
        try:
            value = float(input(message).strip())
            if min_val is not None and value < min_val:
                print(f"Value must be at least {min_val}.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number.")

def show_products(sys):
    """It display all available products in a formatted table.
    It also print all available products in formatted table with 
    details like model, brand, quantity, price, and origin..
    """
    display_header("AVAILABLE PRODUCTS")
    print(f"{'No.':<4} {'Model':<20} {'Brand':<15} {'Quantity':<6} {'Price':<10} {'Origin':<12}")
    print("-" * 70)
    
    products = sys.list_products()
    if not products:
        print("No products in inventory.")
    else:
        for i, product in enumerate(products, 1):
            print(f"{i:<4} {product['model']:<20} {product['brand']:<15} "
                  f"{product['quantity']:<6} {product['price']:<10.2f} {product['origin']:<12}")
    print()

def do_purchase(sys):
    """This handle the purchase process, 
    allowing multiple items to be added to a cart.
    It validates stock availability
    It also generates invoice once confirmed.
    """
    display_header("NEW SALE")
    
    customer = input("Customer Name: ").strip()
    if not customer:
        print("Customer name is required!")
        return
    
    products = sys.list_products()
    if not products:
        print("No products available for sale!")
        return
    
    cart = []
    print("\nAdd items to cart (press Enter without a number to finish):")
    
    while True:
        show_products(sys)
        try:
            item_num_str = input("Enter product number to add to cart (or press Enter to finish): ").strip()
            if not item_num_str:
                break
                
            item_num = int(item_num_str)
            if not (1 <= item_num <= len(products)):
                print("Invalid product number! Please try again.")
                continue
                
            product = products[item_num - 1]
            print(f"Selected: {product['model']} ({product['brand']})")
            
            max_qty = product['quantity']
            qty = valid_int(f"Quantity (available: {max_qty}): ", 1, max_qty)
            
            cart.append((product['model'], product['brand'], qty))
            print(f"SUCCESS: Added {qty} of {product['model']} to cart.\n")
            
        except ValueError:
            print("Invalid input. Please enter a valid product number.")
        except Exception as e:
            print(f"An error occurred: {e}")
    
    if not cart:
        print("No items added to cart. Purchase cancelled.")
        return
        
    try:
        print("\n--- Cart Summary ---")
        for i, (model, brand, qty) in enumerate(cart, 1):
            print(f"{i}. {model} ({brand}) - Quantity: {qty}")
        
        confirm = input("Confirm purchase? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Purchase cancelled.")
            return
            
        sale = sys.purchase(customer, cart)
        
        print("\n" + "="*50)
        print("PURCHASE COMPLETED SUCCESSFULLY!")
        print("="*50)
        print(f"Invoice ID: {sale['invoice_id']}")
        print(f"Customer: {customer}")
        print(f"Total Amount: Rs. {sale['grand_total']:,.2f}")
        print(f"Invoice saved as: {sale['invoice_path']}")
        print("="*50)
        
    except Exception as e:
        print(f"\nError during purchase: {e}")

def handle_restock(sys):
    """ It restock new products into inventory.
    It also collects vendoor details and product info.
    It aso update inventory after restocking.
    This function Confirm transaction and generates invoies.
    """
    display_header("RESTOCK INVENTORY")
    
    vendor = input("Vendor/Supplier Name: ").strip()
    if not vendor:
        print("Vendor name is required!")
        return
    
    items = []
    print("\nAdd items to restock (press Enter without model to finish):")
    
    while True:
        model = input("\nShoe Model (press Enter to finish): ").strip()
        if not model:
            break
        brand = input("Brand: ").strip()
        if not brand:
            print("Brand is required!")
            continue
        qty = valid_int("Quantity: ", 1)
        price = valid_float("Unit Price (Rs.): ", 0.01)
        
        while True:
            origin = input("Origin (domestic/international): ").strip().lower()
            if origin in ("domestic", "international"):
                break
            print("Please enter either 'domestic' or 'international'")
        
        items.append((model, brand, qty, price, origin))
        print(f"Added {model} to restock list.")
    
    if not items:
        print("No items added for restocking.")
        return
        
    try:
        total_cost = sum(qty * price for _, _, qty, price, _ in items)
        print(f"\nTotal Restock Cost: Rs. {total_cost:,.2f}")
        confirm = input("Confirm restock? (y/n): ").strip().lower()
        
        if confirm != 'y':
            print("Restock cancelled.")
            return
            
        restock = sys.restock(vendor, items)
        
        print("\n" + "="*50)
        print("RESTOCK COMPLETED SUCCESSFULLY!")
        print("="*50)
        print(f"Invoice ID: {restock['invoice_id']}")
        print(f"Vendor: {vendor}")
        print(f"Total Cost: Rs. {restock['grand_total']:,.2f}")
        print(f"Invoice saved as: {restock['invoice_path']}")
        print("="*50)
        
    except Exception as e:
        print(f"Error during restock: {e}")

def do_restock_existing(sys):
    """Handle restocking of existing products,
      including out-of-stock items.
      Allow a user to update  price and quanity.
      It upaate inventory and generates bill.
      """
    display_header("RESTOCK EXISTING PRODUCT")
    
    vendor = input("Supplier Name: ").strip()
    if not vendor:
        print("Supplier name is required!")
        return
    
    # Get all products including those with zero quantity
    products = sys.list_products()
    if not products:
        print("No products available in inventory!")
        return
    
    # Display products with numbers (including zero stock items)
    print(f"\n{'No.':<4} {'Model':<20} {'Brand':<15} {'Stock':<6} {'Price':<10} {'Status':<12}")
    print("-" * 67)
    for i, product in enumerate(products, 1):
        status = "In Stock" if product['quantity'] > 0 else "Out of Stock"
        print(f"{i:<4} {product['model']:<20} {product['brand']:<15} "
              f"{product['quantity']:<6} {product['price']:<10.2f} {status:<12}")
    
    try:
        item_num = valid_int("\nSelect product number to restock: ", 1, len(products))
        product = products[item_num - 1]
        
        print(f"\nSelected: {product['model']} ({product['brand']})")
        print(f"Current stock: {product['quantity']} units")
        print(f"Current price: Rs. {product['price']:.2f}")
        
        # Ask if user wants to change the price
        change_price = input("Do you want to change the price? (y/n): ").strip().lower()
        if change_price == 'y':
            new_price = valid_float("Enter new price (Rs.): ", 0.01)
            price = new_price
            print(f"Price updated to: Rs. {new_price:.2f}")
        else:
            price = product['price']
            print(f"Keeping original price: Rs. {price:.2f}")
        
        qty = valid_int("Quantity to add: ", 1)
        
        # Calculate new total stock
        new_stock = product['quantity'] + qty
        
        # Confirm restock
        total_cost = qty * price
        print(f"\nRestock Details:")
        print(f"Current stock: {product['quantity']} units")
        print(f"Adding: {qty} units")
        print(f"New total stock: {new_stock} units")
        print(f"Price: Rs. {price:.2f}")
        print(f"Total cost before VAT: Rs. {total_cost:,.2f}")
        print(f"VAT (13%): Rs. {total_cost * 0.13:,.2f}")
        print(f"Total cost after VAT: Rs. {total_cost * 1.13:,.2f}")
        
        confirm = input("\nConfirm restock? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Restock cancelled.")
            return
        
        # Restock using the product details (with optional new price)
        items = [(product['model'], product['brand'], qty, price, product['origin'])]
        restock = sys.restock(vendor, items)
        
        print("\n" + "="*50)
        print("RESTOCK COMPLETED SUCCESSFULLY!")
        print("="*50)
        print(f"Invoice ID: {restock['invoice_id']}")
        print(f"Supplier: {vendor}")
        print(f"Product: {product['model']} ({product['brand']})")
        print(f"Previous stock: {product['quantity']} units")
        print(f"Added: {qty} units")
        print(f"New stock: {new_stock} units")
        print(f"Price: Rs. {price:.2f}")
        print(f"Total Cost after VAT: Rs. {restock['grand_total']:,.2f}")
        print(f"Invoice saved as: {restock['invoice_path']}")
        print("="*50)
        
    except Exception as e:
        print(f"Error during restock: {e}")

def show_low_stock(sys):
    """Display products with low inventory or equal to threshold.
    It also help to identify item that needed to be restock.
    """
    display_header("LOW STOCK ALERT")
    
    threshold = valid_int("Low stock threshold (default 20): ", 1)
    low_stock_items = sys.low_stock(threshold)
    
    if not low_stock_items:
        print(f"No products with stock level at or below {threshold}.")
        return
        
    print(f"\nProducts with stock ≤ {threshold}:")
    print(f"{'Model':<20} {'Brand':<15} {'Qty':<6} {'Price':<10}")
    print("-" * 50)
    
    for product in low_stock_items:
        print(f"{product['model']:<20} {product['brand']:<15} "
              f"{product['quantity']:<6} {product['price']:<10.2f}")

def show_sales_summary(sys):
    """It Display all sales summary report
    which inclue total invoices, income, discount and top selling item
    """
    display_header("SALES SUMMARY")
    
    summary = sys.sales_summary()
    
    print(f"Total Invoices: {summary['total_invoices']}")
    print(f"Total Revenue: Rs. {summary['total_revenue']:,.2f}")
    print(f"Total Discount Given: Rs. {summary['total_discount']:,.2f}")
    
    if summary['top_items']:
        print("\nTop Selling Items:")
        for i, item in enumerate(summary['top_items'], 1):
            model, brand = item['key'].split('|', 1)
            print(f"{i}. {model} ({brand}) - {item['qty']} units sold")
    else:
        print("\nNo sales recorded yet.")

def show_customer_history(sys):
    """It display purchase history of a customer according to their name
    It display date, invoice ID, and total amount spent.
    """
    display_header("CUSTOMER HISTORY")
    
    customer = input("Customer Name: ").strip()
    if not customer:
        print("Customer name is required!")
        return
        
    history = sys.customer_history(customer)
    
    if not history:
        print(f"No purchase history found for {customer}.")
        return
        
    print(f"\nPurchase History for {customer}:")
    print(f"{'Date':<20} {'Invoice ID':<20} {'Amount (Rs.)':<12}")
    print("-" * 50)
    
    for purchase in history:
        date = purchase['date'].split()[0]
        print(f"{date:<20} {purchase['invoice_id']:<20} {purchase['grand_total']:>12,.2f}")

def main():
    """ It is Main program function
    It display menu repeatedly until user exits.
    It calls appropriate function or each menu option."""
    system = ShoesWholesaleSystem()
    
    while True:
        clear_screen()
        display_header("SPEEDZWEAR WHOLESALE SYSTEM")
        
        print("1. View Products")
        print("2. Make a sell")
        print("3. Restock Inventory")
        print("4. Check Low Stock")
        print("5. View Sales Summary")
        print("6. View Customer History")
        print("7. Exit")
        print("-" * 30)
        
        choice = input("Please select an option (1-7): ").strip()
        
        if choice == "1":
            clear_screen()
            show_products(system)
        elif choice == "2":
            clear_screen()
            do_purchase(system)
        elif choice == "3":
            clear_screen()
            handle_restock(system)
        elif choice == "4":
            clear_screen()
            show_low_stock(system)
        elif choice == "5":
            clear_screen()
            show_sales_summary(system)
        elif choice == "6":
            clear_screen()
            show_customer_history(system)
        elif choice == "7":
            print("\nThank you - Have a good time!!")
            break
        else:
            print("Invalid option! Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
