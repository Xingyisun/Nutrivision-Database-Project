import streamlit as st
from pymongo import MongoClient
import plotly.express as px
import plotly.graph_objects as go

# MongoDB Client Setup
client = MongoClient('localhost', 27017)
db_odd = client['oddIdFoods']
db_even = client['evenIdFoods']

def get_database(item_id):
    """Determine the correct database based on the length of the ID."""
    return db_odd if len(item_id) % 2 else db_even

def get_collection(db):
    """Retrieve the 'foods' collection."""
    return db['foods']

def fetch_all_food_names():
    """Fetch all unique food names from both databases."""
    collection_odd = get_collection(db_odd)
    collection_even = get_collection(db_even)
    food_names_odd = collection_odd.distinct("name")
    food_names_even = collection_even.distinct("name")
    return list(set(food_names_odd + food_names_even))

all_food_names = fetch_all_food_names()

st.title('Nutrition Search System')

# Create tabs for different functionalities
tab1, tab2 = st.tabs(["Search and Display Nutrition", "Compare Foods"])

with tab1:
    search_name = st.text_input('Enter a food name to search:')
    search_button = st.button('Search')
    
    if search_button and search_name:
        regex_query = f"\\b{search_name}\\b"  # Matches whole word only
        collection_odd = get_collection(db_odd)
        collection_even = get_collection(db_even)
        results_odd = list(collection_odd.find({"name": {"$regex": regex_query, "$options": "i"}}))
        results_even = list(collection_even.find({"name": {"$regex": regex_query, "$options": "i"}}))
        results = results_odd + results_even
    
        if results:
            st.write(f"Found {len(results)} items matching your search.")
            for result in results:
                with st.expander(f"{result['name']} (Click to expand)"):
                    st.write(f"ID: {result.get('id', 'No ID provided')}")
                    st.write(f"Description: {result.get('description', 'No description provided.')}")
                    if 'nutrition-per-100g' in result:
                        nutrition_data = {k: v for k, v in result['nutrition-per-100g'].items() if k != 'energy'}
                        if 'sodium' in nutrition_data:
                            nutrition_data['sodium'] = nutrition_data['sodium'] / 1000  # Adjust unit for sodium

                        # Define colors for each nutrient
                        color_map = {
                            "protein": "#636EFA",
                            "fat": "#EF553B",
                            "saturated-fat": "#00CC96",
                            "carbohydrate": "#AB63FA",
                            "sugars": "#FFA15A",
                            "dietary-fibre": "#19D3F3",
                            "sodium": "#FF6692"
                        }

                        # Create pie chart
                        fig = px.pie(
                            names=list(nutrition_data.keys()),
                            values=list(nutrition_data.values()),
                            title='Nutritional Composition per 100g (g)',
                            color_discrete_map=color_map
                        )
                        fig.update_traces(textinfo='percent+label')
                        st.plotly_chart(fig, use_container_width=True)
                    if 'tags' in result:
                        st.text(f"Tags: {', '.join(result['tags'])}")
        else:
            st.warning('No matching food items found.')

with tab2:
    # Implement the comparison functionality here
    st.subheader("Compare Nutritional Values of Two Foods")
    # This part would include functionality to select two foods and display their comparative data
    # Dynamic selection based on input
    filter_query = st.text_input('Type to filter:', '')
    filtered_foods = [food for food in all_food_names if filter_query.lower() in food.lower()]

    food1_name = st.selectbox('Select the first food:', filtered_foods, index=0 if filtered_foods else None)
    food2_name = st.selectbox('Select the second food:', filtered_foods, index=1 if len(filtered_foods) > 1 else None)

    def fetch_food_data(food_name):
        """Fetch food data based on the food name."""
        db_odd = client['oddIdFoods']
        db_even = client['evenIdFoods']
        food_data_odd = db_odd['foods'].find_one({"name": {"$regex": f'^{food_name}$', "$options": "i"}})
        food_data_even = db_even['foods'].find_one({"name": {"$regex": f'^{food_name}$', "$options": "i"}})
        
        if not food_data_odd and not food_data_even:
            print(f"No data found for {food_name} in either database.")
        else:
            which_db = 'oddIdFoods' if food_data_odd else 'evenIdFoods'
            print(f"Data found for {food_name} in {which_db}.")
        
        return food_data_odd if food_data_odd else food_data_even


    # Fetch and compare the data
    if st.button('Compare Nutrition'):
        food1_data = fetch_food_data(food1_name)
        food2_data = fetch_food_data(food2_name)
        
        if food1_data and food2_data:
            nutrients = ['protein', 'fat', 'saturated-fat', 'carbohydrate', 'sugars', 'dietary-fibre', 'sodium']
            food1_nutrition = {nutrient: food1_data['nutrition-per-100g'].get(nutrient, 0) for nutrient in nutrients}
            food2_nutrition = {nutrient: food2_data['nutrition-per-100g'].get(nutrient, 0) for nutrient in nutrients}

            # Normalize sodium values
            food1_nutrition['sodium'] /= 1000
            food2_nutrition['sodium'] /= 1000

            # Create the comparison chart
            fig = go.Figure(data=[
                go.Bar(name=food1_name, x=list(food1_nutrition.keys()), y=list(food1_nutrition.values())),
                go.Bar(name=food2_name, x=list(food2_nutrition.keys()), y=list(food2_nutrition.values()))
            ])
            fig.update_layout(barmode='group', title='Nutritional Comparison per 100g (g)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning('Could not retrieve data for one or both of the foods.')

