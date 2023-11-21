import streamlit as st
import openai
import requests
import pandas
import os.path
import os
import time
from pathlib import Path


# ------------------------------------------FUNCTIONS CODE-------------------------------------


# making a class chatbot
class Chatbot:
    def get_seo_optimized_words(self, messages):
        try:
            # my_api_key = os.getenv("OPEN AI KEY")
            my_api_key = os.getenv(st.secrets["API_KEY"])
            client = openai.OpenAI(api_key=my_api_key)
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=300,
            )
            return response.choices[0].message.content

        except Exception as e:
            # Handle the exception here
            st.info(f"An error occurred: Make sure that all urls in text file are valid image urls")
            st.warning(f"ERROR Details are \n: {e}")
            return None


# using requests to check if url is valid or not
def is_valid_image_url(url):
    try:
        response = requests.head(url)
        content_type = response.headers.get('content-type')
        if content_type:
            return True
        else:
            return False
    except requests.RequestException:
        return False

# get user download path
def get_download_path():
    # Get the user's home directory
    home_dir = Path.home()

    # find the desktop directory based on the operating system
    download_dir = home_dir / 'Downloads'
    return download_dir

# save csv file in download path
def save_csv():
    download_path = f"{get_download_path()}\Alt-text-CSV-Files"
    # writing data to csv file
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    file_name = f"{date}-{formatted_time}.csv"
    full_directory = f"{download_path}\{file_name}"
    st.session_state.mydataframe.to_csv(full_directory, index=False)
    st.info("Find downloads in C:/Users/<User_name>/Downloads/Alt-text-CSV-Files")
    st.success(f"'{file_name}' Downloaded successfully.")
    st.dataframe(st.session_state.mydataframe)
    st.stop()


# -----------------------------Main File Code----------------------------

# finding current date and time
current_time = time.localtime()
day = time.strftime("%d", current_time)
month = time.strftime("%B", current_time)
year = time.strftime("%Y", current_time)
date = f"{day}-{month}-{year}"
formatted_time = time.strftime("%I-%M-%S %p", current_time)

links_input = ""
url_list = []
response_list = []

# i is used to confirm that invalid url are present or not for one time
i = 1
# j is used to calculate invalid number of urls
j = 0

# download button state
button_clicked = False

csv_file_name = date

st.markdown(f"<p style='text-align: right;'>{date}</p>", unsafe_allow_html=True)
st.markdown(f"<h1 style='text-align: center;'>✨Image to SEO keywords✨</h1>", unsafe_allow_html=True)

links_input = st.text_area("Enter links here", placeholder="Enter URLs here one URL per row")

# creating input box styling
st.markdown(f"""
<style>
.stTextArea{{
        position: fixed;
        bottom: 0;
        z-index: 3;
        }}
    </style>
""", unsafe_allow_html=True)

txt_file = st.file_uploader("Upload a text file", type="txt")

# # story dataframe in
if "mydataframe" not in st.session_state:
    st.session_state.mydataframe = []

button_clicked = st.button("Download as CSV")
if button_clicked:
        save_csv()
        button_clicked = False

if button_clicked is False:
    # Split the string into a list of urls by a \n character
    if links_input != "" and not txt_file:
        url_list = links_input.split("\n")
    elif txt_file:
        # finding file name of text file
        file_name = txt_file.name
        # removing extension (.txt) from file name
        file_name = file_name[:-4]
        st.info(f"Text File name : {file_name}")

        urls_byte_format = txt_file.read()

        # converting bytes to string
        urls_string = urls_byte_format.decode('utf-8')

        # handling for when text file is empty
        if urls_string is not None:
            # Split the string into a list of urls by a \n character
            url_list = urls_string.split("\n")
    else:
        st.info("Enter some links each link per row and press Ctrl + Enter")

    if len(url_list) != 0:
        # message dictionary to be passed to openai
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Pretend you're an SEO expert. Create an optimized alt text for the image. Write it as plain text no inverted commas or any heading. Don't Explain any extra thing and always split one images alt by other via \n\n",
                    },
                ],
            }
        ]
        # appending new links to message dictionary so that can be send to gpt-4-vision-model
        for url in url_list:
            # this functions uses requests library to check if image urls are valid or not
            check_image = is_valid_image_url(url)
            if check_image:
                new_dict = {
                    "type": "image_url",
                    "image_url": {
                        "url": f"{url}",
                    },
                }
                messages[0]['content'].append(new_dict)


            else:
                if i == 1:
                    st.info(f"Some of the urls are not valid image urls")
                    i += 1

                # checking how many urls are invalid
                j += 1

        st.warning(f"{j} URLs are Invalid and not converted to alt text")

        # making a chatbot object and calling function to return alt texts
        seo_bot = Chatbot()

        response = seo_bot.get_seo_optimized_words(messages)

        if response:
            response_list = response.split("\n\n")

        if response_list and url_list:
            data = [url_list, response_list]
            dataframe = pandas.DataFrame(data).transpose()
            # mentioning name of columns
            dataframe.columns = ["Image URL", "Suggested alt text"]

            # displaying dataframe on screen
            st.dataframe(dataframe)

            # backup dataframe
            st.session_state.mydataframe = dataframe


