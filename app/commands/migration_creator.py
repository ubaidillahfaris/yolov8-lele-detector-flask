from database.connection import get_connection
import re

def create_migration_table(name):
    table_name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    migration_path = f"migrations/{name.lower()}.py"

    migration_template = f"""from database.connection import get_connection
def upgrade():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        create_table_query = '''
        CREATE TABLE {table_name}s (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            age INTEGER NOT NULL
        );
        '''
        
        cursor.execute(create_table_query)
        conn.commit()
        
        print("Table created successfully.")
        
        cursor.close()
        conn.close()
    except Exception as error:
        print(f"Error creating table: {{error}}")

def downgrade():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        drop_table_query = 'DROP TABLE IF EXISTS {table_name}s;'
        
        cursor.execute(drop_table_query)
        conn.commit()
        
        print("Table dropped successfully.")
        
        cursor.close()
        conn.close()
    except Exception as error:
        print(f"Error dropping table: {{error}}")"""

    with open(migration_path, 'w') as migration_file:
        migration_file.write(migration_template)
    print(f"Migration created: {migration_path}")



def migrate_table(name):
    migration_name = name
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Import file migrasi
        migration_module = __import__(f"migrations.{migration_name}", fromlist=['upgrade'])
        
        # Jalankan operasi downgrade
        migration_module.upgrade()
        
        cursor.close()
        conn.close()
    except Exception as error:
        print(f"Error rolling back: {error}")

def rollback_table(name):
    migration_name = name
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Import file migrasi
        migration_module = __import__(f"migrations.{migration_name}", fromlist=['downgrade'])
        
        # Jalankan operasi downgrade
        migration_module.downgrade()
        
        cursor.close()
        conn.close()
    except Exception as error:
        print(f"Error rolling back: {error}")

