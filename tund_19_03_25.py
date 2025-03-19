import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# Создание БД и таблицы, если она не существует
def setup_database():
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            director TEXT,
            release_year INTEGER,
            genre TEXT,
            duration INTEGER,
            rating REAL,
            language TEXT,
            country TEXT,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()

setup_database()

# Валидация данных
def validate_data():
    title = entries["Pealkiri"].get()
    release_year = entries["Aasta"].get()
    rating = entries["Reiting"].get()

    if not title:
        tk.messagebox.showerror("Viga", "Pealkiri on kohustuslik!")
        return False
    if not release_year.isdigit():
        tk.messagebox.showerror("Viga", "Aasta peab olema arv!")
        return False
    if rating and (not rating.replace('.', '', 1).isdigit() or not (0 <= float(rating) <= 10)):
        tk.messagebox.showerror("Viga", "Reiting peab olema vahemikus 0 kuni 10!")
        return False

    return True

# Функция для вставки данных в БД
def insert_data():
    if not validate_data():
        return

    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO movies (title, director, release_year, genre, duration, rating, language, country, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        entries["Pealkiri"].get(),
        entries["Režissöör"].get(),
        entries["Aasta"].get(),
        entries["Žanr"].get(),
        entries["Kestus"].get(),
        entries["Reiting"].get(),
        entries["Keel"].get(),
        entries["Riik"].get(),
        entries["Kirjeldus"].get()
    ))

    conn.commit()
    conn.close()

    messagebox.showinfo("Edu", "Andmed sisestati edukalt!")
    clear_entries()
    load_data_from_db(tree)

# Очистка всех полей
def clear_entries():
    for entry in entries.values():
        entry.delete(0, tk.END)

# Загрузка данных из БД в таблицу
def load_data_from_db(tree, search_query=""):
    for item in tree.get_children():
        tree.delete(item)

    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()

    if search_query:
        cursor.execute("SELECT title, director, release_year, genre, duration, rating, language, country, description FROM movies WHERE title LIKE ?", ('%' + search_query + '%',))
    else:
        cursor.execute("SELECT title, director, release_year, genre, duration, rating, language, country, description FROM movies")

    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", "end", values=row)

    conn.close()

# Поиск по названию
def on_search():
    search_query = search_entry.get()
    load_data_from_db(tree, search_query)

# Окно для добавления данных
def add_data():
    global entries
    add_window = tk.Toplevel(root)
    add_window.title("Filmi andmete sisestamine")

    labels = ["Pealkiri", "Režissöör", "Aasta", "Žanr", "Kestus", "Reiting", "Keel", "Riik", "Kirjeldus"]
    entries = {}

    for i, label in enumerate(labels):
        tk.Label(add_window, text=label).grid(row=i, column=0, padx=10, pady=5)
        entry = tk.Entry(add_window, width=40)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[label] = entry

    submit_button = tk.Button(add_window, text="Sisesta andmed", command=insert_data)
    submit_button.grid(row=len(labels), column=0, columnspan=2, pady=20)

# Основное окно
root = tk.Tk()
root.title("Filmid")

# Фрейм для поиска
search_frame = tk.Frame(root)
search_frame.pack(pady=10)

search_label = tk.Label(search_frame, text="Otsi filmi pealkirja järgi:")
search_label.pack(side=tk.LEFT)

search_entry = tk.Entry(search_frame)
search_entry.pack(side=tk.LEFT, padx=10)

search_button = tk.Button(search_frame, text="Otsi", command=on_search)
search_button.pack(side=tk.LEFT)

# Кнопка добавления фильма
open_button = tk.Button(root, text="Lisa andmeid", command=add_data)
open_button.pack(pady=20)

# Фрейм для таблицы с прокруткой
frame = tk.Frame(root)
frame.pack(pady=20, fill=tk.BOTH, expand=True)
scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Создание таблицы
tree = ttk.Treeview(frame, yscrollcommand=scrollbar.set,
                    columns=("title", "director", "year", "genre", "duration", "rating", "language", "country", "description"),
                    show="headings")
tree.pack(fill=tk.BOTH, expand=True)

# Связывание прокрутки с таблицей
scrollbar.config(command=tree.yview)

# Настройки колонок
columns = {
    "title": "Pealkiri",
    "director": "Režissöör",
    "year": "Aasta",
    "genre": "Žanr",
    "duration": "Kestus",
    "rating": "Reiting",
    "language": "Keel",
    "country": "Riik",
    "description": "Kirjeldus"
}

for col, header in columns.items():
    tree.heading(col, text=header)
    tree.column(col, width=100)

tree.column("title", width=150)
tree.column("description", width=200)

# Загрузка данных в таблицу
load_data_from_db(tree)

# Запуск Tkinter
root.mainloop()
