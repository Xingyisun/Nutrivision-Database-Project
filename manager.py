import streamlit as st
from pymongo import MongoClient
import json

# MongoDB connection setup
client = MongoClient('localhost', 27017)

# Streamlit UI
st.title('Database Manager UI')

def get_database(item_id):
    # Calculate the sum of Unicode values of all characters in the ID
    unicode_sum = sum(ord(char) for char in item_id)
    # Determine the database based on whether the sum of Unicode values is odd or even
    db_name = 'evenIdFoods' if unicode_sum % 2 == 0 else 'oddIdFoods'
    return client[db_name]


# Function to retrieve or create a collection based on the id.
def get_collection(db):
    # Directly return the 'foods' collection from the given database
    return db['foods']


# Create tabs for different functionalities
tab1, tab2, tab3, tab4 = st.tabs(["Insert Data", "Insert Multiple with JSON", "Delete Data", "Modify Data"])

# Insert Functionality for Single Record
with tab1:
    with st.form("insert_form"):
        st.subheader('Insert Data')
        id_to_insert = st.text_input("ID for Insert")
        name_to_insert = st.text_input("Name for Insert")
        nutrition_info_fields = ['Energy', 'Protein', 'Fat', 'Saturated Fat', 'Carbohydrate', 'Sugars', 'Dietary Fibre', 'Sodium']
        nutrition_info = {field: st.number_input(f"{field} per 100g", min_value=0.0, format="%.2f") for field in nutrition_info_fields}
        tags = st.text_input("Tags (comma-separated)")
        submit_insert = st.form_submit_button('Insert Data')

    if submit_insert and id_to_insert:
        nutrition_data = {key.lower().replace(' ', '-'): value for key, value in nutrition_info.items()}
        tags_list = tags.split(',') if tags else []
        db = get_database(id_to_insert)
        collection = get_collection(db)
        document = {
            "id": id_to_insert,
            "name": name_to_insert,
            "nutrition-per-100g": nutrition_data,
            "tags": tags_list
        }
        try:
            # Check if the ID already exists
            if collection.find_one({"id": id_to_insert}):
                st.error('This item already exists in the database.')
            else:
                result = collection.insert_one(document)
                st.success(f'Data inserted successfully with ID: {result.inserted_id}')
        except Exception as e:
            st.error(f'Failed to insert data: {str(e)}')



with tab2:
    with st.form("bulk_insert_form"):
        st.subheader('Bulk Insert Data (JSON format)')
        bulk_data_to_insert = st.text_area("Paste JSON data here", height=300)
        submit_bulk_insert = st.form_submit_button('Insert Multiple Data')

    if submit_bulk_insert and bulk_data_to_insert:
        try:
            # Parse the JSON data
            entries = json.loads(bulk_data_to_insert)
            if isinstance(entries, list) and all(isinstance(entry, dict) for entry in entries):
                # Initialize counters or logs for where entries are inserted
                inserted_odd = []
                inserted_even = []
                
                for entry in entries:
                    db = get_database(entry['id'])
                    collection = db['foods']  # Directly using the 'foods' collection
                    result = collection.insert_one(entry)  # Insert each entry as a dictionary
                    
                    # Log insertion details
                    if db.name == 'oddIdFoods':
                        inserted_odd.append(result.inserted_id)
                    else:
                        inserted_even.append(result.inserted_id)
                    
                    if result.acknowledged:
                        st.success(f'Data inserted successfully for entry with ID: {result.inserted_id} in database: {db.name}')
                    else:
                        st.error('Failed to insert data')

                # Optional: Summarize where entries went
                st.info(f'Entries inserted into oddIdFoods: {len(inserted_odd)}')
                st.info(f'Entries inserted into evenIdFoods: {len(inserted_even)}')

            else:
                st.error("Invalid JSON format. Please enter a list of dictionaries.")
        except json.JSONDecodeError:
            st.error("Invalid JSON. Please correct it and try again.")



# Delete Functionality
with tab3:
    with st.form("delete_form"):
        st.subheader('Delete Data')
        id_to_delete = st.text_input("ID to Delete")
        submit_delete = st.form_submit_button('Delete Data')

    if submit_delete and id_to_delete:
        db = get_database(id_to_delete)
        collection = get_collection(db)
        result = collection.delete_many({'id': id_to_delete})
        if result.deleted_count > 0:
            st.success(f'{result.deleted_count} document(s) deleted successfully')
        else:
            st.warning('No documents found with the provided ID')

# Modify Functionality
with tab4:
    with st.form("update_form"):
        st.subheader('Modify Data')
        id_to_modify = st.text_input("ID to Modify")
        new_name = st.text_input("New Name")
        new_energy = st.number_input("New Energy per 100g", min_value=0, key='energy')
        new_protein = st.number_input("New Protein per 100g", min_value=0.0, format="%.2f", key='protein')
        new_fat = st.number_input("New Fat per 100g", min_value=0.0, format="%.2f", key='fat')
        new_saturated_fat = st.number_input("New Saturated Fat per 100g", min_value=0.0, format="%.2f", key='saturated_fat')
        new_carbohydrate = st.number_input("New Carbohydrate per 100g", min_value=0.0, format="%.2f", key='carbohydrate')
        new_sugars = st.number_input("New Sugars per 100g", min_value=0.0, format="%.2f", key='sugars')
        new_dietary_fibre = st.number_input("New Dietary Fibre per 100g", min_value=0.0, format="%.2f", key='dietary_fibre')
        new_sodium = st.number_input("New Sodium per 100g", min_value=0, key='sodium')
        new_tags = st.text_input("New Tags (comma-separated)", key='tags')
        submit_update = st.form_submit_button('Modify Data')

    if submit_update and id_to_modify:
        new_nutrition_info = {
            "energy": new_energy,
            "protein": new_protein,
            "fat": new_fat,
            "saturated-fat": new_saturated_fat,
            "carbohydrate": new_carbohydrate,
            "sugars": new_sugars,
            "dietary-fibre": new_dietary_fibre,
            "sodium": new_sodium
        }
        new_tags_list = new_tags.split(',') if new_tags else []
        db = get_database(id_to_modify)
        collection = get_collection(db)
        update_data = {
            "name": new_name,
            "nutrition-per-100g": new_nutrition_info,
            "tags": new_tags_list
        }
        result = collection.update_one(
            {'id': id_to_modify},
            {'$set': update_data}
        )
        if result.modified_count > 0:
            st.success(f'Data modified successfully for {result.modified_count} document(s)')
        else:
            st.warning('No modifications made. Check if the ID is correct or the new data is the same as old data.')
