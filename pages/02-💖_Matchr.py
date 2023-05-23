import streamlit as st 


from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_star_rating import st_star_rating
from pyairtable import Table
from pyairtable.formulas import match
import time
import http,urllib
import numpy as np 

if st.session_state.get("role") not in ["Imad","Chloe"]:
    st.error("You need to be logged in to access this page.")
    st.stop()


User = st.session_state.get('role')
if User == "Imad":
    other = 'Chloe'
else:
    other = "Imad"

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

class Record():
    def __init__(self,api_response):
        self.id = api_response['id']
        for i in api_response['fields']:
            setattr(self,i,api_response['fields'][i])


def retrieve_first_empty_record_by_field(table,field):
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
    for i in all_rec:
        if field not in i['fields']:
            return Record(i)


def retrieve_completed_records_by_fields(table,fields):
    """returns a list of Record objects for entries in table which have field as empty

    Parameters
    ----------
    table : pyairtable.Table
        table to use
    fields : dict-like
        fields to search

    Returns
    -------
    records
        list of Record objects matching condition.
    """
    all_rec = table.all()
    return_recs = []
    for i in all_rec:
        if i.keys() >= fields:
                return_recs.append(Record(i))
    return return_recs

def retrieve_matches(table):
    formula = match({'Imad-Interest':'Yes','Chloe-Interest':'Yes'})
    yes = table.all(formula=formula)
    formula = match({'Imad-Interest':'Yes','Chloe-Interest':'Maybe'})
    maybe1 = table.all(formula=formula)
    formula = match({'Imad-Interest':'Maybe','Chloe-Interest':'Maybe'})
    maybe2 = table.all(formula=formula)
    formula = match({'Imad-Interest':'Maybe','Chloe-Interest':'Yes'})
    maybe3 = table.all(formula=formula)

    yesses = [Record(i) for i in yes]
    maybes = [Record(i) for i in maybe1]+[Record(i) for i in maybe2]+[Record(i) for i in maybe3]
    return yesses,maybes

def retrieve_untried_matches(table):
    formula = match({'Imad-Interest':'Yes','Chloe-Interest':'Yes'})
    yes = table.all(formula=formula)
    yesses = [Record(i) for i in yes]
    yesses = [i for i in yesses if not hasattr(i,'tried')]
    return yesses


def retrieve_attempted(table):
    formula = match({'tried':'Yes'})
    tried = table.all(formula=formula)
    tried = [Record(i) for i in tried]
    return tried

def retrieve_random_untried(table):
    attempted = retrieve_attempted(table)
    return np.random.choice(matches)

table = Table(st.secrets['AIRTABLE_API_KEY'],st.secrets['AIRTABLE_BASE_ID'],'Positions')
# First retrieve all positions for which YOU have not swiped
if 'matchr_choice' not in st.session_state.keys():
    st.session_state.matchr_choice = retrieve_first_empty_record_by_field(table,f'{User}-Interest')
    #st.session_state.matchr_choice = Record(table.first(formula=match({'noimg':'Yes'})))





#pic = st.empty() 
#title = st.empty()
tab1, tab2,tab3,tab4 = st.tabs(["Explore","🔥Matches🔥","Roll the Dice 🎲","Our Ratings ⭐️"])

with tab1:
    placeholder = st.empty()
    with placeholder.form('Entry'):
        st.write(f"## {st.session_state.matchr_choice.Name}")
        if hasattr(st.session_state.matchr_choice,'noimg'):
            st.markdown(st.session_state.matchr_choice.Description)
        else:
            st.image(f"./img/crop/{st.session_state.matchr_choice.Number}.jpg",use_column_width='always')
        cols = st.columns([1,1,1])

        with cols[0]:
            yes = st.form_submit_button("Yes",use_container_width=True)
            if yes:
                totals = Table(st.secrets['AIRTABLE_API_KEY'],st.secrets['AIRTABLE_BASE_ID'],'Totals')
                entry = totals.first(formula=match({'Name':'Total-Swipes'}))
                totals.update(entry['id'],{'Number':entry['fields']['Number']+1})
                if hasattr(st.session_state.matchr_choice,f'{other}-Interest'):
                    if getattr(st.session_state.matchr_choice,f'{other}-Interest') in ['Maybe','Yes']:
                        st.balloons()
                        st.expander('You got a Match!')
                        time.sleep(3)
                with st.spinner('Loading Next'):
                    table.update(st.session_state.matchr_choice.id,{f'{User}-Interest':'Yes'})
                    #placeholder.empty()
                    st.session_state.matchr_choice = retrieve_first_empty_record_by_field(table,f'{User}-Interest')
                    st.experimental_rerun()
        with cols[1]:
            no = st.form_submit_button("No",use_container_width=True)
            if no:
                totals = Table(st.secrets['AIRTABLE_API_KEY'],st.secrets['AIRTABLE_BASE_ID'],'Totals')
                entry = totals.first(formula=match({'Name':'Total-Swipes'}))
                totals.update(entry['id'],{'Number':entry['fields']['Number']+1})
                with st.spinner('Loading Next'):
                    table.update(st.session_state.matchr_choice.id,{f'{User}-Interest':'No'})
                    #placeholder.empty()
                    st.session_state.matchr_choice = retrieve_first_empty_record_by_field(table,f'{User}-Interest')
                    st.experimental_rerun()
        with cols[2]:
            maybe = st.form_submit_button("Maybe",use_container_width=True)
            if maybe:
                totals = Table(st.secrets['AIRTABLE_API_KEY'],st.secrets['AIRTABLE_BASE_ID'],'Totals')
                entry = totals.first(formula=match({'Name':'Total-Swipes'}))
                totals.update(entry['id'],{'Number':entry['fields']['Number']+1})
                table.update(st.session_state.matchr_choice.id,{f'{User}-Interest':'Maybe'})
                if hasattr(st.session_state.matchr_choice,f'{other}-Interest'):
                    if getattr(st.session_state.matchr_choice,f'{other}-Interest') in ['Maybe','Yes']:
                        st.balloons()
                        st.expander('You got a Match!')
                        time.sleep(3)
                
                with st.spinner('Loading Next'):
                    
                    # Check with 
                    #placeholder.empty()
                    st.session_state.matchr_choice = retrieve_first_empty_record_by_field(table,f'{User}-Interest')
                    st.experimental_rerun()


with tab2:
    matches,maybes = retrieve_matches(table)
    col1, col2 = st.columns(2)
    with col1:
        st.write('### 🔥 Matches 🔥')
        for i in matches:
            st.write(i.Name)
            with st.expander("See Card/Image"):
                if hasattr(i,'noimg'):
                    st.markdown(i.Description)
                else:
                    st.image(f"./img/crop/{i.Number}.jpg",use_column_width='always')
    with col2:
        st.write('### Maybes....')
        for i in maybes:
            st.write(i.Name)
            with st.expander("See Card/Image"):
                if hasattr(i,'noimg'):
                    st.markdown(i.Description)
                else:
                    st.image(f"./img/crop/{i.Number}.jpg",use_column_width='always')


with tab3: 
    st.write("### Here's one of your matches 😏")
    with st.form('submit-rating',clear_on_submit=True):
        matches = retrieve_untried_matches(table)
        query= np.random.choice(matches)
        st.write(query.Name)
        if hasattr(query,'noimg'):
            st.markdown(query.Description)
        else:
            st.image(f"./img/crop/{query.Number}.jpg",use_column_width='always')
        st.write("#### Tried it? What'd you think?")
    
        cols = st.columns(3)
        with cols[0]:
            #rating = st_star_rating('🔥 Rating', 5, 3, 25)
            rating = st.slider('rating',1,5,3,1)
        with cols[1]:
            #diff = st_star_rating('Difficulty', 5, 3, 25)
            diff = st.slider('difficulty',1,5,3,1,)
        with cols[2]:
            #comf = st_star_rating('Comfort',5,3,25)
            comf= st.slider('comfort',1,5,3,1)
        submit_extra = st.form_submit_button('Submit-rating-form')
        st.write(query.Name)
        st.write(query.id)
    if submit_extra:
        #print('test')
        st.write(query.Name)
        st.write(query.id)
        table.update(query.id,{f'{User}-rating':rating,f'{User}-difficulty':diff,f'{User}-comfort':comf,'tried':'Yes'})

    reroll = st.button('Roll a new Option')
    if reroll:
        query =  np.random.choice(retrieve_untried_matches(table))


with tab4:
    attempted = retrieve_attempted(table)
    for record in attempted:
        st.write(f'#### {record.Name}')
        if hasattr(record,'noimg'):
            st.markdown(record.Description)
        else:
            st.image(f"./img/crop/{record.Number}.jpg",use_column_width='always')
        if hasattr(record,f"{User}-rating"):
            st.write(f"**{User}'s ratings**")
            cols = st.columns(3)
            with cols[0]:
                a = st_star_rating('🔥 Rating',5,getattr(record,f"{User}-rating"),25,read_only=True,key=f'user-rating-readonly-{record.id}')
            with cols[1]:
                b =st_star_rating('Difficulty',5,getattr(record,f"{User}-difficulty"),25,read_only=True,key=f'user-diff-readonly-{record.id}')
            with cols[2]:
                c = st_star_rating('Comfort',5,getattr(record,f"{User}-comfort"),25,read_only=True,key=f'user-comf-readonly-{record.id}')
        if hasattr(record,f"{other}-rating"):
            st.write(f"**{other}'s ratings**")
            cols = st.columns(3)
            with cols[0]:
                d = st_star_rating('🔥 Rating',5,getattr(record,f"{other}-rating"),25,read_only=True,key=f'other-rating-readonly-{record.id}')
            with cols[1]:
                e = st_star_rating('Difficulty',5,getattr(record,f"{other}-difficulty"),25,read_only=True,key=f'other-diff-readonly-{record.id}')
            with cols[2]:
                f = st_star_rating('Comfort',5,getattr(record,f"{other}-comfort"),25,read_only=True,key=f'other-comf-readonly-{record.id}')
        st.divider()
        






