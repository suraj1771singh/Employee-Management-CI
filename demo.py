import mysql.connector
from mysql.connector import Error
import hashlib
from tabulate import tabulate


def establish_connection():
    """Establishes a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="employee_management_system",
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None


def generate_password_hash(password):
    """Hashes the provided password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def validate_employee_login(cursor, email, password):
    """Validates employee credentials and returns the employee data."""
    hashed_password = generate_password_hash(password)
    query = "SELECT * FROM employees WHERE email = %s AND password = %s"
    cursor.execute(query, (email, hashed_password))
    return cursor.fetchone()


def fetch_employee_by_id(cursor, emp_id):
    """Fetches and displays employee details by their ID in a tabular format using 'tabulate'."""
    query = "SELECT * FROM employees WHERE id = %s"
    cursor.execute(query, (emp_id,))
    return cursor.fetchone()


def fetch_all_employees(cursor):
    """Fetches and displays all employees in a tabular format using 'tabulate'."""
    query = "SELECT * FROM employees"
    cursor.execute(query)
    return cursor.fetchall()


def update_employee_details(
    cursor, emp_id, name=None, salary=None, dept=None, password=None
):
    """Updates employee information with any of the provided fields."""
    fields_to_update = []
    params = []

    if name:
        fields_to_update.append("name = %s")
        params.append(name)
    if salary:
        fields_to_update.append("salary = %s")
        params.append(salary)
    if dept:
        fields_to_update.append("dept = %s")
        params.append(dept)
    if password:
        fields_to_update.append("password = %s")
        params.append(generate_password_hash(password))

    params.append(emp_id)

    if fields_to_update:
        query = f"UPDATE employees SET {', '.join(fields_to_update)} WHERE id = %s"
        cursor.execute(query, tuple(params))
        connection.commit()


def register_new_employee(cursor, email, name, password, salary, dept):
    """Registers a new employee into the database."""
    hashed_password = generate_password_hash(password)
    query = "INSERT INTO employees (email, name, password, salary, dept) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (email, name, hashed_password, salary, dept))
    connection.commit()


def remove_employee(cursor, emp_id):
    """Removes an employee from the database."""
    query = "DELETE FROM employees WHERE id = %s"
    cursor.execute(query, (emp_id,))
    connection.commit()


def admin_panel(cursor):
    while True:
        print("\n" + "=" * 40)
        print(" " * 10 + "ADMIN DASHBOARD")
        print("=" * 40)
        print("1. Register Employee")
        print("2. View Employee Details")
        print("3. List All Employees")
        print("4. Update Employee Details")
        print("5. Delete Employee")
        print("6. Reset Admin Password")
        print("7. Logout")
        print("=" * 40)

        choice = input("Enter your option: ").strip()

        if choice == "1":
            print("\n" + "=" * 40)
            print(" " * 10 + "ADD NEW EMPLOYEE")
            print("=" * 40)
            email = input("Enter email: ")
            name = input("Enter name: ")
            password = input("Enter password: ")
            salary = float(input("Enter salary: "))
            dept = input("Enter department: ")
            register_new_employee(cursor, email, name, password, salary, dept)
            print("New employee added successfully!")

        elif choice == "2":
            emp_id = int(input("\nEnter employee ID: "))
            employee = fetch_employee_by_id(cursor, emp_id)
            if employee:
                # Define the headers
                headers = ["ID", "Name", "Email", "Department", "Salary"]

                # Prepare the table data
                table_data = [
                    (employee[0], employee[1], employee[2], employee[5], employee[4])
                ]

                # Print the table using tabulate
                print("\nEmployee Information:")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
            else:
                print("Employee not found.")

        elif choice == "3":
            employees = fetch_all_employees(cursor)
            if employees:
                # Define the headers
                headers = ["ID", "Name", "Email", "Department", "Salary"]

                # Prepare the table data
                table_data = [
                    (emp[0], emp[1], emp[2], emp[5], emp[4]) for emp in employees
                ]

                # Print the table using tabulate
                print("\nList of Employees:")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
            else:
                print("No employees in the system.")

        elif choice == "5":
            emp_id = int(input("\nEnter employee ID to remove: "))
            employee = fetch_employee_by_id(cursor, emp_id)
            if employee:
                remove_employee(cursor, emp_id)
                print("Employee removed successfully.")
            else:
                print("Employee not found. Cannot remove.")

        elif choice == "4":
            emp_id = int(input("\nEnter employee ID to modify: "))
            employee = fetch_employee_by_id(cursor, emp_id)
            if employee:
                print("\n" + "=" * 40)
                print(" " * 10 + "MODIFY EMPLOYEE DETAILS")
                print("=" * 40)
                name = input("Enter new name (press Enter to skip): ")
                salary = input("Enter new salary (press Enter to skip): ")
                dept = input("Enter new department (press Enter to skip): ")
                password = input("Enter new password (press Enter to skip): ")
                update_employee_details(cursor, emp_id, name, salary, dept, password)
                print("Employee details successfully updated.")
            else:
                print("Employee not found. Cannot modify details.")

        elif choice == "6":
            new_password = input("\nEnter new admin password: ")
            confirm_password = input("Confirm new password: ")
            if new_password == confirm_password:
                with open("admin_credentials.txt", "w") as f:
                    f.write(generate_password_hash(new_password))
                print("Admin password reset successfully!")
            else:
                print("Passwords do not match. Try again.")

        elif choice == "7":
            print("Logging out...")
            break

        else:
            print("Invalid input. Please try again.")
        print("=" * 40)


def employee_panel(cursor, emp_id):
    """Employee operations panel with improved console view."""
    while True:
        print("\n" + "=" * 40)
        print(" " * 10 + "EMPLOYEE DASHBOARD")
        print("=" * 40)
        print("1. View Profile")
        print("2. Update Profile")
        print("3. Logout")
        print("=" * 40)

        choice = input("Select an option: ").strip()

        if choice == "1":
            print("\n" + "=" * 40)
            print(" " * 10 + "VIEW PROFILE")
            print("=" * 40)
            employee = fetch_employee_by_id(cursor, emp_id)
            if employee:
                # Define the headers
                headers = ["ID", "Name", "Email", "Department", "Salary"]

                # Prepare the table data
                table_data = [
                    (employee[0], employee[1], employee[2], employee[5], employee[4])
                ]

                # Print the table using tabulate
                print("\nEmployee Information:")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
            else:
                print("Employee not found.")

        elif choice == "2":
            print("\n" + "=" * 40)
            print(" " * 10 + "MODIFY PROFILE")
            print("=" * 40)
            name = input("Update name (press Enter to skip): ")
            salary = input("Update salary (press Enter to skip): ")
            dept = input("Update department (press Enter to skip): ")
            password = input("Update password (press Enter to skip): ")
            update_employee_details(cursor, emp_id, name, salary, dept, password)
            print("Profile updated successfully!")

        elif choice == "3":
            print("Logging out...")
            break

        else:
            print("Invalid option. Please try again.")
        print("=" * 40)


def main():
    global connection
    connection = establish_connection()
    if connection:
        cursor = connection.cursor()

        print("Select your role:")
        print("1. Admin")
        print("2. Employee")

        choice = input("Enter your choice (1 or 2): ").strip()

        if choice == "1":
            try:
                with open("admin_credentials.txt", "r") as f:
                    admin_password_hash = f.read().strip()

                admin_password = input("Enter admin password: ")
                if generate_password_hash(admin_password) == admin_password_hash:
                    admin_panel(cursor)
                else:
                    print("Incorrect admin password.")
            except FileNotFoundError:
                print("Admin credentials file not found. Reset the password.")

        elif choice == "2":
            email = input("Enter your email: ")
            password = input("Enter your password: ")
            employee = validate_employee_login(cursor, email, password)
            if employee:
                emp_id = employee[0]
                print("Welcome, Employee!")
                employee_panel(cursor, emp_id)
            else:
                print("Invalid login credentials.")

        else:
            print("Invalid choice. Please enter 1 for Admin or 2 for Employee.")

        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
