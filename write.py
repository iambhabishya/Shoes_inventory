# Author Bhabishya Koirala

def write_inventory(path, inventory):
    """
    It save the current inventory dictionary into a text file.
    The output format is: model, brand, quantity, price, origin
    The items are sorted by brand and model for consistent file structure.
    
    """
    lines = []
    # Sort items by brand and model for consistent file output
    sorted_items = sorted(inventory.values(), key=lambda x: (x['brand'], x['model']))
    
    for item in sorted_items:
        line = f"{item['model']}, {item['brand']}, {item['quantity']}, {item['price']}, {item['origin']}"
        lines.append(line)
    
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except Exception as e:
        print(f"Error: Could not write to inventory file {path}: {e}")

def write_invoice(invoice_id, content):
    """ 
   It creates a text file for a invoice.
   The file name is based on invoice id.
   It returns tthe full file path of the saved invoice.
    """
    # The file will be created in the same folder as the script.
    file_path = f"{invoice_id}.txt"
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path
    except Exception as e:
        print(f"Error: Could not write invoice file {file_path}: {e}")
        return None
