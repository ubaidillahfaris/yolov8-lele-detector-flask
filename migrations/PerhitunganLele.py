from database.connection import get_connection
def upgrade():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        create_table_query = '''
        CREATE TABLE perhitungan_leles (
            id SERIAL PRIMARY KEY,
            tanggal DATE NOT NULL,
            grade VARCHAR(100),
            jumlah INTEGER NOT NULL,
            harga DECIMAL DEFAULT 0.0,
            file_path VARCHAR,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        );
        '''
        
        cursor.execute(create_table_query)
        conn.commit()
        
        print("Table created successfully.")
        
        cursor.close()
        conn.close()
    except Exception as error:
        print(f"Error creating table: {error}")

def downgrade():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        drop_table_query = 'DROP TABLE IF EXISTS perhitungan_leles;'
        
        cursor.execute(drop_table_query)
        conn.commit()
        
        print("Table dropped successfully.")
        
        cursor.close()
        conn.close()
    except Exception as error:
        print(f"Error dropping table: {error}")