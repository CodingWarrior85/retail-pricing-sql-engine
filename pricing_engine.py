import sqlite3
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Walmart Price & Rolldown Engine")


def init_db():
    """Initializes a local SQL database file and inserts sample electronic store items."""
    conn = sqlite3.connect("walmart_pricing.db")
    cursor = conn.cursor()

    # Create a relational SQL table
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS inventory
                   (
                       item_id
                       TEXT
                       PRIMARY
                       KEY,
                       name
                       TEXT
                       NOT
                       NULL,
                       original_price
                       REAL
                       NOT
                       NULL,
                       is_rolldown
                       INTEGER
                       DEFAULT
                       0
                   )
                   """)

    # Clear old data and insert fresh database rows for testing
    cursor.execute("DELETE FROM inventory")
    sample_items = [
        ("2001", "onn. 50-Inch 4K Roku Smart TV", 248.00, 1),  # 1 = Active Rolldown Discount
        ("2002", "Apple AirPods Pro (2nd Gen)", 199.00, 0),  # 0 = Standard Price
        ("2003", "HP 14-Inch Chromebook Laptop", 179.00, 1),  # 1 = Active Rolldown Discount
        ("2004", "Nintendo Switch OLED Console", 349.99, 0)  # 0 = Standard Price
    ]
    cursor.executemany("INSERT INTO inventory VALUES (?, ?, ?, ?)", sample_items)

    conn.commit()
    conn.close()


# Run database setup immediately when the server initializes
init_db()


@app.get("/api/price/{item_id}")
def check_price(item_id: str):
    """SQL backend endpoint: Queries the database file directly using standard SQL syntax."""
    conn = sqlite3.connect("walmart_pricing.db")
    cursor = conn.cursor()

    # Secure parameter-driven SQL Query statement
    cursor.execute("SELECT name, original_price, is_rolldown FROM inventory WHERE item_id = ?", (item_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        name, original_price, is_rolldown = row
        current_price = original_price
        savings = 0.0

        # Core Business Logic: Calculate a 15% markdown if marked as an active rolldown
        if is_rolldown == 1:
            savings = round(original_price * 0.15, 2)
            current_price = round(original_price - savings, 2)

        return {
            "status": "success",
            "name": name,
            "original_price": original_price,
            "current_price": current_price,
            "savings": savings,
            "on_clearance": bool(is_rolldown)
        }

    return {"status": "error", "message": "Item identifier not found in database records."}


@app.get("/", response_class=HTMLResponse)
def pricing_interface():
    """Customer-facing digital tag layout."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Walmart Digital Price Signage</title>
        <style>
            body { font-family: 'Arial', sans-serif; background: #e9ecef; padding: 50px; display: flex; justify-content: center; }
            .tag { background: white; border: 3px solid #0071dc; border-radius: 8px; padding: 25px; width: 350px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
            .input-box { width: 80%; padding: 10px; margin-bottom: 15px; font-size: 14px; border: 1px solid #ccc; border-radius: 4px; }
            .btn { background: #ffc220; color: #333; border: none; padding: 10px 20px; font-weight: bold; border-radius: 4px; cursor: pointer; }
            .price-display { margin-top: 20px; display: none; }
            .was-price { text-decoration: line-through; color: #777; font-size: 16px; }
            .now-price { color: #de1c24; font-size: 32px; font-weight: bold; margin: 5px 0; }
            .badge { background: #de1c24; color: white; padding: 4px 10px; font-size: 12px; font-weight: bold; border-radius: 3px; display: inline-block; margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <div class="tag">
            <h3 style="color:#0071dc; margin-top:0;">Electronic Pricing Query</h3>
            <input type="text" id="scanId" class="input-box" placeholder="Scan or Type Item ID (e.g., 2001)">
            <button onclick="fetchPrice()" class="btn">Query Base Engine</button>

            <div id="display" class="price-display">
                <div id="badge" class="badge">ROLLDOWN</div>
                <div id="itemName" style="font-weight:bold; font-size:16px;"></div>
                <div id="wasSection" class="was-price"></div>
                <div id="nowSection" class="now-price"></div>
            </div>
        </div>
        <script>
            async function fetchPrice() {
                const id = document.getElementById('scanId').value;
                const res = await fetch(`/api/price/${id}`);
                const data = await res.json();
                const display = document.getElementById('display');

                if(data.status === "success") {
                    display.style.display = "block";
                    document.getElementById('itemName').innerText = data.name;

                    if(data.on_clearance) {
                        document.getElementById('badge').style.display = "inline-block";
                        document.getElementById('wasSection').innerText = "Was: $" + data.original_price;
                        document.getElementById('nowSection').innerText = "NOW: $" + data.current_price;
                    } else {
                        document.getElementById('badge').style.display = "none";
                        document.getElementById('wasSection').innerText = "";
                        document.getElementById('nowSection').innerText = "Price: $" + data.original_price;
                    }
                } else {
                    alert("System tracking error: Item not logged.");
                }
            }
        </script>
    </body>
    </html>
    """
