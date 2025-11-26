from db_connection import create_connection, close_connection
from mysql_env import get_event_data_as_lists


def display_data():
    """
    Se conecta a la Base de Datos y muestra los eventos como listas.
    """
    conn = create_connection()
    if not conn:
        return

    try:
        ids, event_names, event_dates, locations, organizers, attendee_counts = get_event_data_as_lists(conn)

        print("--- Listas de Datos de Eventos ---")
        print(f"IDs:              {ids}")
        print(f"Nombres Evento:   {event_names}")
        print(f"Fechas:           {event_dates}")
        print(f"Ubicaciones:      {locations}")
        print(f"Organizadores:    {organizers}")
        print(f"Asistentes:       {attendee_counts}")

    finally:
        close_connection(conn)

if __name__ == "__main__":
    display_data()