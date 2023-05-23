
import streamlit as st 
from pyairtable import Api, Base, Table
from pyairtable.formulas import match
from datetime import date 
import json 


if st.session_state.get("role") not in ["Imad","Chloe"]:
    st.error("You need to be logged in to access this page.")
    st.stop()


User = st.session_state.get('role')
if User == "Imad":
    other = 'Chloe'
else:
    other = "Imad"

table = Table(st.secrets['AIRTABLE_API_KEY'],st.secrets['AIRTABLE_BASE_ID'],'Trivia')
today = date.today()
today = today.strftime("%Y-%m-%d")



with open("json/quiz.json", 'r') as j:
    contents = json.loads(j.read())

formula = match({'Date':today})
entry = table.first(formula=formula)
rec_id = entry['id']

all_tab = table.all()
myscore = 0
their_score = 0
for i in all_tab:
    if f'{User}-Score' in i['fields']:
        myscore+= i['fields'][f'{User}-Score']
    if f'{other}-Score' in i['fields']:
        their_score+= i['fields'][f'{other}-Score']
st.write(
            f"## Today's Question: {entry['fields']['Question']}"
        )

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Your Score", value=str(myscore), delta="Total Score")
    if f'{User}-Answer' in entry['fields']:
            st.write("You have already filled out today's quiz question. Try tomorrow!")
    else:
        with st.form('entry'):
            st.write('### Enter Your Answer')
            options = contents[entry['fields']['Question']]
            selection = st.multiselect(label='Choose answers',options=options)
            submit = st.form_submit_button('Submit')
        if submit:
            outstr = ""
            for i in selection:
                outstr += f"{i} | "
            table.update(rec_id,{f'{User}-Answer':outstr})
            st.experimental_rerun()
    with col2: 
        st.metric(label=f"{other}'s Score", value=str(their_score), delta="Total Score")
        if f'{User}-Guess' in entry['fields']:
            if f'{other}-Answer' in entry['fields']:
                score = 0
                answer_str = table.get(rec_id)['fields'][f'{User}-Guess']
                answer_list = answer_str.split(' | ')
                answer_list = [i for i in answer_list if len(i)>0]
                for i in answer_list:
                    if i in entry['fields'][f'{other}-Answer']:
                        score+=1
                        st.write(f'You were right! {other} chose {i}')
                    if i not in entry['fields'][f'{other}-Answer']:
                        score -= 1
                        st.write(f"Ruh Roh, {other} didn't choose {i}...")

                st.write(f'You got a score of {score}.')
                st.write(f"All of {other}'s answers: ")
                st.write(entry['fields'][f'{other}-Answer'])
                table.update(rec_id,{f'{User}-Score':score})
            else:
                st.write('Guess has been input, waiting on your partner!') 
        else:
            with st.form('quiz'):
                st.write(f'### Enter Your Guess for {other}')
                options = contents[entry['fields']['Question']]
                selection2 = st.multiselect(label='Choose answers',options=options)
                submit2 = st.form_submit_button('Submit')
            if submit2:
                if f'{other}-Answer' in entry['fields']:
                    score = 0
                    for i in selection2:
                        if i in entry['fields'][f'{other}-Answer']:
                            score+=1
                            st.write(f'You were right! {other} chose {i}')
                        else:
                            score-=1
                            st.write(f"Ruh Roh {other} didn't choose {i}")


                    st.write(f'Your score this round: {score}')
                    st.write(f"All of {other}'s answers: ")
                    st.write(entry['fields'][f'{other}-Answer'])
                    table.update(rec_id,{f'{User}-Score':score})
                    outstr = ""
                    for i in selection2:
                        outstr += f"{i} | "
                    table.update(rec_id,{f"{User}-Guess":outstr})
                    st.experimental_rerun()
                else: 
                    outstr = ""
                    for i in selection2:
                        outstr += f"{i} | "
                    table.update(rec_id,{f"{User}-Guess":outstr})
                    st.write(f"{other} hasn't answered yet, but your guess has been lodged!")
                    st.experimental_rerun()
