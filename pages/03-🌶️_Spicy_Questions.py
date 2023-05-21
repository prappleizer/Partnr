import streamlit as st 


from streamlit_extras.add_vertical_space import add_vertical_space
from pyairtable import  Table
from datetime import date
from pyairtable.formulas import match

class Record():
    def __init__(self,api_response):
        self.id = api_response['id']
        for i in api_response['fields']:
            setattr(self,i,api_response['fields'][i])

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

# def add_bg_from_url():
#     st.markdown(
#             f"""
#             <style>
#             .stApp {{
#                 background-image: url("https://images.pexels.com/photos/7134985/pexels-photo-7134985.jpeg");
#                 background-attachment: fixed;
#                 background-size: cover
#             }}
#             </style>
#             """,
#             unsafe_allow_html=True
#         )

# add_bg_from_url() 

today = date.today()
today = today.strftime("%Y-%m-%d")
st.write(f'# Daily Questions (Spicy Edition): {today}')
add_vertical_space(4)

table = Table(st.secrets['AIRTABLE_API_KEY'],st.secrets['AIRTABLE_BASE_ID'],'Daily')

User = st.session_state.get('role')
if User == "Imad":
    other = 'Chloe'
else:
    other = "Imad"


formula = match({'Date':today})
entry = Record(table.first(formula=formula))
if hasattr(entry,f'{User}-Kinky-Answer'):
    st.write("You have already answered today's Question!")
else:    
    placeholder = st.empty()
    with placeholder.form('daily-question',clear_on_submit=True):
        st.write(f"#### {getattr(entry,'Kinky-Question')}")
        answer = st.text_area('Enter Response',value='',height=300)
        submit = st.form_submit_button("Submit")

    if submit:
        totals = Table(st.secrets['AIRTABLE_API_KEY'],st.secrets['AIRTABLE_BASE_ID'],'Totals')
        entry = Record(totals.first(formula=match({'Name':'Total-Dailys'})))
        totals.update(entry.id,{'Number':entry.Number+1})
        balloons = st.balloons()
        table.update(entry.id,{f"{User}-Kinky-Answer":answer})
        placeholder.empty()
        st.write('Your Response has been submitted!')

st.divider()
st.write('## Previous Answers')

dates1 = retrieve_completed_records_by_field(table,'Chloe-Kinky-Answer')
dates1 = [i.Date for i in dates1]
dates2 = retrieve_completed_records_by_field(table,'Imad-Kinky-Answer')
dates2 = [i.Date for i in dates2]
dates = list(set(dates1+dates2))


def get_answer(date,user):
    formula = match({'Date':date})
    try:
        one = table.first(formula=formula)['fields'][f'{user}-Kinky-Answer']
        print(one)
    except KeyError:
        one = None
    return one
    
if len(dates)>0:
    date_use = st.selectbox('Choose Date to View',options=dates)
    col1,col2 = st.columns(2)
    my_answer = get_answer(date_use,User)
    their_answer = get_answer(date_use,other)
    with col1:
        st.write(f'My Answer on {date_use}')
        st.write(my_answer)
    with col2:
        st.write(f"{other}'s Answer on {date_use}")
        st.write(their_answer)
