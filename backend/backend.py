import zipfile
import os
import shutil
import PyPDF2
from io import BytesIO
from . import gemini, vision
from docx import Document

def analysis(file, ques_key):
    # Define the path to the zip file
    if ques_key.name.endswith('.pdf'):
        # Read the file content from the UploadedFile object as bytes
        pdf_bytes = ques_key.read()
        
        # Use BytesIO to treat the file as a binary stream
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        
        # Initialize an empty string to store the extracted text
        extracted_text = ''
        
        # Iterate through each page of the PDF
        for page in pdf_reader.pages:
            extracted_text += page.extract_text()
        
        # Do something with the extracted text from the PDF
        
    elif ques_key.name.endswith('.docx'):
        # You may need to use `python-docx` for DOCX processing.
        doc = Document(BytesIO(ques_key.read()))
        
        extracted_text = ''
        for paragraph in doc.paragraphs:
            extracted_text += paragraph.text
        
        # Do something with the extracted text from the DOCX
    
    else:
        print("Unsupported file format. Only PDF and DOCX files are supported.")


    if len(file) == 1 and file[0].type == "application/x-zip-compressed":
        zip_file_path = file[0]
        # print("Zip : ", zip_file_path)
        
        # Define the folder where you want to extract the PDF files
        output_folder = "backend/extracted_folder"

        # Ensure the output folder exists, if not, create it
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Extract the contents of the zip file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(output_folder)

        # Move folders to the output folder
        for foldername in os.listdir(output_folder):
            folder_path = os.path.join(output_folder, foldername)
            if os.path.isdir(folder_path):
                shutil.move(folder_path, os.path.join(output_folder, foldername))

        # Iterate through the folders in the output folder
        for foldername in os.listdir(output_folder):
            folder_path = os.path.join(output_folder, foldername)
            f_name = foldername
            print(f_name)
            if os.path.isdir(folder_path):
                written = ''
                for filename in sorted(os.listdir(folder_path), key=lambda x: int(x.split('.')[0])):
                    image_path = os.path.join(folder_path, filename)
                    written += vision.image_to_text(image_path) + '\n'
                print(f_name,":",written)
                gemini.prompt(written, f_name, extracted_text)
            else:
                print("No answers")