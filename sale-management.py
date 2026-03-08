from datetime import datetime
import os

# ---------------- Product Class ----------------

class Product:
    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock

# ---------------- Customer Class ----------------
class Customer:
    def __init__(self, name, phone):
        self.name = name
        self.phone = phone

# ---------------- Sale Class ----------------
class Sale:
    def __init__(self, customer, date=None, items=None):
        self.customer = customer
        self.items = items if items else []
        self.date = date if date else datetime.now()

    def add_item(self, product, qty):
        if qty <= product.stock:
            self.items.append((product, qty))
            product.stock -= qty
            return True
        return False

    def total(self):
        return sum(product.price * qty for product, qty in self.items)

    def receipt(self):
        print("\n------ RECEIPT ------")
        print("Customer:", self.customer.name)
        print("Phone:", self.customer.phone)
        print("Date:", self.date.strftime("%Y-%m-%d %H:%M:%S"))
        print("---------------------")
        for product, qty in self.items:
            subtotal = product.price * qty
            print(f"{product.name} | Qty: {qty} | Price: {product.price} | Subtotal: {subtotal}")
        print("---------------------")
        print("TOTAL:", self.total())
        print("---------------------\n")

# ---------------- Sales System ----------------
class SalesSystem:
    SALES_FILE = "sales.txt"
    STOCK_FILE = "products.txt"

    def __init__(self):
        self.products = []
        self.sales_history = []
        self.load_stock()
        self.load_sales()

    # ---------------- Products ----------------
    def add_product(self, name, price, stock):
        self.products.append(Product(name, price, stock))
        self.save_stock()

    def show_products(self):
        print("\nAvailable Products")
        for i, p in enumerate(self.products):
            print(i, f"{p.name} | Price: {p.price} | Stock: {p.stock}")

    # ---------------- Stock Persistence ----------------
    def save_stock(self):
        with open(self.STOCK_FILE, "w") as f:
            for p in self.products:
                f.write(f"{p.name}|{p.price}|{p.stock}\n")

    def load_stock(self):
        if not os.path.exists(self.STOCK_FILE):
            return
        with open(self.STOCK_FILE, "r") as f:
            for line in f:
                name, price, stock = line.strip().split("|")
                self.products.append(Product(name, float(price), int(stock)))

    # ---------------- Sales Persistence ----------------
    def save_sales_to_file(self):
        with open(self.SALES_FILE, "w") as f:
            for sale in self.sales_history:
                f.write(f"Customer:{sale.customer.name}\n")
                f.write(f"Phone:{sale.customer.phone}\n")
                f.write(f"Date:{sale.date.strftime('%Y-%m-%d %H:%M:%S')}\n")
                for product, qty in sale.items:
                    f.write(f"{product.name}|{qty}|{product.price}\n")
                f.write(f"TOTAL:{sale.total()}\n")
                f.write("END\n")

    def load_sales(self):
        if not os.path.exists(self.SALES_FILE):
            return
        with open(self.SALES_FILE, "r") as f:
            lines = f.readlines()
        sale = None
        items = []
        for line in lines:
            line = line.strip()
            if line.startswith("Customer:"):
                sale = {}
                items = []
                sale["customer"] = line.split(":", 1)[1]
            elif line.startswith("Phone:"):
                sale["phone"] = line.split(":", 1)[1]
            elif line.startswith("Date:"):
                sale["date"] = datetime.strptime(line.split(":", 1)[1], "%Y-%m-%d %H:%M:%S")
            elif line.startswith("TOTAL:"):
                sale["total"] = float(line.split(":", 1)[1])
                sale["items"] = items
            elif line == "END":
                customer = Customer(sale["customer"], sale["phone"])
                sale_obj = Sale(customer, sale["date"])
                for item in sale["items"]:
                    p = Product(item["name"], item["price"], stock=0)
                    sale_obj.items.append((p, item["qty"]))
                self.sales_history.append(sale_obj)
            else:
                if "|" in line:
                    name, qty, price = line.split("|")
                    items.append({"name": name, "qty": int(qty), "price": float(price)})

    # ---------------- Make Sale ----------------
    def make_sale(self):
        name = input("Customer name: ")
        phone = input("Customer phone: ")
        customer = Customer(name, phone)
        sale = Sale(customer)

        while True:
            self.show_products()
            try:
                index = int(input("Choose product number: "))
                qty = int(input("Quantity: "))
            except ValueError:
                print("Invalid input")
                continue

            if index < 0 or index >= len(self.products):
                print("Invalid product")
                continue

            product = self.products[index]
            if sale.add_item(product, qty):
                print("Product added to cart")
                self.save_stock()
            else:
                print("Not enough stock")

            more = input("Add another product? (y/n): ")
            if more.lower() != "y":
                break

        self.sales_history.append(sale)
        self.save_sales_to_file()
        print("Sale completed!")
        sale.receipt()

    # ---------------- Sales History ----------------
    def show_sales_history(self):
        print("\n--- Sales History ---")
        for i, sale in enumerate(self.sales_history):
            print(f"[{i}] Customer: {sale.customer.name} | Total: {sale.total()} | Date: {sale.date.strftime('%Y-%m-%d %H:%M')}")
            for product, qty in sale.items:
                print("-", product.name, "x", qty)

    # ---------------- Daily Report ----------------
    def daily_sales_report(self):
        today = datetime.now().date()
        total = 0
        print("\n--- Daily Sales Report ---")
        for sale in self.sales_history:
            if sale.date.date() == today:
                print(sale.customer.name, "| Total:", sale.total())
                total += sale.total()
        print("Total Revenue Today:", total)

    # ---------------- Clear History ----------------
    def clear_sales_history(self):
        confirm = input("Are you sure you want to delete ALL sales history? (y/n): ")
        if confirm.lower() == "y":
            self.sales_history = []
            open(self.SALES_FILE, "w").close()
            print("All sales history has been deleted!")
        else:
            print("Operation cancelled.")

    # ---------------- Edit Receipt ----------------
    def edit_receipt(self):
        self.show_sales_history()
        try:
            index = int(input("Enter sale number to edit: "))
            sale = self.sales_history[index]
        except (ValueError, IndexError):
            print("Invalid selection")
            return

        while True:
            print("\n--- Edit Receipt Menu ---")
            print("1. Edit Customer Name")
            print("2. Edit Customer Phone")
            print("3. Edit Sale Date")          # <-- new option
            print("4. Edit Product Quantity")
            print("5. Add New Product")
            print("6. Remove Product")
            print("7. Finish Editing")

            choice = input("Choose option: ")

            if choice == "1":
                new_name = input(f"New customer name ({sale.customer.name}): ")
                if new_name.strip():
                    sale.customer.name = new_name

            elif choice == "2":
                new_phone = input(f"New phone ({sale.customer.phone}): ")
                if new_phone.strip():
                    sale.customer.phone = new_phone

            elif choice == "3":  # <-- Edit date
                new_date_str = input(f"New date and time (YYYY-MM-DD HH:MM:SS) ({sale.date.strftime('%Y-%m-%d %H:%M:%S')}): ")
                if new_date_str.strip():
                    try:
                        sale.date = datetime.strptime(new_date_str, "%Y-%m-%d %H:%M:%S")
                        print("Date updated successfully!")
                    except ValueError:
                        print("Invalid date format. Use YYYY-MM-DD HH:MM:SS.")

            elif choice == "4":
                for i, (product, qty) in enumerate(sale.items):
                    print(f"[{i}] {product.name} x {qty}")
                try:
                    item_index = int(input("Select product number to edit quantity: "))
                    product, old_qty = sale.items[item_index]
                    new_qty = int(input(f"New quantity for {product.name} ({old_qty}): "))
                    diff = new_qty - old_qty
                    if product.stock >= diff:
                        product.stock -= diff
                        sale.items[item_index] = (product, new_qty)
                        self.save_stock()
                        print("Quantity updated.")
                    else:
                        print("Not enough stock for this change.")
                except (ValueError, IndexError):
                    print("Invalid selection.")

            elif choice == "5":
                self.show_products()
                try:
                    prod_index = int(input("Choose product number to add: "))
                    qty = int(input("Quantity: "))
                    product = self.products[prod_index]
                    if product.stock >= qty:
                        sale.items.append((product, qty))
                        product.stock -= qty
                        self.save_stock()
                        print(f"{product.name} added to receipt.")
                    else:
                        print("Not enough stock.")
                except (ValueError, IndexError):
                    print("Invalid input.")

            elif choice == "6":
                for i, (product, qty) in enumerate(sale.items):
                    print(f"[{i}] {product.name} x {qty}")
                try:
                    rem_index = int(input("Select product number to remove: "))
                    product, qty = sale.items.pop(rem_index)
                    product.stock += qty
                    self.save_stock()
                    print(f"{product.name} removed from receipt.")
                except (ValueError, IndexError):
                    print("Invalid selection.")

            elif choice == "7":
                break

            else:
                print("Invalid option.")

        self.save_sales_to_file()
        print("Receipt updated successfully!")
        sale.receipt()

# ---------------- Create System ----------------
system = SalesSystem()

# Add default products if stock file is empty
if len(system.products) == 0:
    system.add_product("Bread", 1.5, 20)
    system.add_product("Cake", 5, 10)
    system.add_product("Cookie", 2, 15)

# ---------------- Menu ----------------
while True:
    print("\n===== SALES MANAGEMENT =====")
    print("1. Sell Product")
    print("2. View Sales History")
    print("3. Daily Sales Report")
    print("4. Clear Sales History")
    print("5. Edit Receipt")
    print("6. Exit")

    choice = input("Choose option: ")

    if choice == "1":
        system.make_sale()
    elif choice == "2":
        system.show_sales_history()
    elif choice == "3":
        system.daily_sales_report()
    elif choice == "4":
        system.clear_sales_history()
    elif choice == "5":
        system.edit_receipt()
    elif choice == "6":
        break
    else:
        print("Invalid option")