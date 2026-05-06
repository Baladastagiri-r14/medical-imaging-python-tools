import mysql.connector


def backup_table_data(host, user, password, output_file):
    database = "Mammography"
    table_name = "REVIEWER_PATIENT"

    try:
        # 1. Connect to the database
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor()

        # 2. Fetch all data from the table
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        # 3. Open the output file
        with open(output_file, "w", encoding="utf-8") as f:
            for row in rows:
                values = []
                for val in row:
                    if val is None:
                        values.append("NULL")
                    elif isinstance(val, str):
                        escaped = val.replace("'", "''")  # Escape single quotes
                        values.append(f"'{escaped}'")
                    else:
                        values.append(str(val))
                insert_stmt = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});"
                f.write(insert_stmt + "\n")

        print(f"Backup completed successfully to '{output_file}'")

    except mysql.connector.Error as err:
        print("Error:", err)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Example usage
backup_table_data(
    host="localhost",       # change if your DB is on a different host
    user="root",            # your DB username
    password="password",    # your DB password
    output_file="REVIEWER_PATIENT_backup.sql"
)
