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
    hug = st.button(f'Send {other} a Hug 🫂')
    if hug:
        send_push(other,f'{User} sent you a Hug 🫂')
with cols[1]: 
    kiss = st.button(f'Send {other} a Kiss 💋')
    if kiss:
        send_push(other,f'{User} sent you a Kiss 💋')
with cols[2]:
    vibes = st.button(f'Send some Good Vibes🌈')
    if vibes:
        send_push(other,f'{User} sent you Good Vibes 🌈')
with cols[3]:
    missing = st.button('Send an I Miss You 😞')
    if missing:
        send_push(other,f'{User} misses you 😞')
with cols[4]:
    attention = st.button('Ask for Attention 🛎')
    if attention:
        send_push(other,f'{User} would like some attention 🛎')
with cols[5]:
    cuddles = st.button('Ask for Cuddles 🧸')
    if cuddles:
        send_push(other,f'{User} would like some cuddles please 🧸')

cols2 = st.columns(6)
with cols2[0]:
    think = st.button('Thinking about You 🥺')
    if think:
        send_push(other,f'{User} is thinking about you 🥺')
with cols2[1]:
    want = st.button('Send an I Want You 🥵')
    if want:
        send_push(other,f'{User} WANTS you rn 🥵')
with cols2[2]:
    pretty = st.button("Send a You're so pretty 😍")
    if pretty:
        send_push(other,f"{User} thinks you're pretty 😍")
with cols2[3]:
    proud = st.button("Send an I'm Proud of U 🎉")
    if proud:
        send_push(other,f"{User} is proud of you 🎉")
with cols2[4]:
    not_you = st.button("Send 'It's Not You ❤️'")
    if not_you:
        send_push(other,f"{User} wants u to know that their mood isn't bc of you ❤️")
with cols2[5]:
    hungy = st.button("Send an I'm Hungy 🍽")
    if hungy:
        send_push(other,f"{User}'s hungy... wanna go eat? 🍽")

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


with st.container():
    
    for i in all_letters:
        st.write(f"### From {i['fields']['Author']} at {i['fields']['Time']}")
        st.write(i['fields']['Letter'])

