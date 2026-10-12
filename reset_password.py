
import sqlite3
from getpass import getpass
from pathlib import Path
from werkzeug.security import generate_password_hash

DATABASE = Path(__file__).resolve().parent / "tasknet.db"


def main():
    if not DATABASE.exists():
        print("TaskNet database was not found. Check this file is beside app.py.")
        return

    email = input("Enter your TaskNet account email: ").strip().lower()

    if not email or "@" not in email:
        print("Please enter a valid email address.")
        return

    with sqlite3.connect(DATABASE) as db:
        user = db.execute(
            "SELECT id, name FROM users WHERE email = ? COLLATE NOCASE",
            (email,)
        ).fetchone()

        if user is None:
            print("No TaskNet account was found with that email.")
            return

        print(f"Account found for: {user[1]}")

        password = getpass("Enter your new password (minimum 12 characters): ")
        confirmation = getpass("Confirm your new password: ")

        if len(password) < 12:
            print("Password must be at least 12 characters.")
            return

        if password != confirmation:
            print("The passwords do not match.")
            return

        password_hash = generate_password_hash(password)

        db.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (password_hash, user[0])
        )

    print("Password updated successfully! You can now log in to TaskNet.")


if __name__ == "__main__":
    main()
