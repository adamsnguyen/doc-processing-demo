import streamlit as st
import requests
import json
import base64
import logging
import datetime
from num2words import num2words

# Set up logging
logging.basicConfig(level=logging.ERROR)

def main():
    st.title("Document Processor")

    # File uploader
    uploaded_file = st.file_uploader("Choose a Word document", type="docx")

    # Form inputs
    client = st.text_input("Client Name")
    date = st.date_input("Date: ", datetime.date.today())
    notice_period = st.slider("Select number of days:", 
                 min_value=0, 
                 max_value=365, 
                 value=60, 
                 step=1)
    notice_period_text = num2words(notice_period)
    notice_period_string = f"{notice_period_text} ({notice_period})"

    if st.button("Process Document"):
        if uploaded_file is not None:
            try:
                # Read file contents
                file_contents = uploaded_file.read()

                # Encode file contents to base64
                encoded_file = base64.b64encode(file_contents).decode()

                # Prepare data for API
                if isinstance(date, datetime.date):
                    date_str = date.isoformat()
                else:
                    date_str = str(date)

                data = {
                    "body": json.dumps({
                        "file": encoded_file,
                        "placeholders": {
                            "{{NAME}}": client,
                            "{{DATE}}": date_str,
                            "{{NOTICE_PERIOD}}": str(notice_period_string)
                        }
                    })
                }

                st.json(data)

                # Get API key from Streamlit secrets
                api_key = st.secrets["API_KEY"]

                # Send request to API Gateway
                api_url = "https://iv7g55y423.execute-api.us-east-2.amazonaws.com/test/process-doc-replace"
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": api_key
                }
                
                st.write("Sending request with headers:", headers)
                st.write("To URL:", api_url)

                response = requests.post(api_url, json=data, headers=headers)
                
                st.write("Response status code:", response.status_code)
                st.write("Response headers:", dict(response.headers))

                if response.status_code == 200:
                    response_data = response.json()
                    if 'body' in response_data:
                        try:
                            body_content = json.loads(response_data['body'])
                            if 'processed_document' in body_content:
                                processed_doc = base64.b64decode(body_content['processed_document'])
                                st.download_button(
                                    label="Download Processed Document",
                                    data=processed_doc,
                                    file_name=f"{client}_processed_document.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                )
                            else:
                                st.error("Processed document not found in the response body")
                                st.write("Debug info:", body_content)
                        except json.JSONDecodeError:
                            st.error("Error decoding JSON in response body")
                            st.write("Debug info:", response_data['body'])
                    else:
                        st.error("Body not found in the response")
                        st.write("Debug info:", response_data)

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
