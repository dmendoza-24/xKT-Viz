import datetime
import pickle
import pandas as pd
import json
import re
trace = 0
student_index = 0
example_index = 0
start_index = []
encountered_spheres = []
confidence_list = []
mastered_spheres = []
held_miscs = []
profile = dict()

def gather_input():
    # user decides trace to be visualized
    global trace
    global student_index
    global example_index
    global profile
    while True:
        try:
            trace = int(input("Enter trace number to display: ").strip())
            student_index = trace // 100 + 1
            example_index = trace % 100
            break
        except ValueError:
            print("Invalid input type, try again.")
        #end try
    #end while
    students = {0:1,
                100:2,
                200:3,
                300:4,
                400:5,
                500:6,
                600:7,
                700:8,
                800:9,
                900:10}
    for trace_min, student in reversed(students.items()):
        if student_index >= trace_min:
            stud_type = student
            break
        #end if
    #end for
    with open(r'.\data\students\Student_'+str(stud_type)+r'_profile.json','r') as file:
        profile = json.load(file)
    #end with
#end gather_input

def events_setup():
    # creates data to be converted into graph event icons
    data_lines = ["date,knowledge,event_type,event_title,desc_index\n"]
    desc_lines = []
    output_path = (r'.\data\example\output\output_' + str(student_index) + r'_' + str(example_index) + r'_lem.md')
    trace_path = (r'.\data\example\traces\trace_' + str(trace) + r'.csv')

    with open(output_path, 'r', encoding='utf8') as output_file:
        with open(trace_path, 'r', encoding='utf8') as trace_file:
            trace_timeline = '--'.join(trace_file.readlines()).split('\n--==::==::==\n')
            trace_timeline = trace_timeline[:len(trace_timeline)-1]
            event_type = ""
            output_file.readline()
            end_of_file = False
            all_events = []
            while True:
                current_event = []
                while True:
                    current_line = output_file.readline()
                    if (current_line == ''):
                        end_of_file = True
                        break
                    elif (current_line.strip()[0:6] == '# Step'):
                        break
                    elif (current_line.strip() == ''):
                        continue
                    elif (current_line.strip() == '## Example Cases:'):
                        current_event.append(current_line.strip())
                    elif (current_line.strip()[0:2] != '##'):
                        current_event.append(current_line.rstrip())
                    #end if/elif
                #end while
                event_type = current_event[0]
                if event_type == "Homework" or event_type == "Quiz":
                    description = r'\n'.join(current_event[1:])
                    description = re.split(r'Q\d+.'+'|'+r'A\d+.', description)
                    questions = description[1:(len(description)//2+1)]
                    answers = description[(len(description)//2+1):]
                    for i in range(len(answers)):
                        answers[i] = answers[i][:answers[i].find('Knowledge Components:')]
                    #end for
                    description = []
                    for i in range(len(questions)):
                        description.append('Q'+str(i+1)+'. ' + questions[i].strip())
                        description.append('A. ' + answers[i].strip())
                    #end for
                else:
                    description = current_event[1:]
                #end if/else
                all_events.append((event_type,description))
                if end_of_file:
                    break
                #end if
            #end while
            desc_count = 1
            global encountered_spheres
            encountered_spheres = []
            global confidence_list
            confidence_list = []
            global mastered_spheres
            mastered_spheres = []
            global held_miscs
            held_miscs = []
            exposed_spheres = set()
            last_step = 0
            for step in trace_timeline:
                known_count = 0
                total_spheres = 115
                step_events = []
                conf_dict = dict()
                if encountered_spheres:
                    enc_dict = encountered_spheres[-1][0].copy()
                else:
                    enc_dict = dict()
                mast_list = []
                mis_list = []
                first = True
                for component in step.split('--'):
                    current = component.split(r';')
                    if current[0] == 'Mis':
                        current_step = int(current[-2])
                        if current[-1].strip() == '1':
                            with open(r'.\data\CS1C_references\sphere_to_mis.pkl', 'rb') as file:
                                mis_dict = pickle.load(file)
                                for sphere, miscs in mis_dict.items():
                                    for mis in miscs:
                                        if mis == current[1]:
                                            mis_list.append((sphere, mis))
                                        #end if
                                    #end for
                                #end for
                            #end with
                        #end if
                    #end if
                    if current[0] == "Sphere":
                        current_step = int(current[-3])
                        if first:
                            exposed_spheres = set() if last_step == 0 or last_step != current_step else exposed_spheres
                            first = False
                        #end if
                        if current[-2] == "1":
                            known_count += 1
                            mast_list.append(current[1])
                        elif current[-2] == "0":
                            if current[-2] in mast_list:
                                known_count -= 1
                                mast_list.remove(current[1])
                            #end if
                        #end if/elif
                        if current[-5] == "1":
                            exposed_spheres.add(current[1])
                            enc_dict[current[1]] = enc_dict.get(current[1], 0) + 1
                        #end if
                        conf_dict[current[1]] = current[-1].strip()
                        step_events = current[-10:-5]
                    #end if
                #end for
                encountered_spheres.append([enc_dict,current_step])
                confidence_list.append([conf_dict, current_step])
                mastered_spheres.append([mast_list, current_step])
                held_miscs.append((mis_list, current_step))
                filtered_enc = []
                for sphere in enc_dict:
                    if sphere not in exposed_spheres:
                        filtered_enc.append(sphere)
                    #end if
                #end for
                if not exposed_spheres:
                    exposed_spheres.add("No spheres were exposed today.")
                #end if
                try:
                    event_addon = '' if last_step == 0 or last_step != current_step else event_addon
                    if step_events[0] == "1": # Lecture
                        idx = next((i for i, (event,desc) in enumerate(all_events) if event == "Lecture"))
                        current_event = all_events.pop(idx)
                        date = start_date + datetime.timedelta(days=current_step)
                        data_lines.append(','.join([date.strftime("%m-%d-%Y"),str(known_count/total_spheres*100),current_event[0],current_event[0],str(desc_count)]) + '\n')
                        desc_lines.append(r'\n'.join(current_event[1]))
                        desc_count +=1
                        event_addon += ' for Lecture' if last_step == 0 or last_step != current_step else ' and Lecture'
                    if step_events[1] == "1": # Reading
                        idx = next((i for i, (event,desc) in enumerate(all_events) if event == "Reading"))
                        current_event = all_events.pop(idx)
                        date = start_date + datetime.timedelta(days=current_step)
                        data_lines.append(','.join([date.strftime("%m-%d-%Y"),str(known_count/total_spheres*100),current_event[0],current_event[0],str(desc_count)]) + '\n')
                        desc_lines.append(r'\n'.join(current_event[1]))
                        desc_count +=1
                        event_addon += ' for Reading' if last_step == 0 or last_step != current_step else ' and Reading'
                    if step_events[2] == "1": # Office Hours
                        idx = next((i for i, (event,desc) in enumerate(all_events) if event == "Office Hours"))
                        current_event = all_events.pop(idx)
                        date = start_date + datetime.timedelta(days=current_step)
                        data_lines.append(','.join([date.strftime("%m-%d-%Y"),str(known_count/total_spheres*100),current_event[0],current_event[0],str(desc_count)]) + '\n')
                        desc_lines.append(r'\n'.join(current_event[1]))
                        desc_count +=1
                        event_addon += ' for Office Hours' if last_step == 0 or last_step != current_step else ' and Office Hours'
                    if step_events[3] == "1": # Homework
                        idx = next((i for i, (event,desc) in enumerate(all_events) if event == "Homework"))
                        current_event = all_events.pop(idx)
                        date = start_date + datetime.timedelta(days=current_step)
                        data_lines.append(','.join([date.strftime("%m-%d-%Y"),str(known_count/total_spheres*100),current_event[0],current_event[0],str(desc_count)]) + '\n')
                        desc_lines.append(r'\n'.join(current_event[1]))
                        desc_count +=1
                        event_addon += ' for Homework' if last_step == 0 or last_step != current_step else ' and Homework'
                    if step_events[4] == "1": # Quiz
                        idx = next((i for i, (event,desc) in enumerate(all_events) if event == "Quiz"))
                        current_event = all_events.pop(idx)
                        date = start_date + datetime.timedelta(days=current_step)
                        data_lines.append(','.join([date.strftime("%m-%d-%Y"),str(known_count/total_spheres*100),current_event[0],current_event[0],str(desc_count)]) + '\n')
                        desc_lines.append(r'\n'.join(current_event[1]))
                        desc_count +=1
                        event_addon += ' for Quiz' if last_step == 0 or last_step != current_step else ' and Quiz'
                    #end ifs
                except IndexError:
                    print("ERROR")
                    continue
                #end try/except
                date = start_date + datetime.timedelta(days=current_step)
                data_lines.append(','.join([date.strftime("%m-%d-%Y"),str(known_count/total_spheres*100),"Knowledge Components","Knowledge Components" + event_addon,str(desc_count)]) + '\n')
                if len(filtered_enc) == 0:
                    desc_lines.append(r'\n'.join(exposed_spheres))
                else:
                    desc_lines.append(r'\n'.join(exposed_spheres) + r'\nOther Encountered Spheres ▼\n' + r'\n'.join(filtered_enc))
                #end if/else
                desc_count += 1
                last_step = current_step
            #end for
        #end with
    #end with
    with open(r'.\data\visual_data.csv', 'w') as file:
        for line in data_lines:
            file.write(line)
        #end for
    #end with
    with open(r'.\data\descriptions.txt', 'w', encoding='utf-8') as file:
        for line in desc_lines:
            file.write(line + '\n')
        #end for
    #end with
#end events_setup

def trace_conversion(date):
    # called in main to create user specified graph data
    global start_date
    start_date = date.split('/')
    month = int(start_date[0].lstrip('0'))
    day = int(start_date[1])
    year = int(start_date[2])
    start_date = datetime.datetime(year, month, day)
    gather_input()
    events_setup()
    return start_date
#end trace_conversion

def sph_level(step, sphere):
    for miscs, stp in held_miscs:
        if stp == step:
            for sph, mis in miscs:
                if sph == sphere:
                    return 0
                #end if
            #end for
        #end if
    #end for
    for masts, stp in mastered_spheres:
        if stp == step:
            for sph in masts:
                if sph == sphere:
                    return 1
                #end if
            #end for
        #end if
    #end for
    return 2
#end sph_level

def get_start_date():
    return start_date
#end get_start_date

def get_held_miscs():
    return held_miscs
#end get_held_miscs

def generate_confidence(sphere):
    conf_values = []
    for conf_dict in confidence_list:
        conf = round(float(conf_dict[0][sphere]), 3) * 100
        date = (start_date + datetime.timedelta(days = conf_dict[1])).strftime('%m-%d-%Y')
        conf_values.append([date, conf])
    #end for
    df = pd.DataFrame(conf_values, columns=['date','confidence'])
    return df
#end generate_confidence