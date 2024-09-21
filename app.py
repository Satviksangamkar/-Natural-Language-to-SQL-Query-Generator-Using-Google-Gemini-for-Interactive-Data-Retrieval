from dotenv import load_dotenv
import streamlit as st
import os
import sqlite3
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Generative AI key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Google Gemini Model and provide queries as response
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([prompt[0], question])
    return response.text.strip()  # Remove leading/trailing whitespace

# Function to retrieve query results from the database
def read_sql_query(sql, db):
    """
    Executes a SQL query on the specified database and returns the results.
    """
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    print(f"Executing SQL: {sql}")  # Debug line
    try:
        cur.execute(sql)
        rows = cur.fetchall()
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return []
    finally:
        conn.close()
    return rows

# Function to create and populate the STUDENT table
def setup_database():
    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()

    # Create the STUDENT table if it doesn't exist
    table_info = """
    CREATE TABLE IF NOT EXISTS STUDENT (
        NAME VARCHAR(255),
        CLASS VARCHAR(255),
        SECTION VARCHAR(255),
        MARKS INT
    );
    """
    cursor.execute(table_info)

    # Insert records if table is empty
    cursor.execute("SELECT COUNT(*) FROM STUDENT")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO STUDENT VALUES ('Krish', 'Data Science', 'A', 90)")
        cursor.execute("INSERT INTO STUDENT VALUES ('Sudhanshu', 'Data Science', 'B', 100)")
        cursor.execute("INSERT INTO STUDENT VALUES ('Darius', 'Data Science', 'A', 86)")
        cursor.execute("INSERT INTO STUDENT VALUES ('Vikash', 'DEVOPS', 'A', 50)")
        cursor.execute("INSERT INTO STUDENT VALUES ('Dipesh', 'DEVOPS', 'A', 35)")
        conn.commit()

    conn.close()

# Define your prompt for the model
prompt = [
    """
    You are an expert in converting English questions to SQL queries!
    The SQL database has the name STUDENT and has the following columns - NAME, CLASS, 
    SECTION, MARKS. For example:
    - Example 1: How many entries of records are present? 
      SQL command: SELECT COUNT(*) FROM STUDENT;
    - Example 2: Tell me all the students studying in Data Science class? 
      SQL command: SELECT * FROM STUDENT WHERE CLASS='Data Science';
    The SQL code should not have ``` at the beginning or end and should not include the word "SQL" in the output.
    """
]

# Streamlit App UI
st.set_page_config(page_title="Gemini SQL Query App")
st.header("Gemini App To Retrieve SQL Data")

# User input for questions
question = st.text_input("Input your question:", key="input")
submit = st.button("Ask the question")

# Setup the database (create table and insert data)
setup_database()

# If submit is clicked
if submit:
    if question.strip():  # Ensure the question is not empty
        response = get_gemini_response(question, prompt)
        print(f"Generated SQL: {response}")  # Debugging
        result = read_sql_query(response, "student.db")
        
        # Display the results
        st.subheader("The Response is:")
        if result:
            for row in result:
                st.write(row)  # Display each row in Streamlit
        else:
            st.write("No results found or an error occurred.")
    else:
        st.warning("Please enter a valid question.")
