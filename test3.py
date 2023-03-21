# Just a test

import requests
from bs4 import BeautifulSoup
import streamlit as st


url = st.text_input("Paste your inews url here please", "inews url")

response = requests.get(url)
webpage = response.content
soup = BeautifulSoup(webpage, "html.parser")

headline = soup.find("h1").get_text()
standfirst = soup.find("h2").get_text()
copy_mess = soup.find_all("p")

copy = "".join(p for p in copy_mess)

# copy = [line.get_text() for line in copy_mess if line.attrs["class"][0] == 'ssrcss-1q0x1qg-Paragraph' and line.parent.attrs["class"] != ("ssrcss-1f3bvyz-Stack e1y4nx260" or "ssrcss-y7krbn-Stack e1y4nx260")]
# last_updated_time = soup.find(attrs={'property':'og:updated_time'})
article = copy_mess

st.title(headline)
st.header(standfirst)
st.markdown(copy) 