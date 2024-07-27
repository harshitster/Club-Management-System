import os
import psycopg2
import logging

# YEAR in fest - year
# ENUM in team - temp_type
# ENUM in participant - gender
# ENUM in visitor - gender
# ENUM in item - type

dir_path = os.path.join(os.path.dirname(__file__), 'db-store')
os.makedirs(dir_path, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(dir_path, 'db-init.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w'
)

host = os.environ['POSTGRES_HOST']
port = int(os.environ['POSTGRES_PORT'])
user = os.environ['POSTGRES_USER']
password = os.environ['POSTGRES_PASSWORD']
dbname = os.environ['POSTGRES_DB']

logging.info(f"Connecting to host: {host}, port: {port}, user: {user}, dbname: {dbname}")

try:    
    conn = psycopg2.connect(
        host=host, 
        port=port,
        user=user,
        password=password,
        dbname=dbname
    )

    logging.info("Connection - Successful")

    cur = conn.cursor()

    statements = [
        """
        CREATE TABLE university(
            uni_id VARCHAR(5),
            university_name VARCHAR(25),
            city VARCHAR(25),
            state VARCHAR(25),
            PRIMARY KEY (uni_id)
        );
        """,
        
        "SELECT create_distributed_table('university', 'uni_id');",
        
        """
        CREATE TABLE fest(
            fest_id VARCHAR(5),
            fest_name VARCHAR(25) NOT NULL,
            year DATE,
            head_teamID VARCHAR(5),
            uni_id VARCHAR(5),
            PRIMARY KEY (uni_id, fest_id),
            FOREIGN KEY (uni_id) REFERENCES university(uni_id)
        );
        """,
        
        "SELECT create_distributed_table('fest', 'uni_id');",
        
        """
        CREATE TABLE team(
            team_id VARCHAR(5),
            team_name VARCHAR(25) NOT NULL,
            team_type INT,
            fest_id VARCHAR(5),
            uni_id VARCHAR(5),
            PRIMARY KEY (uni_id, team_id),
            FOREIGN KEY (uni_id, fest_id) REFERENCES fest(uni_id, fest_id)
        );
        """,
        
        "SELECT create_distributed_table('team', 'uni_id');",
        
        """
        ALTER TABLE fest ADD CONSTRAINT fest_head_name FOREIGN KEY(uni_id, head_teamID) REFERENCES team(uni_id, team_id);
        """,
        
        """
        CREATE TABLE member(
            mem_id VARCHAR(5),
            mem_name VARCHAR(25) NOT NULL,
            DOB DATE,
            super_memID VARCHAR(5),
            team_id VARCHAR(5),
            uni_id VARCHAR(5),
            PRIMARY KEY (uni_id, mem_id),
            FOREIGN KEY (uni_id, super_memID) REFERENCES member(uni_id, mem_id),
            FOREIGN KEY (uni_id, team_id) REFERENCES team(uni_id, team_id)
        );
        """,
        
        "SELECT create_distributed_table('member', 'uni_id');",
        
        """
        CREATE TABLE event(
            event_id VARCHAR(5),
            event_name VARCHAR(25) NOT NULL,
            building VARCHAR(15),
            floor VARCHAR(10),
            room_no INT,
            price DECIMAL(10,2),
            team_id VARCHAR(5),
            uni_id VARCHAR(5),
            PRIMARY KEY (uni_id, event_id),
            CHECK (price <= 1500.00),
            FOREIGN KEY (uni_id, team_id) REFERENCES team(uni_id, team_id) ON DELETE CASCADE
        );
        """,
        
        "SELECT create_distributed_table('event', 'uni_id');",
        
        """
        CREATE TABLE event_conduction(
            event_id VARCHAR(5),
            date_of_conduction DATE,
            uni_id VARCHAR(5),
            PRIMARY KEY(uni_id, event_id, date_of_conduction),
            FOREIGN KEY (uni_id, event_id) REFERENCES event(uni_id, event_id)
        );
        """,
        
        "SELECT create_distributed_table('event_conduction', 'uni_id');",
        
        """
        CREATE TABLE participant(
            SRN VARCHAR(10),
            name VARCHAR(25) NOT NULL,
            department VARCHAR(20),
            semester INT,
            gender INT,
            uni_id VARCHAR(5),
            PRIMARY KEY (uni_id, SRN),
            FOREIGN KEY (uni_id) REFERENCES university(uni_id)
        );
        """,
        
        "SELECT create_distributed_table('participant', 'uni_id');",
        
        """
        CREATE TABLE visitor(
            SRN VARCHAR(10),
            name VARCHAR(25),
            age INT,
            gender INT,
            uni_id VARCHAR(5),
            PRIMARY KEY (uni_id, SRN, name),
            FOREIGN KEY (uni_id, SRN) REFERENCES participant(uni_id, SRN)
        );
        """,
        
        "SELECT create_distributed_table('visitor', 'uni_id');",
        
        """
        CREATE TABLE registration(
            event_id VARCHAR(5),
            SRN VARCHAR(10),
            registration_id VARCHAR(5) NOT NULL,
            uni_id VARCHAR(5),
            PRIMARY KEY (uni_id, event_id, SRN),
            FOREIGN KEY (uni_id, event_id) REFERENCES event(uni_id, event_id),
            FOREIGN KEY (uni_id, SRN) REFERENCES participant(uni_id, SRN)
        );
        """,
        
        "SELECT create_distributed_table('registration', 'uni_id');",
        
        """
        CREATE TABLE stall(
            stall_id VARCHAR(5),
            name VARCHAR(25) NOT NULL,
            fest_id VARCHAR(5),
            uni_id VARCHAR(5),
            PRIMARY KEY (uni_id, stall_id),
            FOREIGN KEY (uni_id, fest_id) REFERENCES fest(uni_id, fest_id)
        );
        """,
        
        "SELECT create_distributed_table('stall', 'uni_id');",
        
        """
        CREATE TABLE item(
            name VARCHAR(25),
            type INT,
            uni_id VARCHAR(5),
            PRIMARY KEY (uni_id, name),
            FOREIGN KEY (uni_id) REFERENCES university(uni_id)
        );
        """,
        
        "SELECT create_distributed_table('item', 'uni_id');",  # Create Reference Table
        
        """
        CREATE TABLE stall_items(
            stall_id VARCHAR(5),
            item_name VARCHAR(25),
            price_per_unit DECIMAL(10,2),
            total_quantity INT,
            uni_id VARCHAR(5),
            PRIMARY KEY (uni_id, stall_id, item_name),
            FOREIGN KEY (uni_id, stall_id) REFERENCES stall(uni_id, stall_id),
            FOREIGN KEY (uni_id, item_name) REFERENCES item(uni_id, name)
        );
        """,
        
        "SELECT create_distributed_table('stall_items', 'uni_id');",
        
        """
        CREATE TABLE purchased(
            SRN VARCHAR(10),
            stall_id VARCHAR(5),
            item_name VARCHAR(25),
            timestamp TIMESTAMP,
            quantity INT,
            uni_id VARCHAR(5),
            PRIMARY KEY (uni_id, SRN, stall_id, item_name, timestamp),
            FOREIGN KEY (uni_id, SRN) REFERENCES participant(uni_id, SRN),
            FOREIGN KEY (uni_id, stall_id) REFERENCES stall(uni_id, stall_id),
            FOREIGN KEY (uni_id, item_name) REFERENCES item(uni_id, name)
        );
        """,
        
        "SELECT create_distributed_table('purchased', 'uni_id');"
    ]

    logging.info("Schema Implementation and Propogation to worker nodes STARTED")

    for statement in statements:
        try:
            cur.execute(statement)
        except psycopg2.Error as e:
            logging.error(f"Error executing SQL statement: {statement}\n{e}")
            conn.rollback()
            break
        else:
            logging.info(f"Executed SQL statement: {statement}")

    conn.commit()

    logging.info("Schema Implementation and Propogation to worker nodes COMPLETED")

except psycopg2.Error as e:
    logging.error(f"PostgreSQL error: {e}")

except Exception as e:
    logging.error(f"Unexpected error: {e}")

finally:
    if 'cur' in locals() and cur is not None:
        cur.close()
    if 'conn' in locals() and conn is not None:
        conn.close()

    logging.info("Connection Closed")