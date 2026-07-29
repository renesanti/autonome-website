import sqlite3

DB_NAME = "trending.db"


def init_ecommerce_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Foreign keys inschakelen in SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Klanten tabel
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            first_name TEXT,
            last_name TEXT,
            billing_address TEXT,
            billing_city TEXT,
            billing_postal_code TEXT,
            billing_country TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Producten tabel
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            price_cents INTEGER NOT NULL, -- Prijs in centen (999 = €9.99)
            currency TEXT DEFAULT 'EUR',
            file_path TEXT, -- Pad naar het PDF-bestand
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Orders tabel
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT UNIQUE NOT NULL, -- bijv. ORD-2026-0001
            customer_id INTEGER NOT NULL,
            order_status TEXT DEFAULT 'new', -- new, processing, completed, cancelled
            payment_status TEXT DEFAULT 'pending', -- pending, paid, failed, refunded
            payment_method TEXT, -- stripe, mollie, paypal
            payment_provider_id TEXT, -- ID van Stripe/Mollie transactie
            total_amount_cents INTEGER NOT NULL,
            download_token TEXT UNIQUE, -- Unieke token voor veilige PDF download
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)

    # 4. Orderregels tabel
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            product_sku TEXT NOT NULL,
            product_name TEXT NOT NULL,
            unit_price_cents INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # Voeg direct het eerste product toe (De AI Company Blueprint PDF)
    cursor.execute("""
        INSERT OR IGNORE INTO products (sku, name, description, price_cents, currency, file_path)
        VALUES (
            'PDF-AI-BIZ-01',
            'The Autonomous AI Company Playbook',
            'How to build, automate and scale a 100% AI-run business from A to Z.',
            999,
            'EUR',
            'downloads/ai_company_blueprint.pdf'
        )
    """)

    conn.commit()
    conn.close()
    print(
        "E-commerce tabellen succesvol aangemaakt en PDF product toegevoegd!"
    )


if __name__ == "__main__":
    init_ecommerce_tables()
