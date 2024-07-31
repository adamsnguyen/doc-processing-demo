import streamlit as st
import requests
import json
import base64
import logging

# Set up logging
logging.basicConfig(level=logging.ERROR)

def main():
    st.title("Document Processor")

    # File uploader
    uploaded_file = st.file_uploader("Choose a Word document", type="docx")

    # Form inputs
    client = st.text_input("Client Name")
    amount = st.text_input("Amount")

    if st.button("Process Document"):
        if uploaded_file is not None:
            try:
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
                api_url = "https://iv7g55y423.execute-api.us-east-2.amazonaws.com/test/process-doc-replace"
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": api_key
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
                    error_message = f"Error processing document: Status code {response.status_code}"
                    st.error(error_message)
                    logging.error(f"{error_message} - Response: {response.text}")
                    st.write("Debug info:", response.text)

            except requests.RequestException as e:
                error_message = f"Network error occurred: {str(e)}"
                st.error(error_message)
                logging.error(error_message)

            except json.JSONDecodeError as e:
                error_message = f"Error decoding JSON response: {str(e)}"
                st.error(error_message)
                logging.error(error_message)

            except Exception as e:
                error_message = f"An unexpected error occurred: {str(e)}"
                st.error(error_message)
                logging.error(error_message)
                st.exception(e)  # This will display the full traceback

        else:
            st.error("Please upload a document before processing.")

if __name__ == "__main__":
    main()
