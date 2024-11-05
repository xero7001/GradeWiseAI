"""
At the command line, only need to run once to install the package via pip:

$ pip install google-generativeai
"""

import google.generativeai as genai
import csv
import streamlit as st
import re
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

with open('backend/responses.csv', 'w', newline='',  encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Roll Number", "Rating", "Feedback"])


# Set up the model
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

# convo = model.start_chat(history=[
# ])
# convo.send_message("What architectures are used in Gemini and ChatGPT?")
# print(convo.last.text)
def prompt(essay, rollno, reference):
    # start_time = time.time()
    print("Prompting model...")
    messages_chatgpt=[{"role": "system", "content": """You are an answer script evaluator. Your task is
                        to rate the student's answers on a scale from 1 to 10 under the "Rating" heading. 
                       The rating should be based on how closely the student's answers align with the reference 
                       answer key provided. If the student's answers are not at all related to the reference answer 
                       key, give a score of 0. Award a score of 10 if all the key points from the reference answer 
                       are covered in the student's responses. After providing the rating, offer 
                       "Feedback and Suggestions for Improvement" in clear, concise points, guiding the student 
                       on how to enhance their answers. Ensure that the feedback is constructive and directly 
                       related to the content provided in the reference answer key. Also, donot mention about
                       question paper's reference key in the feedback. Check the matching percentage of the student's
                       answers to reference answers and provide feedback accordingly.
Reference Answer Key: """ + reference + """, Student's Answer Script: """ + essay + """
"""
},
{"role": "user", "content": essay} ]
    def transform_to_gemini(messages_chatgpt):
      messages_gemini = []
      system_promt = ''
      for message in messages_chatgpt:
          if message['role'] == 'system':
              system_promt = message['content']
          elif message['role'] == 'user':
              messages_gemini.append({'role': 'user', 'parts': [message['content']]})
          elif message['role'] == 'assistant':
              messages_gemini.append({'role': 'model', 'parts': [message['content']]})
      if system_promt:
          messages_gemini[0]['parts'].insert(0, f"*{system_promt}*")  
      return messages_gemini
    messages = transform_to_gemini(messages_chatgpt)
    response = model.generate_content(messages)
    # print(response.text)
    # response_text = response.text
    response_text = re.sub(r'\*', '', response.text)


    # Extract rating and feedback
    rating_index = response_text.find("Rating: ") + len("Rating: ")
    rating_end_index = response_text.find("\n", rating_index)
    rating_str = response_text[rating_index:rating_end_index]

    # Extract numerator of fraction rating if exists
    rating = re.match(r'^\d+', rating_str).group()
    if not rating:
        rating = 0

    # Find feedback content
    feedback_start_index = response_text.find(":", rating_end_index) + 1
    feedback_content = response_text[feedback_start_index:].strip()

    print("Rating:", rating)
    print("Feedback:")
    print(feedback_content)

    with open('backend/responses.csv', 'a', newline='', encoding="utf-8") as file:
      writer = csv.writer(file)
      # print(rollno, rating, feedback_content)
      writer.writerow([rollno, rating, feedback_content])




    
