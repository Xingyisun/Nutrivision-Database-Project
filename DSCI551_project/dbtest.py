import json
from pymongo import MongoClient

# Setup MongoDB connection
client = MongoClient('localhost', 27017)
db_odd = client['oddIdFoods']
db_even = client['evenIdFoods']

def setup_unique_index(collection):
    """ Setup a unique index on the 'id' field to prevent duplicates """
    collection.create_index("id", unique=True)

def unicode_partition(data):
    """ Determine if the sum of Unicode values of the id is odd or even """
    return sum(ord(char) for char in data['id']) % 2

def load_data():
    # Load data from the JSON file
    with open('data/food.json', 'r') as file:
        foods = json.load(file)

    # Setup unique index for both collections to prevent duplicate ids
    setup_unique_index(db_odd.foods)
    setup_unique_index(db_even.foods)

    # Insert data into the appropriate database
    for food in foods:
        try:
            if unicode_partition(food) == 0:
                db_even.foods.insert_one(food)
            else:
                db_odd.foods.insert_one(food)
        except Exception as e:
            print(f"Failed to insert {food['id']}: {str(e)}")

    print("Data has been loaded into the databases.")

if __name__ == "__main__":
    load_data()
