from typing import Dict, Any

def read_inventory(path: str) -> Dict[str, Dict[str, Any]]:
    """
    Reads the inventory file and loads data into a dictionary.
    - Expected file format: model,brand,quantity,price,origin
    - Ignores empty lines or comments (#).
    - Keys are stored as "model|brand".
    - Values are dictionaries with model, brand, quantity, price, and origin.
    """
    inventory: Dict[str, Dict[str, Any]] = {}

    line_no = 0
    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line_no += 1
                line = raw.strip()

                # Skip blank lines and comments
                if not line or line.startswith("#"):
                    continue

                try:
                    # Split into 5 fields: model, brand, quantity, price, origin
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) != 5:
                        raise ValueError("Each line must have 5 comma-separated values")

                    model, brand, qty_str, price_str, origin = parts
                    qty = int(qty_str)           # convert quantity to int
                    price = float(price_str)     # convert price to float
                    key = f"{model}|{brand}"     # unique key for dictionary

                    # Save record in inventory dictionary
                    inventory[key] = {
                        "model": model,
                        "brand": brand,
                        "quantity": qty,
                        "price": price,
                        "origin": origin.lower(),  # normalize origin
                    }
                except Exception as e:
                    raise ValueError(f"Error in inventory file at line {line_no}: {e}") from e
    except FileNotFoundError:
        raise FileNotFoundError(f"Inventory file not found: {path}")

    return inventory

    inventory: Dict[str, Dict[str, Any]] = {}

    line_no = 0
    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line_no += 1
                line = raw.strip()

                # Skip blank lines and comments
                if not line or line.startswith("#"):
                    continue

                try:
                    # Split into 5 fields: model, brand, quantity, price, origin
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) != 5:
                        raise ValueError("Each line must have 5 comma-separated values")

                    model, brand, qty_str, price_str, origin = parts
                    qty = int(qty_str)           # convert quantity to int
                    price = float(price_str)     # convert price to float
                    key = f"{model}|{brand}"     # unique key for dictionary

                    # Save record in inventory dictionary
                    inventory[key] = {
                        "model": model,
                        "brand": brand,
                        "quantity": qty,
                        "price": price,
                        "origin": origin.lower(),  # normalize origin
                    }
                except Exception as e:
                    raise ValueError(f"Error in inventory file at line {line_no}: {e}") from e
    except FileNotFoundError:
        raise FileNotFoundError(f"Inventory file not found: {path}")

    return inventory
