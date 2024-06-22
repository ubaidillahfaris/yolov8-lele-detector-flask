from database.connection import get_connection
def upgrade():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        create_table_query = '''
        CREATE TABLE hargas (
            id SERIAL PRIMARY KEY,
            grade VARCHAR(100) NOT NULL,
            harga DECIMAL DEFAULT 0.0,
            age INTEGER NOT NULL
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
        
        drop_table_query = 'DROP TABLE IF EXISTS hargas;'
        
        cursor.execute(drop_table_query)
        conn.commit()
        
        print("Table dropped successfully.")
        
        cursor.close()
        conn.close()
    except Exception as error:
        print(f"Error dropping table: {error}")