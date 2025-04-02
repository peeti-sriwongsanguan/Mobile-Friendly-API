#client-code.py
import requests
import json

# Replace with your API server's address
# If testing on the same device, use 127.0.0.1
# If testing from another device on the same network, use the IP address of the device running the server
API_URL = "http://192.168.1.100:5007"  # Example IP - replace with your actual server IP


def get_all_items():
    """Fetch all items from the API"""
    response = requests.get(f"{API_URL}/items")
    if response.status_code == 200:
        return response.json()['items']
    else:
        print(f"Error: {response.status_code}")
        return []


def add_new_item(title, description=""):
    """Add a new item to the database via the API"""
    data = {
        "title": title,
        "description": description
    }

    response = requests.post(
        f"{API_URL}/items",
        headers={"Content-Type": "application/json"},
        data=json.dumps(data)
    )

    if response.status_code == 201:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None


def get_item_by_id(item_id):
    """Fetch a specific item by ID"""
    response = requests.get(f"{API_URL}/items/{item_id}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None


def delete_item(item_id):
    """Delete an item by ID"""
    response = requests.delete(f"{API_URL}/items/{item_id}")
    if response.status_code == 200:
        return True
    else:
        print(f"Error: {response.status_code}")
        return False


def get_all_forms():
    """Fetch all forms from the API"""
    response = requests.get(f"{API_URL}/forms")
    if response.status_code == 200:
        return response.json()['forms']
    else:
        print(f"Error: {response.status_code}")
        return []


def get_form(form_id):
    """Fetch a specific form by ID"""
    response = requests.get(f"{API_URL}/forms/{form_id}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None


def add_form(form_data):
    """Add a new form with items to the database"""
    response = requests.post(
        f"{API_URL}/forms",
        headers={"Content-Type": "application/json"},
        data=json.dumps(form_data)
    )

    if response.status_code == 201:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def update_form(form_id, form_data):
    """Update an existing form"""
    response = requests.put(
        f"{API_URL}/forms/{form_id}",
        headers={"Content-Type": "application/json"},
        data=json.dumps(form_data)
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def delete_form(form_id):
    """Delete a form"""
    response = requests.delete(f"{API_URL}/forms/{form_id}")
    if response.status_code == 200:
        return True
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False


if __name__ == "__main__":
    # Example: Add a new material request form
    new_form = {
        "vehicle_registration": "กข 1234",
        "date": "2025-04-02",
        "requester_name": "สมชาย ใจดี",
        "recipient_name": "สมหญิง รักสงบ",
        "items": [
            {
                "item_number": 1,
                "material_description": "ปูนซีเมนต์",
                "material_code": "C-001",
                "quantity": 5,
                "unit": "ถุง"
            },
            {
                "item_number": 2,
                "material_description": "ทรายละเอียด",
                "material_code": "S-002",
                "quantity": 2,
                "unit": "คิว"
            }
        ]
    }

    print("Adding a new form...")
    result = add_form(new_form)
    if result:
        form_id = result['id']
        print(f"Added form with ID: {form_id}")

        # Get the form we just added
        print(f"\nGetting form {form_id}...")
        form = get_form(form_id)
        if form:
            print(f"Form: {form['requester_name']} - {form['date']}")
            print("Items:")
            for item in form['items']:
                print(f"- {item['material_description']}: {item['quantity']} {item['unit']}")

        # Update the form
        print("\nUpdating the form...")
        updated_form = new_form.copy()
        updated_form["recipient_name"] = "วิชัย ขยันงาน"
        updated_form["items"].append({
            "item_number": 3,
            "material_description": "เหล็กเส้น",
            "material_code": "ST-003",
            "quantity": 10,
            "unit": "เส้น"
        })

        update_result = update_form(form_id, updated_form)
        if update_result:
            print("Form updated successfully")

    # Get all forms
    print("\nGetting all forms...")
    forms = get_all_forms()
    for form in forms:
        print(f"- Form {form['id']}: {form['requester_name']} ({form['date']})")
        print(f"  Items: {len(form['items'])}")