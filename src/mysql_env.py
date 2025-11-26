from db_connection import create_connection, close_connection


def drop_table(conn):
    """Elimina la tabla events si existe."""
    query = "DROP TABLE IF EXISTS events;"
    cursor = conn.cursor()
    cursor.execute(query)
    print("Table 'events' dropped if it existed.")
    cursor.close()


def create_table(conn):
    query = """
        CREATE TABLE IF NOT EXISTS events (
            id INT AUTO_INCREMENT PRIMARY KEY,
            event_name VARCHAR(100) NOT NULL,
            event_date DATE NOT NULL,
            location VARCHAR(100),
            organizer VARCHAR(100),
            attendee_count INT
        ) ENGINE=InnoDB;
    """
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    print("Table 'events' created.")
    cursor.close()


def insert_event(conn, event_name, event_date, location, organizer, attendee_count):
    query = "INSERT INTO events (event_name, event_date, location, organizer, attendee_count) VALUES (%s, %s, %s, %s, %s)"
    cursor = conn.cursor()
    cursor.execute(query, (event_name, event_date, location, organizer, attendee_count))
    conn.commit()
    print(f"Added event: {event_name}")
    cursor.close()


def get_events(conn):
    query = "SELECT id, event_name, event_date, location, organizer, attendee_count FROM events;"
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    print("\nEvent List:")
    for r in rows:
        print(f"ID: {r[0]} | Evento: {r[1]} | Fecha: {r[2]} | Lugar: {r[3]} | Organiza: {r[4]} | Asistentes: {r[5]}")
    cursor.close()


def get_event_data_as_lists(conn):
    """
    Recupera los datos de los eventos y los devuelve en 6 listas separadas.
    """
    query = "SELECT id, event_name, event_date, location, organizer, attendee_count FROM events;"
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    ids = []
    event_names = []
    event_dates = []
    locations = []
    organizers = []
    attendee_counts = []

    for row in rows:
        ids.append(row[0])
        event_names.append(row[1])
        event_dates.append(row[2])
        locations.append(row[3])
        organizers.append(row[4])
        attendee_counts.append(row[5])

    cursor.close()
    return ids, event_names, event_dates, locations, organizers, attendee_counts


def main():
    conn = create_connection()
    if conn:
        drop_table(conn)  
        create_table(conn)

        insert_event(conn, "Conferencia de IA", "2024-10-15", "Centro de Convenciones", "Tech Corp", 500)
        insert_event(conn, "Festival de Música", "2024-11-20", "Parque Central", "Music Fest Org", 100)
        insert_event(conn, "Feria del Libro", "2024-09-05", "Biblioteca Nacional", "Cultura Gto", 200)
        insert_event(conn, "Maratón Anual", "2024-10-22", "Calles de la Ciudad", "Deportes City", 500)
        insert_event(conn, "Exposición de Arte", "2025-01-15", "Museo de Arte Moderno", "Galería Central", 300)
        insert_event(conn, "Hackathon 2024", "2024-11-30", "Universidad Tecnológica", "Code Hub", 150)

        get_events(conn)
        close_connection(conn)


if __name__ == "__main__":
    main()