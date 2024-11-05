import streamlit as st
import pandas as pd
import numpy as np
import csv
from email.message import EmailMessage
import ssl
import smtplib

# Dictionary to store roll numbers and emails
roll_email_dict = {}

# Section to upload CSV containing roll numbers and emails
st.markdown("### Upload Student Roll Number and their respective email in CSV file")
uploaded_csv = st.file_uploader("Choose a CSV file", accept_multiple_files=False)

# Process the uploaded CSV file
if uploaded_csv:
    bytes_data = uploaded_csv.read().decode("utf-8")  # Decode bytes to string
    st.write("Filename:", uploaded_csv.name)
    
    # Parse CSV data
    csv_reader = csv.reader(bytes_data.splitlines())
    next(csv_reader)  # Skip header row

    # Store roll number and email in dictionary
    for row in csv_reader:
        roll_no = row[1]  # Assuming Roll No is the second column (index 1)
        email = row[2]    # Assuming Email is the third column (index 2)
        roll_email_dict[roll_no] = email

# Display the dictionary
st.write("Roll Number and Email Dictionary:")
st.write(roll_email_dict)

# Section to download the results CSV file
st.markdown("### You can download the results as a CSV file.")
with open("backend/responses.csv", "rb") as file:
    btn = st.download_button(
            label="Download Results",
            data=file,
            file_name="responses.csv",
            mime="text/csv"
          )

# Function to load data
def load_data(csv_file):
    df = pd.read_csv(csv_file)
    return df

# Title for rating distribution analysis
st.title('Rating Distribution Analysis')

# Load responses CSV data
df = load_data('backend/responses.csv')

# Count occurrences of each rating
ratings_counts = pd.DataFrame({'Rating': range(1, 11), 'Count': 0})
for rating in range(1, 11):
    ratings_counts.loc[rating - 1, 'Count'] = (df['Rating'] == rating).sum()

# Display bar chart
st.write('### Distribution of Ratings')
st.bar_chart(ratings_counts.set_index('Rating'))

# Email forwarding section
stud_len = len(roll_email_dict)
saved_time = (4 * stud_len) / 60 - stud_len / 60
st.markdown(f"### WOW! You just saved {saved_time:.2f} hours of manual work!🎉")

st.markdown('### Send feedback to students based on the results.')
send = st.button("Send Feedback through Email")

if send:
    email_sender = "gradewiseai@gmail.com"
    email_password = "aefk ncoz kajz abtc"
    subject = "Your Essay feedback"

    # Load responses from the CSV file
    responses = {}
    with open('backend/responses.csv', 'r') as responses_file:
        response_reader = csv.DictReader(responses_file)
        for row in response_reader:
            responses[row['Roll Number']] = {
                'rating': row['Rating'],
                'feedback': row['Feedback']
            }

    # Sending feedback emails
    for roll_number, email_receiver in roll_email_dict.items():
        if roll_number in responses:
            rating = responses[roll_number]['rating']
            feedback = responses[roll_number]['feedback']
            body = (
                f"The evaluation of your essay has been completed.\n"
                f"Your Rating for the essay is: {rating}/10\n"
                f"Feedback: {feedback}\n\n"
                f"Thank you!\nNote: This is an automated email. Please do not reply."
            )
        else:
            body = (
                "There hasn't been any submission of essays, so the rating is provided as 0."
            )

        # Prepare email message
        em = EmailMessage()
        em["From"] = email_sender
        em["To"] = email_receiver
        em["Subject"] = subject
        em.set_content(body)

        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())

    st.success('Emails sent successfully to all students.', icon="✅")
 