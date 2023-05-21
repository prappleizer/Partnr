import streamlit_authenticator as stauth
import streamlit as st 
import yaml
from yaml.loader import SafeLoader
from pyairtable import Api, Base, Table
from pyairtable.formulas import match
from streamlit_echarts import st_echarts
import pandas as pd 
from datetime import date
import pandas as pd
import streamlit as st
import json
from streamlit_drawable_canvas import st_canvas



with open('credentials.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized'],

)

def get_days():
    anniversary = date(2023, 3,19)
    today = date.today() 
    delta = today - anniversary
    return delta.days


def return_options():
    option = {
    "series": [
        {
            "type": 'gauge',
            "min": 0,
            "max": 360,
            "progress": {
                "show": True,
                "width": 10
            },
            "axisLine": {
                "lineStyle": {
                    "width": 10
                }
            },
            "axisTick": {
                "show": False
            },
            "splitLine": {
                "length": 5,
                "lineStyle": {
                    "width": 1,
                    "color": '#999'
                }
            },
            "axisLabel": {
                "distance": 25,
                "color": '#999',
                "fontSize": 10
            },
            "anchor": {
                "show": True,
                "showAbove": True,
                "size": 25,
                "itemStyle": {
                    "borderWidth": 2
                }
            },
            "title": {
                "show": True,
                "value": 'UP Status',
                "fontSize": 20,
                "offsetCenter": [0, '70%']
            },
            "detail": {
                "valueAnimation": True,
                "fontSize": 20,
                "offsetCenter": [0, '90%']
            },
            "data": [
                {
                    "name": 'Days Together',
                    "value": get_days(),
                    "bounds": [0, 360],
                    "fontSize": 30
                                }
                            ]
                        }
                    ]
                }
    return option

def get_pbar_options(daily,cards,notes,moods):
    gaugeData = [
    {
        "value": daily,
        "name": 'Daily Check-Ins',
        "title": {
            "offsetCenter": ['0%', '-60%']
        },
        "detail": {
            "valueAnimation": True,
            "offsetCenter": ['0%', '-42%']
        }
    },
    {
        "value": cards,
        "name": 'Cards Swiped',
        "title": {
            "offsetCenter": ['0%', '-25%']
        },
        "detail": {
            "valueAnimation": True,
            "offsetCenter": ['0%', '-8%']
        }
    },
    {
        "value": notes,
        "name": 'Notes Sent',
        "title": {
            "offsetCenter": ['0%', '10%']
        },
        "detail": {
            "valueAnimation": True,
            "offsetCenter": ['0%', '28%']
        }
    },
    {
        "value": moods,
        "name": 'Moods Set',
        "title": {
            "offsetCenter": ['0%', '45%']
        },
        "detail": {
            "valueAnimation": True,
            "offsetCenter": ['0%', '64%']
        }
    }
]

    option = {
        "series": [
            {
                "type": 'gauge',
                "startAngle": 90,
                "endAngle": -270,
                "pointer": {
                    "show": False
                },
                "progress": {
                    "show": True,
                    "overlap": False,
                    "roundCap": True,
                    "clip": False,
                    "itemStyle": {
                        "borderWidth": 1.0,
                        "borderColor": '#464646'
                    }
                },
                "axisLine": {
                    "lineStyle": {
                        "width": 25
                    }
                },
                "splitLine": {
                    "show": False,
                    "distance": 0,
                    "length": 10
                },
                "axisTick": {
                    "show": False
                },
                "axisLabel": {
                    "show": False,
                    "distance": 60
                },
                "data": gaugeData,
                "title": {
                    "fontSize": 10
                },
                "detail": {
                    "width": 20,
                    "height": 14,
                    "fontSize": 14,
                    "color": 'inherit',
                    "borderColor": 'inherit',
                    "borderRadius": 20,
                    "borderWidth": 1,
                    "formatter": '{value}'
                }
            }
        ]
    }
    return option

name, authentication_status, username = authenticator.login('Login', 'main')
if authentication_status:
    st.session_state["role"] = name.split(' ')[0]
    if 'clear_drawing' not in st.session_state.keys():
        st.session_state['clear_drawing'] = False
    User = st.session_state.get('role')
    if User == "Imad":
        other = 'Chloe'
    else:
        other = "Imad"
    authenticator.logout('Logout', 'main')    
    st.write(f"# Welcome, {name.split(' ')[0]} ♥")
    
    #st.metric(label="You have been together", value=get_days(), delta="days")
    col1,col2=st.columns(2)
    with col1:
        #st.write('Here is some lovely info about your relationship')
        st_echarts(options=return_options())
    with col2:
        table = Table(st.secrets['AIRTABLE_API_KEY'],st.secrets['AIRTABLE_BASE_ID'],'Totals')
        dailys = table.first(formula=match({'Name':'Total-Dailys'}))['fields']['Number']
        cards = table.first(formula=match({'Name':'Total-Swipes'}))['fields']['Number']
        notes = table.first(formula=match({'Name':'Total-Notes'}))['fields']['Number']
        moods = table.first(formula=match({'Name':'Total-Moodsets'}))['fields']['Number']
        st_echarts(get_pbar_options(dailys,cards,notes,moods))
    st.write(f'### Leave {other} a Note :)')
    # Specify canvas parameters in application
    drawing_mode = "freedraw"
    stroke_width = st.slider("Stroke width: ", 1, 25, 3)
    placeholder = st.empty() 
    with placeholder.form('canv'):
        table = Table(st.secrets['AIRTABLE_API_KEY'],st.secrets['AIRTABLE_BASE_ID'],'notes')
        if st.session_state['clear_drawing'] is not True:
            try:
                other_drawing = table.first(formula=match({'Name':f"From {other}"}))['fields']['drawing']
                other_drawing=json.loads(other_drawing)
            except:
                other_drawing=None
        else:
            other_drawing=None
        canvas_result = st_canvas(
            initial_drawing=other_drawing,
            fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
            stroke_width=stroke_width,
            stroke_color="#000",
            background_color="#eee",
            background_image= None,
            update_streamlit=True,
            height=150,
            width=700,
            drawing_mode=drawing_mode,
            point_display_radius= 0,
            key="canvas",
        )

        # Do something interesting with the image data and paths
        #if canvas_result.image_data is not None:
        #    st.image(canvas_result.image_data)
        if canvas_result.json_data is not None:
            objects = pd.json_normalize(canvas_result.json_data["objects"]) # need to convert obj to str because PyArrow
            for col in objects.select_dtypes(include=['object']).columns:
                objects[col] = objects[col].astype("str")
        col1,col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button('Send')
        with col2:
            clear = st.form_submit_button("Clear")
    if submit:
        loc = table.first(formula=match({'Name':f"From {User}"}))['id']
        table.update(loc,{'drawing':json.dumps(canvas_result.json_data, indent = 4)})
        totals = Table(st.secrets['AIRTABLE_API_KEY'],st.secrets['AIRTABLE_BASE_ID'],'Totals')
        entry = totals.first(formula=match({'Name':'Total-Notes'}))
        totals.update(entry['id'],{'Number':entry['fields']['Number']+1})
        st.balloons()
    if clear:
        st.session_state['clear_drawing'] = True
        st.experimental_rerun()
        

elif authentication_status == False:
    st.error('Username/password is incorrect')
    st.session_state["role"] = 'anonymous'
elif authentication_status == None:
    st.warning('Please enter your username and password')
    st.session_state["role"] = 'anonymous'





