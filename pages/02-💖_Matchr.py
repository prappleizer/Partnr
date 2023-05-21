import streamlit as st 


from streamlit_extras.add_vertical_space import add_vertical_space
from pyairtable import Table
from pyairtable.formulas import match


if st.session_state.get("role") not in ["Imad","Chloe"]:
    st.error("You need to be logged in to access this page.")
    st.stop()


User = st.session_state.get('role')
if User == "Imad":
    other = 'Chloe'
else:
    other = "Imad"



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


table = Table(st.secrets['AIRTABLE_API_KEY'],st.secrets['AIRTABLE_BASE_ID'],'Positions')
# First retrieve all positions for which YOU have not swiped
if 'choice' not in st.session_state.keys():
    st.session_state.choice = retrieve_first_empty_record_by_field(table,f'{User}-Interest')
    #st.session_state.choice = Record(table.first(formula=match({'noimg':'Yes'})))





#pic = st.empty() 
#title = st.empty()
tab1, tab2, = st.tabs(["Explore","🔥Matches🔥"])

with tab1:
    placeholder = st.empty()
    with placeholder.form('Entry'):
        st.write(f"## {st.session_state.choice.Name}")
        if hasattr(st.session_state.choice,'noimg'):
            st.markdown(st.session_state.choice.Description)
        else:
            st.image(f"./img/crop/{st.session_state.choice.Number}.jpg",use_column_width='always')
        cols = st.columns([1,1,1])

        with cols[0]:
            yes = st.form_submit_button("Yes",use_container_width=True)
            if yes:
                totals = Table(st.secrets['AIRTABLE_API_KEY'],st.secrets['AIRTABLE_BASE_ID'],'Totals')
                entry = totals.first(formula=match({'Name':'Total-Swipes'}))
                totals.update(entry['id'],{'Number':entry['fields']['Number']+1})
                if hasattr(st.session_state.choice,f'{other}-Interest'):
                    if getattr(st.session_state.choice,f'{other}-Interest') in ['Maybe','Yes']:
                        st.balloons()
                        st.expander('You got a Match!')
                with st.spinner('Loading Next'):
                    table.update(st.session_state.choice.id,{f'{User}-Interest':'Yes'})
                    #placeholder.empty()
                    st.session_state.choice = retrieve_first_empty_record_by_field(table,f'{User}-Interest')
                    st.experimental_rerun()
        with cols[1]:
            no = st.form_submit_button("No",use_container_width=True)
            if no:
                totals = Table(st.secrets['AIRTABLE_API_KEY'],st.secrets['AIRTABLE_BASE_ID'],'Totals')
                entry = totals.first(formula=match({'Name':'Total-Swipes'}))
                totals.update(entry['id'],{'Number':entry['fields']['Number']+1})
                with st.spinner('Loading Next'):
                    table.update(st.session_state.choice.id,{f'{User}-Interest':'No'})
                    #placeholder.empty()
                    st.session_state.choice = retrieve_first_empty_record_by_field(table,f'{User}-Interest')
                    st.experimental_rerun()
        with cols[2]:
            maybe = st.form_submit_button("Maybe",use_container_width=True)
            if maybe:
                totals = Table(st.secrets['AIRTABLE_API_KEY'],st.secrets['AIRTABLE_BASE_ID'],'Totals')
                entry = totals.first(formula=match({'Name':'Total-Swipes'}))
                totals.update(entry['id'],{'Number':entry['fields']['Number']+1})
                table.update(st.session_state.choice.id,{f'{User}-Interest':'Maybe'})
                if hasattr(st.session_state.choice,f'{other}-Interest'):
                    if getattr(st.session_state.choice,f'{other}-Interest') in ['Maybe','Yes']:
                        st.balloons()
                        st.expander('You got a Match!')
                
                with st.spinner('Loading Next'):
                    
                    # Check with 
                    #placeholder.empty()
                    st.session_state.choice = retrieve_first_empty_record_by_field(table,f'{User}-Interest')
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

