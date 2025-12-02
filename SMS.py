"""
Simple Student Management System (console-based)
- Uses SQLite for storage (no external DB required)
- Features: add, view, search, update, delete, export CSV, basic validation
- Python 3.7+
"""

import sqlite3
import csv
import datetime
import os
from typing import Optional

DB_FILENAME = "students.db"


def get_connection():
    return sqlite3.connect(DB_FILENAME)


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        grade TEXT,
        email TEXT,
        phone TEXT,
        address TEXT,
        created_at TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()


def add_student(name: str, age: Optional[int], gender: str, grade: str,
                email: str, phone: str, address: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO students (name, age, gender, grade, email, phone, address, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, age, gender, grade, email, phone, address, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()


def list_students(order_by: str = "id"):
    conn = get_connection()
    cur = conn.cursor()
    query = f"SELECT id, name, age, gender, grade, email, phone, address, created_at FROM students ORDER BY {order_by}"
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return rows


def search_students(keyword: str):
    conn = get_connection()
    cur = conn.cursor()
    like = f"%{keyword}%"
    cur.execute("""
    SELECT id, name, age, gender, grade, email, phone, address, created_at
    FROM students
    WHERE name LIKE ? OR email LIKE ? OR phone LIKE ? OR grade LIKE ?
    ORDER BY id
    """, (like, like, like, like))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_student(student_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, age, gender, grade, email, phone, address, created_at FROM students WHERE id = ?", (student_id,))
    row = cur.fetchone()
    conn.close()
    return row


def update_student(student_id: int, name: str, age: Optional[int], gender: str,
                   grade: str, email: str, phone: str, address: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    UPDATE students
    SET name = ?, age = ?, gender = ?, grade = ?, email = ?, phone = ?, address = ?
    WHERE id = ?
    """, (name, age, gender, grade, email, phone, address, student_id))
    conn.commit()
    conn.close()


def delete_student(student_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()


def export_csv(filename="students_export.csv"):
    rows = list_students()
    if not rows:
        return False
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "age", "gender", "grade", "email", "phone", "address", "created_at"])
        for r in rows:
            writer.writerow(r)
    return os.path.abspath(filename)


# ---------- Helpers for input & display ----------

def input_int(prompt, allow_empty=False):
    while True:
        s = input(prompt).strip()
        if allow_empty and s == "":
            return None
        try:
            return int(s)
        except ValueError:
            print("Please enter a valid integer (or leave empty).")


def print_student_row(row):
    id_, name, age, gender, grade, email, phone, address, created_at = row
    print(f"ID: {id_} | Name: {name} | Age: {age} | Gender: {gender} | Grade: {grade}")
    print(f"   Email: {email} | Phone: {phone}")
    print(f"   Address: {address}")
    print(f"   Created: {created_at}")
    print("-" * 70)


def pause():
    input("Press Enter to continue...")


# ---------- CLI Menu ----------

def menu_add():
    print("\nAdd new student")
    name = input("Name: ").strip()
    if not name:
        print("Name is required.")
        return
    age = input_int("Age (leave empty if unknown): ", allow_empty=True)
    gender = input("Gender (M/F/Other, leave empty if unknown): ").strip()
    grade = input("Grade/Class (e.g., 10, A-level): ").strip()
    email = input("Email: ").strip()
    phone = input("Phone: ").strip()
    address = input("Address: ").strip()
    add_student(name, age, gender, grade, email, phone, address)
    print("Student added successfully.")


def menu_view():
    print("\nAll students")
    rows = list_students()
    if not rows:
        print("No students found.")
    else:
        for r in rows:
            print_student_row(r)


def menu_search():
    kw = input("Enter name / email / phone / grade to search: ").strip()
    if not kw:
        print("Search keyword required.")
        return
    rows = search_students(kw)
    if not rows:
        print("No matching students found.")
    else:
        for r in rows:
            print_student_row(r)


def menu_update():
    sid = input_int("Enter student ID to update: ")
    student = get_student(sid)
    if not student:
        print("Student not found.")
        return
    print("Current info:")
    print_student_row(student)
    print("Enter new values (leave blank to keep current):")
    _, old_name, old_age, old_gender, old_grade, old_email, old_phone, old_address, _ = student

    name = input(f"Name [{old_name}]: ").strip() or old_name
    update_student(sid, name)
    print("Student updated.")


def menu_delete():
    sid = input_int("Enter student ID to delete: ")
    student = get_student(sid)
    if not student:
        print("Student not found.")
        return
    print("About to delete:")
    print_student_row(student)
    confirm = input("Type 'yes' to confirm delete: ").strip().lower()
    if confirm == "yes":
        delete_student(sid)
        print("Student deleted.")
    else:
        print("Delete cancelled.")


def menu_export():
    path = export_csv()
    if not path:
        print("No data to export.")
    else:
        print(f"Exported to: {path}")


def main_menu():
    init_db()
    menu_text = """
Student Management System
-------------------------
1) Add student
2) View all students
3) Search students
4) Update student
5) Delete student
6) Export to CSV
0) Exit
"""
    while True:
        print(menu_text)
        choice = input("Choose an option: ").strip()
        if choice == "1":
            menu_add()
            pause()
        elif choice == "2":
            menu_view()
            pause()
        elif choice == "3":
            menu_search()
            pause()
        elif choice == "4":
            menu_update()
            pause()
        elif choice == "5":
            menu_delete()
            pause()
        elif choice == "6":
            menu_export()
            pause()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main_menu()
