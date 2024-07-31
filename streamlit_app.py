import streamlit as st
import requests
import json
import base64

def main():
    st.title("Document Processor")

    # File uploader
    uploaded_file = st.file_uploader("Choose a Word document", type="docx")

    # Form inputs
    client = st.text_input("Client Name")
    amount = st.text_input("Amount")

    if st.button("Process Document"):
        if uploaded_file is not None:
            # Read file contents
            file_contents = uploaded_file.read()

            # Encode file contents to base64
            encoded_file = base64.b64encode(file_contents).decode()

            # Prepare data for API
            data = {
                "file": encoded_file,
                "placeholders": {
                    "client": client,
                    "amount": amount
                }
            }

            # Get API key from Streamlit secrets
            api_key = st.secrets["API_KEY"]

            # Send request to API Gateway
            api_url = "https://your-api-gateway-url/prod/process_document"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            response = requests.post(api_url, json=data, headers=headers)

            if response.status_code == 200:
                # Decode and save the processed document
                processed_doc = base64.b64decode(response.json()['body'])
                st.download_button(
                    label="Download Processed Document",
                    data=processed_doc,
                    file_name="processed_document.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            else:
                st.error("Error processing document")

if __name__ == "__main__":
    main()
