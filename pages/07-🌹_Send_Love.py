import streamlit as st 


from streamlit_extras.add_vertical_space import add_vertical_space
from pyairtable import Table
from datetime import date
from pyairtable.formulas import match
import http, urllib 
from datetime import datetime 

if st.session_state.get("role") not in ["Imad","Chloe"]:
    st.error("You need to be logged in to access this page.")
    st.stop()


def send_push(name,message):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
        "token": st.secrets['PUSHOVER_TOKEN'],
        "user": st.secrets[f'PUSHOVER_USER_{name.upper()}'],
        "message": message,
    }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()
    return conn 


User = st.session_state.get('role')
if User == "Imad":
    other = 'Chloe'
else:
    other = "Imad"

st.title('Send Love')

cols = st.columns(6)

with cols[0]:
    hug = st.button('Send a Hug')
    if hug:
        send_push(other,f'{User} sent you a Hug 🫂')
with cols[1]: 
    kiss = st.button('Send a Kiss')
    if kiss:
        send_push(other,f'{User} sent you a Kiss 💋')
with cols[2]:
    vibes = st.button('Send Good Vibes')
    if vibes:
        send_push(other,f'{User} sent you Good Vibes 🌈')
with cols[3]:
    missing = st.button('Send an I Miss You')
    if missing:
        send_push(other,f'{User} misses you 😞')
with cols[4]:
    attention = st.button('Ask for Attention')
    if attention:
        send_push(other,f'{User} would like some attention 🛎')
with cols[5]:
    cuddles = st.button('Ask for Cuddles')
    if cuddles:
        send_push(other,f'{User} would like some cuddles please 🧸')


table = Table(st.secrets['AIRTABLE_API_KEY'],st.secrets["AIRTABLE_BASE_ID"],"Letters")
with st.form('long note',clear_on_submit=True):
    st.write('## Write a longer note')
    text = st.text_area(label='Enter Note')
    submit = st.form_submit_button('Send 💌')
    if submit:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        table.create({'Time':dt_string,'Author':User,'Letter':text})
        send_push(other,f'{User} sent you a letter 💌')


st.write('# Our Correspondance')

all_letters = table.all() 
st.markdown(
            """
            <style>
    @font-face {
    font-family: 'Tangerine';
    font-style: normal;
    font-weight: 400;
    src: url(https://fonts.gstatic.com/s/tangerine/v12/IurY6Y5j_oScZZow4VOxCZZM.woff2) format('woff2');
    unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
    }

        html, body, [class*="css"]  {
        font-family: 'Tangerine';
        font-size: 48px;
        }
        </style>

        """,
            unsafe_allow_html=True,
        )
for i in all_letters:
    st.write(f"### From {i['fields']['Author']} at {i['fields']['Time']}")
    st.write(i['fields']['Letter'])

