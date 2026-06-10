"""
Build the small fictional gallery SQLite databases used by the hosting UI.

The script is idempotent: each generated gallery file is recreated from
scratch, while the existing medical.db class database is left untouched.
"""

import os
import sqlite3


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "databases")


def recreate_database(filename):
    os.makedirs(DATABASE_DIR, exist_ok=True)
    db_path = os.path.join(DATABASE_DIR, filename)
    if os.path.exists(db_path):
        os.remove(db_path)
    return sqlite3.connect(db_path)


def seed_pokemon():
    conn = recreate_database("pokemon.db")
    conn.execute(
        """
        CREATE TABLE Pokemon (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            hp INTEGER NOT NULL
        )
        """
    )
    conn.executemany(
        "INSERT INTO Pokemon (id, name, type, hp) VALUES (?, ?, ?, ?)",
        [
            (1, "Sprigbat", "Leaf", 42),
            (2, "Emberling", "Fire", 39),
            (3, "Pebblor", "Rock", 55),
            (4, "Mistfin", "Water", 46),
            (5, "Voltkit", "Electric", 35),
            (6, "Frostowl", "Ice", 48),
            (7, "Glowmole", "Light", 44),
            (8, "Shadillo", "Shadow", 52),
        ],
    )
    conn.commit()
    conn.close()


def seed_gym():
    conn = recreate_database("gym.db")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(
        """
        CREATE TABLE Members (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            year_group TEXT NOT NULL
        );

        CREATE TABLE Classes (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            coach TEXT NOT NULL,
            capacity INTEGER NOT NULL
        );

        CREATE TABLE Bookings (
            id INTEGER PRIMARY KEY,
            member_id INTEGER NOT NULL,
            class_id INTEGER NOT NULL,
            booking_date TEXT NOT NULL,
            FOREIGN KEY (member_id) REFERENCES Members (id),
            FOREIGN KEY (class_id) REFERENCES Classes (id)
        );
        """
    )
    conn.executemany(
        "INSERT INTO Members (id, name, year_group) VALUES (?, ?, ?)",
        [
            (1, "Mina", "Year 11"),
            (2, "Jonas", "Year 12"),
            (3, "Leila", "Year 13"),
            (4, "Omar", "Year 12"),
        ],
    )
    conn.executemany(
        "INSERT INTO Classes (id, name, coach, capacity) VALUES (?, ?, ?, ?)",
        [
            (1, "Morning Spin", "Avery", 12),
            (2, "Core Strength", "Riley", 10),
            (3, "Yoga Flow", "Sam", 14),
        ],
    )
    conn.executemany(
        "INSERT INTO Bookings (id, member_id, class_id, booking_date) VALUES (?, ?, ?, ?)",
        [
            (1, 1, 1, "2026-06-01"),
            (2, 2, 1, "2026-06-01"),
            (3, 3, 2, "2026-06-02"),
            (4, 4, 3, "2026-06-03"),
            (5, 1, 3, "2026-06-03"),
        ],
    )
    conn.commit()
    conn.close()


def seed_music():
    conn = recreate_database("music.db")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(
        """
        CREATE TABLE Artists (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            genre TEXT NOT NULL
        );

        CREATE TABLE Songs (
            id INTEGER PRIMARY KEY,
            artist_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            duration_seconds INTEGER NOT NULL,
            FOREIGN KEY (artist_id) REFERENCES Artists (id)
        );
        """
    )
    conn.executemany(
        "INSERT INTO Artists (id, name, genre) VALUES (?, ?, ?)",
        [
            (1, "North Arcade", "Synth Pop"),
            (2, "The Paper Planets", "Indie Rock"),
            (3, "Luna Vale", "Acoustic"),
        ],
    )
    conn.executemany(
        "INSERT INTO Songs (id, artist_id, title, duration_seconds) VALUES (?, ?, ?, ?)",
        [
            (1, 1, "Signal Lights", 214),
            (2, 1, "Late Bus", 188),
            (3, 2, "Folded Maps", 232),
            (4, 2, "Balcony Weather", 205),
            (5, 3, "Small Hours", 196),
        ],
    )
    conn.commit()
    conn.close()


def seed_library():
    conn = recreate_database("library.db")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(
        """
        CREATE TABLE Books (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT NOT NULL
        );

        CREATE TABLE Members (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            tutor_group TEXT NOT NULL
        );

        CREATE TABLE Loans (
            id INTEGER PRIMARY KEY,
            book_id INTEGER NOT NULL,
            member_id INTEGER NOT NULL,
            loan_date TEXT NOT NULL,
            returned INTEGER NOT NULL,
            FOREIGN KEY (book_id) REFERENCES Books (id),
            FOREIGN KEY (member_id) REFERENCES Members (id)
        );
        """
    )
    conn.executemany(
        "INSERT INTO Books (id, title, author, genre) VALUES (?, ?, ?, ?)",
        [
            (1, "The Clockwork Orchard", "Nia Bell", "Adventure"),
            (2, "Harbour of Clouds", "Tomas Reed", "Fantasy"),
            (3, "A Field Guide to Mars", "Maya Chen", "Science Fiction"),
            (4, "The Last Lighthouse", "Iris Vale", "Mystery"),
        ],
    )
    conn.executemany(
        "INSERT INTO Members (id, name, tutor_group) VALUES (?, ?, ?)",
        [
            (1, "Amal", "11A"),
            (2, "Bea", "12C"),
            (3, "Chen", "13B"),
        ],
    )
    conn.executemany(
        "INSERT INTO Loans (id, book_id, member_id, loan_date, returned) VALUES (?, ?, ?, ?, ?)",
        [
            (1, 1, 1, "2026-05-20", 0),
            (2, 3, 2, "2026-05-22", 1),
            (3, 4, 3, "2026-05-25", 0),
        ],
    )
    conn.commit()
    conn.close()


def main():
    seed_pokemon()
    seed_gym()
    seed_music()
    seed_library()
    print("Seeded gallery databases: pokemon.db, gym.db, music.db, library.db")


if __name__ == "__main__":
    main()
