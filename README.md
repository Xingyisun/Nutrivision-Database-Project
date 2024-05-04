
# NutriVision: Nutrition Database Management System

## Description
NutriVision is a comprehensive nutrition management system designed to facilitate access to detailed nutritional information for various foods. It provides tools for data insertion, retrieval, modification, and visualization through a user-friendly web interface built with Streamlit and powered by MongoDB.

## Files 
1. **Database setup**: db.py
2. **Manager UI**: manager.py
3. **user UI**: user.py
4. **Preload Dataset**: food.json

## Features
- **Data Distribution**: Automatically partitions data into two collections based on item ID criteria, optimizing query performance.
- **Interactive UI for Management**: Allows users to perform CRUD (Create, Read, Update, Delete) operations on food data entries.
- **Nutritional Data Visualization**: Uses Plotly to create dynamic pie charts and bar graphs to visually compare nutritional contents.
- **Search and Compare**: Enables users to search for food items and compare their nutritional values interactively.

## Prerequisites
- Python 3.x
- MongoDB
- AWS EC2 (for deployment)
- Python packages: pymongo, streamlit, plotly

## Setup
1. **MongoDB Installation**:
   - Install MongoDB.

2. **Install Python Dependencies**:
   - Ensure all required packages are installed:
     ```
     pip install pymongo streamlit plotly
     ```

## Installation
1. **Clone the Repository**:
   ```
   git clone https://github.com/Xingyisun/Nutrivision-Database-Project.git
   ```
## Database setup
   - python3 db.py
## Running the Streamlit app (make sure it is not blocked by the firewall)
1. **Start the MongoDB service** (if running MongoDB locally).
2. **Launch the Streamlit application**:
   - For the database manager:
     ```
     streamlit run manager.py
     ```
   - For the user interface:
     ```
     streamlit run user.py
     ```

