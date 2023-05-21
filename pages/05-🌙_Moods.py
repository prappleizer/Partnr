import streamlit as st 
from pyairtable import  Table
from pyairtable.formulas import match
import pandas as pd
import altair as alt

if st.session_state.get("role") not in ["Imad","Chloe"]:
    st.error("You need to be logged in to access this page.")
    st.stop()

#st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto")

User = st.session_state.get('role')
if User == "Imad":
    other = 'Chloe'
else:
    other = "Imad"

st.title('Set Mood')

options = [
"hangry",
"sleepy",
"cuddly",
"flirty",
"cozy",
"sensitive",
"irritable",
"silly",
"focused",
"anxious",
"frustrated",
"grumpy",
"overwhelmed",
"bored",
"lazy",
"lonely",
"gloomy",
"restless",
"head-empty",
"tummy-hurty",
"twirly",
"energetic",
"adventurous",
"crunk",
"bubbly",
"relaxed",
]


with st.form('mood',clear_on_submit=True):
    select = st.multiselect("Moods",options = options)
    submit = st.form_submit_button('Set Mood')
if submit:
    table=Table(st.secrets['AIRTABLE_API_KEY'],st.secrets['AIRTABLE_BASE_ID'],'Moods')
    rec_id = table.first(formula=match({'Name':User}))['id']
    table.update(rec_id,{'mood-tags':select})
    st.write('Mood has been updated.')
    totals = Table(st.secrets['AIRTABLE_API_KEY'],st.secrets['AIRTABLE_BASE_ID'],'Totals')
    entry = totals.first(formula=match({'Name':'Total-Moodsets'}))
    totals.update(entry['id'],{'Number':entry['fields']['Number']+1})

st.divider()




def return_altair(moods):
    source = pd.DataFrame({"category": moods, "value": [5]*len(moods)})

    pie = alt.Chart(source).mark_arc(innerRadius=105).encode(
    theta=alt.Theta(field="value", type="quantitative", stack=True, scale=alt.Scale(type="linear",rangeMax=1.5708, rangeMin=-1.5708 )),
    color=alt.Color(field="category", type="nominal"),)

    #pie = pie + pie.mark_text(radius=190, fontSize=14).encode(text='category')

    return pie



st.write(f'Right now, {other} is feeling...')
table=Table(st.secrets['AIRTABLE_API_KEY'],st.secrets['AIRTABLE_BASE_ID'],'Moods')
moods = table.first(formula=match({'Name':other}))['fields']['mood-tags']
#st_echarts(options=get_chart_options(moods),width="100%")
st.altair_chart(return_altair(moods), use_container_width=True)


st.write(f'Right now, Your mood is set to...')
table=Table(st.secrets['AIRTABLE_API_KEY'],st.secrets['AIRTABLE_BASE_ID'],'Moods')
moods = table.first(formula=match({'Name':User}))['fields']['mood-tags']
#st_echarts(options=get_chart_options(moods),width="100%")
st.altair_chart(return_altair(moods), use_container_width=True)

