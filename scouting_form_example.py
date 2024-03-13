import streamlit as st


def write_scouting_row(data:dict):
    #conn = st.connection("gsheets", type=GSheetsConnection)
    #existing_data = conn.read(ttl=0,)
    #existing_data = existing_data.append(data,ignore_index=True)
    print("Saving...")
    print(existing_data.to_string())
    #conn.update(data=existing_data)

st.title("Scouting Form Experiment")
match_form = st.form(key="match_row",clear_on_submit=True)

with match_form:
    col1,col2,col3 = st.columns(3)
    with col1:
        team = st.selectbox(label="Team", options=['281', '2974', '4451', '342', '343'])
    with col2:
        match = st.selectbox(label="Match", options=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])
    with col3:
        scouter = st.text_input("Scout First Name")

    st.header("Fouls and Penalties")
    col1 ,col2,col3,col4 = st.columns(4)

    with col1:
        num_fouls = st.number_input('Foul Counts',key='num_fouls',min_value=0,step=1)
    with col2:
        num_penalties = st.number_input('Penalties',key='num_penalties',min_value=0,step=1)


    st.header("Scoring")
    col1 ,col2,col3,col4 = st.columns(4)
    with col1:
        st.text("Amp")
        amp_misses = st.number_input(':no_entry_sign: Miss',key='amp_misses',min_value=0,step=1)
        amp_scores = st.number_input(':white_check_mark: Success',key='amp_scores',min_value=0,step=1)


    with col2:
        st.text("Close Speaker")
        close_speaker_misses = st.number_input('Miss',key='close_speaker_misses',min_value=0,step=1)
        close_speaker_scores = st.number_input('Success',key='close_speaker_scores',min_value=0,step=1)

    with col3:
        st.text("Podium")
        podium_misses = st.number_input('Miss',key='podium_misses',min_value=0,step=1)
        podium_scores = st.number_input('Success',key='podium_scores',min_value=0,step=1)

    with col4:
        st.text("Far Field")
        far_speaker_misses = st.number_input('Miss',key='far_speaker_misses',min_value=0,step=1)
        far_speaker_scores = st.number_input('Success',key='far_speaker_scores',min_value=0,step=1)

    st.header("End Game")
    col1, col2,col3= st.columns(3)
    with col1:
        num_rps = st.number_input('RPs', key="rps", min_value=0, max_value=4, step=1)
    with col2:
        climbed = st.checkbox ("Climbed",key='disabled_broken')

    with col3:
        parked_broken = st.checkbox ("Parked",key='parked_broken')

    notes = st.text_area("Other Notes")

    submitted = st.form_submit_button("Submit", type="secondary", disabled=False, use_container_width=False)
    if submitted:
        write_scouting_row({
            "Team":  team,
            "Match": match,
            "Notes": notes,
            "Climb": climbed,
            'rps': num_rps,
            'Notes': notes
        })
        st.text("Response Saved!")
