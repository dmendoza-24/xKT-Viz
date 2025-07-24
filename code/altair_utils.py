import altair as alt
import pandas as pd
import datetime
charts = []
start_date = None
end_date = None

def visualize(dataset, start, end = None):
    # generates and combines interactive knowledge charts
    global charts
    global start_date
    global end_date
    charts = []
    if end is None:
        end = dataset.iloc[-1, 0].split('-')
        end = datetime.datetime(int(end[2]), int(end[0]), int(end[1]))
    #end if
    start_date = start
    end_date = end
    single = alt.selection_point()
    
    gk_line = alt.Chart(dataset).mark_line(color='#69abd3', clip=True).encode(
        x=alt.X('date:T',title=None, scale=alt.Scale(domain=(start_date, end_date), padding=10)),
        y=alt.Y('knowledge:Q',title=None)
    )
    charts.append(gk_line)

    icons = alt.Chart(dataset).transform_calculate(
        url= 'http://localhost:1111/?desc=' + alt.datum.desc_index + '&title=' + alt.datum.event_title + r"+$" + alt.datum.date,
        emoji="{'Knowledge Components':'🔵','Lecture':'🧑‍🏫','Homework':'📝','Reading':'📖','Quiz':'📍','Office Hours':'🕒'}[datum.event_type]"
    ).mark_text(size=20, clip=True).encode(
        x=alt.X('date:T', title='Dates', scale=alt.Scale(domain=(start_date, end_date), padding=10)),
        y=alt.Y('position:Q', title='% Mastery', scale=alt.Scale(domain=[-2.5,102.5]),axis=alt.Axis()),
        href=alt.Href('url:N', title='Details'),
        text=alt.Text('emoji:N'),
        opacity=alt.condition(single, alt.value(1), alt.value(0.2)),
        tooltip=['event_type:N', 'date:T']
    ).add_params(single).properties(
        width='container',
        height=700
    ).interactive()
    charts.append(icons)

    main_graph = (sum(charts,start=alt.Chart(mark='image'))).configure_scale(clamp=False)
    main_graph['usermeta'] = {'embedOptions': {'loader': {'target': '_blank', 'rel': 'noopener noreferrer'}}}
    main_graph.save(r'.\data\chart.html')
#end visualize

def data_conversion(path):
    # Accesses data and utilizes Pandas to sort it into a data frame for Altair graph
    df = pd.read_csv(path)
    df['position'] = 0.0
    for index, row in df.iterrows():
        event_type = df.loc[index, 'event_type']
        knowledge = df.loc[index, 'knowledge']
        position = event_offset(event_type, knowledge)
        df.loc[index,'position'] = position
    #end for
    return df
#end data_conversion

def event_offset(event_type, knowledge):
    # Determines correct position offset for events in the Panda df
    if event_type == 'Homework':
        offset = 0
        if abs(knowledge-95) <= 2 and knowledge >= 95:
            offset = 2.5
        elif abs(knowledge-95) <= 2 and knowledge < 95:
            offset = -2.5
        #end if
        return 95 - offset
    elif event_type == 'Lecture':
        offset = 0
        if abs(knowledge-10) <= 2 and knowledge >= 10:
            offset = 2.5
        elif abs(knowledge-10) <= 2 and knowledge < 10:
            offset = -2.5
        #end if
        return 10 - offset
    elif event_type == 'Knowledge Components':
        return knowledge
    elif event_type == 'Reading':
        offset = 0
        if abs(knowledge-75) <= 2 and knowledge >= 75:
            offset = 2.5
        elif abs(knowledge-75) <= 2 and knowledge < 75:
            offset = -2.5
        #end if
        return 75 - offset
    elif event_type == 'Office Hours':
        offset = 0
        if abs(knowledge-20) <= 2 and knowledge >= 20:
            offset = 2.5
        elif abs(knowledge-20) <= 2 and knowledge < 20:
            offset = -2.5
        #end if
        return 20 - offset
    elif event_type == 'Quiz':
        offset = 0
        if abs(knowledge-85) <= 2 and knowledge >= 85:
            offset = 2.5
        elif abs(knowledge-85) <= 2 and knowledge < 85:
            offset = -2.5
        #end if
        return 85 - offset
    #end if/elif
#end event_offset

def add_confidence(dataset, line_color):
    global charts
    conf_graph = alt.Chart(dataset).mark_line(color=line_color, clip=True).encode(
        x=alt.X('date:T',title=None, scale=alt.Scale(domain=(start_date, end_date), padding=10)),
        y=alt.Y('confidence:Q',title=None)
    )
    charts.append(conf_graph)
    main_graph = (sum(charts,start=alt.Chart(mark='image'))).configure_scale(clamp=False)
    main_graph['usermeta'] = {'embedOptions': {'loader': {'target': '_blank', 'rel': 'noopener noreferrer'}}}
    main_graph.save(r'.\data\chart.html')
#end add_confidence

def remove_confidence():
    global charts
    del charts[-1]
    main_graph = (sum(charts,start=alt.Chart(mark='image'))).configure_scale(clamp=False)
    main_graph['usermeta'] = {'embedOptions': {'loader': {'target': '_blank', 'rel': 'noopener noreferrer'}}}
    main_graph.save(r'.\data\chart.html')
#end remove_confidence
