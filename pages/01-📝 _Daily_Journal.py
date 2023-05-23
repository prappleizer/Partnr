import streamlit as st 


from streamlit_extras.add_vertical_space import add_vertical_space
from pyairtable import Table
from datetime import date
from pyairtable.formulas import match
import http, urllib 

class Record():
    def __init__(self,api_response):
        self.id = api_response['id']
        for i in api_response['fields']:
            setattr(self,i,api_response['fields'][i])

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

def retrieve_completed_records_by_field(table,field):
    """returns a list of Record objects for entries in table which have field as empty

    Parameters
    ----------
    table : pyairtable.Table
        table to use
    field : str
        field to search

    Returns
    -------
    records
        list of Record objects matching condition.
    """
    all_rec = table.all()
    return_recs = []
    for i in all_rec:
        if field in i['fields']:
            return_recs.append(Record(i))
    return return_recs

if st.session_state.get("role") not in ["Imad","Chloe"]:
    st.error("You need to be logged in to access this page.")
    st.stop()

today = date.today()
today = today.strftime("%Y-%m-%d")
st.write(f'# Daily Questions: {today}')
add_vertical_space(4)

table = Table(st.secrets['AIRTABLE_API_KEY'],st.secrets['AIRTABLE_BASE_ID'],'Daily')

User = st.session_state.get('role')
if User == "Imad":
    other = 'Chloe'
else:
    other = "Imad"


formula = match({'Date':today})
entry = Record(table.first(formula=formula))
if hasattr(entry,f'{User}-Answer'):
    st.write("You have already answered today's Question!")
else:    
    placeholder = st.empty()
    with placeholder.form('daily-question',clear_on_submit=True):
        st.write(f'#### {entry.Question}')
        answer = st.text_area('Enter Response',value='',height=300)
        submit = st.form_submit_button("Submit")

    if submit:
        balloons = st.balloons()
        table.update(entry.id,{f"{User}-Answer":answer})
        totals = Table(st.secrets['AIRTABLE_API_KEY'],st.secrets['AIRTABLE_BASE_ID'],'Totals')
        entry2 = totals.first(formula=match({'Name':'Total-Dailys'}))
        totals.update(entry2['id'],{'Number':entry2['fields']['Number']+1})
        placeholder.empty()
        st.write('Your Response has been submitted!')
        if f'{other}-Answer' in table.get(entry.id)['fields']:
            send_push(other,f"{User} just filled out their daily journal! Check out your answers")
        else:
            send_push(other,f"{User} just filled out their daily journal! Fill out yours?")

st.divider()
st.write('## Previous Answers')

dates1 = retrieve_completed_records_by_field(table,'Chloe-Answer')
dates1 = [i.Date for i in dates1]
dates2 = retrieve_completed_records_by_field(table,'Imad-Answer')
dates2 = [i.Date for i in dates2]
dates = [i for i in dates1 if i in dates2] + [i for i in dates2 if i in dates1]
dates = sorted(list(set(dates)))

def get_answer(date,user):
    formula = match({'Date':date})
    question = table.first(formula=formula)['fields']['Question']
    try:
        answer = table.first(formula=formula)['fields'][f'{user}-Answer']
    except KeyError:
        answer = None
    return question,answer
    

date_use = st.selectbox('Choose Date to View',options=dates)
col1,col2 = st.columns(2)
question,my_answer = get_answer(date_use,User)
question,their_answer = get_answer(date_use,other)
with col1:
    st.write(f'#### My Answer on {date_use}')
    st.write(question)
    st.markdown(f"*{my_answer.strip()}*")
with col2:
    st.write(f"#### {other}'s Answer on {date_use}")
    st.write(question)
    st.markdown(f"*{their_answer.strip()}*")
