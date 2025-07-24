import wx
import wx.html2
import wx.richtext
import re
import datetime
import pickle
from urllib.parse import urlparse, parse_qs
import configparser
from . import altair_utils as vsz
from . import converter as cvt
dataset = None

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        # creates a wx frame with html content
        super(MyFrame, self).__init__(parent, title=title, size = wx.DisplaySize())
        self.current_date = cvt.get_start_date()
        # Graph Panel
        self.splitter = wx.SplitterWindow(self,-1)

        self.graph = wx.Panel(self.splitter, -1)
        self.graph.SetBackgroundColour(wx.Colour(255,255,255))

        self.browser = wx.html2.WebView.New(self.graph)
        self.browser.Bind(wx.html2.EVT_WEBVIEW_NEWWINDOW, self.new_tab)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.browser, 1, wx.ALL | wx.EXPAND, 10)
        
        label1 = wx.StaticText(self.graph, label='Events')
        label1.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName=u'Noto Color Emoji'))
        events = wx.StaticText(self.graph, label=u'🔵 Knowledge Components   🧑‍🏫 Lecture   📝 Homework   📖 Reading   📍 Quiz   🕒 Office Hours')

        label2 = wx.StaticText(self.graph, label='Knowledge')
        label2.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName=u'Noto Color Emoji'))
        
        lines = wx.FlexGridSizer(rows=1,cols=4,vgap=5,hgap=10)
        subline1 = wx.StaticText(self.graph,label='Overall Knowledge')
        subline1.SetForegroundColour(wx.Colour(105,171,211)) #blue
        subline2 = wx.StaticText(self.graph,label='Mastered Sphere')
        subline2.SetForegroundColour(wx.Colour(0,153,0)) #green
        subline3 = wx.StaticText(self.graph,label='Unknown Sphere')
        subline3.SetForegroundColour(wx.Colour(220,154,30)) #orange/yellow
        subline4 = wx.StaticText(self.graph,label='Misunderstood Sphere')
        subline4.SetForegroundColour(wx.Colour(255,0,0)) #red
        for subline in [subline1, subline2, subline3, subline4]:
            subline.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL, faceName=u'Noto Color Emoji'))
        #end for
        lines.AddMany([ (subline1,0,wx.ALL,0),
                        (subline2,0,wx.ALL,0),
                        (subline3,0,wx.ALL,0),
                        (subline4,0,wx.ALL,0)])
        
        events.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL,faceName=u'Noto Color Emoji'))
        grid= wx.FlexGridSizer(rows=4,cols=1, vgap=0, hgap=2)
        grid.AddMany([ (label1,0,wx.ALL,5),
                       (events,0,wx.ALL,10),
                       (label2,0,wx.ALL,5),
                       (lines,0,wx.ALL,10)])
        grid.AddGrowableCol(0,1)
        grid.AddGrowableRow(0,1)
        grid.AddGrowableRow(1,1)
        grid.AddGrowableRow(2,1)
        grid.AddGrowableRow(3,1)

        sizer.Add(grid, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)
        self.graph.SetSizer(sizer)
        
        # Details Panel - starts hidden
        self.details = wx.Panel(self.splitter, -1)
        self.details.SetBackgroundColour(wx.Colour(255,255,255))

        self.label = wx.StaticText(self.details, label='Details:')
        self.label.SetBackgroundColour(wx.Colour(255,255,255))
        self.description = wx.richtext.RichTextCtrl(self.details, style=wx.CB_READONLY|wx.TE_MULTILINE)
        self.description.WriteText("Click on an event in the graph to display its details.")
        self.description.Bind(wx.EVT_TEXT_URL, self.description_click)

        rb1 = wx.RadioButton(self.details, label = '1 Day View', style=wx.RB_GROUP)
        rb1.Bind(wx.EVT_RADIOBUTTON, self.graph_view)
        rb2 = wx.RadioButton(self.details, label = '3 Day View')
        rb2.Bind(wx.EVT_RADIOBUTTON, self.graph_view)
        rb3 = wx.RadioButton(self.details, label = 'Week View')
        rb3.Bind(wx.EVT_RADIOBUTTON, self.graph_view)
        rb4 = wx.RadioButton(self.details, label = 'Month View')
        rb4.Bind(wx.EVT_RADIOBUTTON, self.graph_view)
        rb5 = wx.RadioButton(self.details,label='Full Term')
        rb5.Bind(wx.EVT_RADIOBUTTON, self.graph_view)
        rb5.SetValue(True)

        sizer2 = wx.BoxSizer(wx.VERTICAL)
        grid2 = wx.FlexGridSizer(rows=9, cols=1, vgap = 10, hgap = 5)

        grid2.Add(self.label)
        grid2.Add(self.description, 0, wx.EXPAND)
        grid2.AddGrowableRow(1,1)
        grid2.AddGrowableCol(0,1)
        grid2.AddMany([(rb1,0,wx.ALL,5),
                       (rb2,0,wx.ALL,5),
                       (rb3,0,wx.ALL,5),
                       (rb4,0,wx.ALL,5),
                       (rb5,0,wx.ALL,5)])

        sizer2.Add(grid2, 1, wx.ALL | wx.EXPAND, 10)
        self.details.SetSizer(sizer2)

        self.splitter.SplitVertically(self.graph, self.details, int(wx.DisplaySize()[0] * 0.75))
        self.Center()
        
        # Handle exiting and load graph
        self.Bind(wx.EVT_CLOSE, self.close_frame)
        self.load_html_content()
    #end __init__
    
    def load_html_content(self):
        # opens html file and returns it to frame
        with open(r'.\data\chart.html', 'r') as file:
            html_content = file.read()
            self.browser.SetPage(html_content, "")
        #end with
    #end load_html_content

    def graph_view(self, event):
        view = event.GetEventObject().GetLabel()
        if view == "Full Term":
            vsz.visualize(dataset, cvt.get_start_date())
        elif view == "1 Day View":
            vsz.visualize(dataset, self.current_date - datetime.timedelta(hours=12), self.current_date + datetime.timedelta(hours=12))
        elif view == "3 Day View":
            vsz.visualize(dataset, self.current_date, self.current_date + datetime.timedelta(days=2))
        elif view == "Week View":
            vsz.visualize(dataset, self.current_date, self.current_date + datetime.timedelta(days=6))
        elif view == "Month View":
            vsz.visualize(dataset, self.current_date, self.current_date + datetime.timedelta(days=30))
        #end if/elif
        self.load_html_content()
    #end graph_view
    
    def new_tab(self, event):
        # retrieves the description index parameter from a selected Altair action
        url = event.GetURL()
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        title = query_params.get('title')[0].replace(r'$','\n')
        title = title.split()
        self.current_date = datetime.datetime.fromtimestamp(int(title[-1])//1000)
        difference = self.current_date - cvt.get_start_date()
        title[-1] = '\n' + datetime.datetime.fromtimestamp(int(title[-1])//1000).strftime('%B %d, %Y')
        title = ' '.join(title)
        self.display_details(event= wx.EVT_BUTTON, desc_index= int(query_params.get('desc')[0]), title=title, timestep=difference.days)
        event.Skip()
    #end new_tab

    def display_details(self, event, desc_index, title, timestep):
        # shows and updates detail panel using desc_index from new_tab
        with open(r'.\data\descriptions.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for i in range(0,len(lines)):
                lines[i] = lines[i].replace(r'\n', '\n')
            self.timestep = timestep
            description = lines[desc_index-1]
        #end with
        self.event_title = title
        self.label.SetLabel(title)

        self.encountered_hidden = True
        try:
            if self.popup_displayed:
                vsz.remove_confidence()
                self.load_html_content()
            #end if
        except AttributeError:
            pass
        #end try
        self.popup_displayed = False
        self.not_know_comps = True
        self.description.Clear()
        self.description.SetDefaultStyle(wx.TextAttr())
        if title.startswith("Knowledge Components"):
            self.not_know_comps = False
            description = description.split('\n')
            for line in description:
                if line.startswith("Other Encountered Spheres"):
                    self.description.BeginURL(line)
                    self.description.WriteText(line + '\n')
                    self.description.EndURL()
                    self.other_encountered_spheres = description[(description.index(line)+1):]
                    break
                elif line.startswith("No spheres were exposed today."):
                    self.description.WriteText(line + '\n')
                else:
                    self.description.BeginTextColour(self.color_coding(line,1))
                    self.description.BeginURL(line)
                    self.description.WriteText(line + '\n')
                    self.description.EndURL()
                    self.description.EndTextColour()
                #end if/else
            #end for
        elif title.startswith("Quiz") or title.startswith("Homework"):
            description = description.split('\n')
            code_font = False
            self.incorrect = False
            question_end = 0
            answer = []
            backup_answer = []
            for i in range(len(description)):
                if description[i].startswith('A.'):
                    answer.append(description[i].lstrip('A. '))
                    backup_answer.append(description[i].lstrip('A. '))
                    count = 1
                    while True:
                        if description[i+count] == '':
                            break
                        #end if
                        answer.append(description[i+count])
                        backup_answer.append(description[i+count])
                        count += 1
                    #end while
                    # question = '\n'.join(answer[:question_end])
                    answer = '\n'.join(answer)
                    self.backup_ques = '\n'.join(backup_answer[:question_end-1])
                    backup_answer = '\n'.join(backup_answer)
                    self.description.BeginTextColour(self.color_coding(answer,2,backup_answer))
                    self.description.BeginAlignment(wx.TEXT_ALIGNMENT_CENTER)
                    remainder = description[i].lstrip('A. ')
                    if remainder == '```':
                        code_font = not code_font
                    else:
                        #if self.incorrect:
                            #self.description.BeginURL(question)
                            #self.current_answer = description[i].lstrip('A.')
                            #self.description.WriteText(description[i].lstrip('A.') + ' ▼ \n')
                            #self.description.EndURL()
                        #else:
                            self.description.WriteText(description[i].lstrip('A. ') + '\n')
                    #end if/else
                elif re.match(r'Q\d+.', description[i]):
                    self.incorrect = False
                    stripped_ques = ' '.join(description[i].split(' ')[1:])
                    answer = []
                    backup_answer = []
                    answer.append(stripped_ques)
                    backup_answer.append(stripped_ques)
                    count = 1
                    not_seperated = True
                    while True:
                        if description[i+count] == '':
                            break
                        #end if
                        if description[i+count] == '## Example Cases:':
                            answer.append('')
                            backup_answer.append('')
                            not_seperated = False
                        #end if
                        if description[i+count] == '```' and not_seperated:
                            answer.append('')
                            not_seperated = False
                        #end if
                        answer.append(description[i+count])
                        backup_answer.append(description[i+count])
                        count +=1
                    #end while
                    question_end = len(answer)
                    self.description.EndTextColour()
                    self.description.EndAlignment()
                    self.description.SetDefaultStyle(wx.TextAttr())
                    self.description.WriteText(description[i] + '\n')
                elif description[i] == '```':
                    code_font = not code_font
                else:
                    if code_font:
                        self.description.BeginFont(wx.Font(70,wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD,faceName="Courier New"))
                        self.description.WriteText(description[i] + '\n')
                        self.description.EndFont()
                    else:
                        self.description.WriteText(description[i] + '\n')
                #end if
            #end for
        else:
            description = description.split('\n')
            for line in description:
                self.description.BeginURL(line)
                self.description.WriteText(line + '\n')
                self.description.EndURL()
                #end if/else
            #end for
        #end if
        self.description.SetInsertionPoint(0)
        self.details.Layout()
    #end display_details

    def color_coding(self, component, mode, backup = None):
        if mode == 1: #Knowledge Components
            level = cvt.sph_level(self.timestep, component)
            if level == 0:
                return wx.Colour(255,0,0) #red
            elif level == 1:
                return wx.Colour(0,153,0) #green
            elif level == 2:
                return wx.Colour(220,154,30) #orange/yellow
            else:
                return wx.Colour(0,0,0) #black
        elif mode == 2: #Quiz/Homework
            with open(r'.\data\CS1C_references\qa_to_correct.pkl','rb') as file:
                ques_answ = pickle.load(file)
                for qa, correct in ques_answ.items():
                    fixed_qa = qa[0].replace(r'\n\n',r'\n').replace(r'\n', '\n') + '\n' + qa[1].replace(r'\n','\n')
                    if component == fixed_qa and correct:
                        return wx.Colour(0,153,0) #green
                    elif component == fixed_qa:
                        self.incorrect = True
                        return wx.Colour(255,0,0) #red
                    #end if/else
                    if backup == fixed_qa and correct:
                        return wx.Colour(0,153,0) #green
                    elif backup == fixed_qa:
                        self.incorrect = True
                        return wx.Colour(255,0,0) #red
                    #end if/else
                #end for
                return wx.Colour(255,0,0) #red
            #end with
        #end if
    #end color_coding

    def description_click(self, event):
        #if self.event_title.startswith("Quiz") or self.event_title.startswith("Homework:"):
        #    self.answer_popup(event.GetString(), self.current_answer, self.backup_ques)
        sphere = event.GetString()
        if sphere.startswith("Other Encountered Spheres"):
            self.encountered_hidden = not self.encountered_hidden
            if not self.encountered_hidden:
                self.description.SetInsertionPointEnd()
                self.description.Replace(self.description.GetInsertionPoint()-2, self.description.GetInsertionPoint(), '►\n')
                self.encountered_index = self.description.GetInsertionPoint()
                for line in self.other_encountered_spheres:
                    self.description.BeginTextColour(self.color_coding(line,1))
                    self.description.BeginURL(line)
                    self.description.WriteText(line + '\n')
                    self.description.EndURL()
                    self.description.EndTextColour()
                #end for
            else:
                self.description.Remove(self.encountered_index-2, self.description.GetLastPosition())
                self.description.WriteText('▼\n')
            #end if/else
        else:
            if self.popup_displayed:
                vsz.remove_confidence()
                self.load_html_content()
                if sphere == self.last_sphere:
                    self.description.Remove(self.popup_point-2, self.popup_point)
                    self.popup_displayed = False
                else:
                    self.description.Remove(self.popup_point-2, self.popup_point)
                    self.popup_displayed = False
                    self.sphere_popup(sphere, True)
                #end if/else
            else:
                self.sphere_popup(sphere, True)
            #end if/else
        #end if/else
    #end description_click

    def sphere_popup(self, sphere, misconceptions = False):
        text_content = self.description.GetValue()
        pointer_idx = text_content.find(sphere, 0)
        while True:
            if self.description.GetRange(pointer_idx, pointer_idx+1) == '\n':
                break
            #end if
            pointer_idx += 1
        #end while
        self.description.SetInsertionPoint(pointer_idx)
        self.description.WriteText('\n')
        popup_style = wx.richtext.RichTextAttr()
        popup_style.SetFont(wx.Font(70,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_MEDIUM))
        popup_style.SetBackgroundColour(wx.Colour(211,211,211))
        reset_focus = self.description.GetFocusObject()
        self.popup = self.description.WriteTextBox(popup_style)
        self.description.SetFocusObject(self.popup)
        with open(r'.\data\CS1C_references\title_to_description_sphere.pkl','rb') as file:
            sphere_dict = pickle.load(file)
            sphere_desc = sphere_dict[sphere]
            self.description.AppendText(sphere_desc)
        #end with
        if misconceptions:
            if cvt.sph_level(self.timestep, sphere) == 0:
                with open(r'.\data\CS1C_references\sphere_to_mis.pkl', 'rb') as mis_titles:
                    with open(r'.\data\CS1C_references\title_to_description_mis.pkl', 'rb') as mis_descs:
                        title_dict = pickle.load(mis_titles)
                        desc_dict = pickle.load(mis_descs)
                        try:
                            all_miscs = title_dict[sphere]
                            self.description.AddParagraph("")
                            self.description.AddParagraph("Potential Misconceptions:")
                            popup_style.SetFontUnderlined(True)
                            self.popup.GetParagraphAtLine(2).SetAttributes(popup_style)
                            popup_style.SetFontUnderlined(False)
                            popup_style.SetFontStyle(wx.FONTSTYLE_ITALIC)
                            count = 3
                            paragraphs = set()
                            for miscs, stp in cvt.get_held_miscs():
                                if stp == self.timestep:
                                    for sph, mis in miscs:
                                        if sph == sphere:
                                            if mis in all_miscs:
                                                paragraphs.add('  ●  ' + mis + ': ' + desc_dict[mis])
                                            #end if
                                        #end if
                                    #end for
                                #end if
                            #end for
                            for para in paragraphs:
                                self.description.AddParagraph(para)
                                self.popup.GetParagraphAtLine(count).SetAttributes(popup_style)
                                count += 1
                            # end for
                        except KeyError:
                            pass
                    #end with
                #end with
            #end if
        #end if
        self.description.SetFocusObject(reset_focus)
        if self.not_know_comps:
            color = '#000000'
        else:
            color = {0:'#ff0000', 1:'#009900', 2:'#dc9a1e'}[cvt.sph_level(self.timestep, sphere)]
        #end if/else
        conf_df = cvt.generate_confidence(sphere)
        vsz.add_confidence(conf_df, color)
        self.load_html_content()
        
        self.popup_displayed = True
        self.last_sphere = sphere
        self.popup_point = pointer_idx + 2
    #end sphere_popup

    def close_frame(self, event):
        # handles the closing of the browser and window
        self.browser.Close()
        event.Skip()
    #end close_frame
#end MyFrame

class MyApp(wx.App):
    def OnInit(self):
        # sets up wx app and initializes a frame
        self.frame = MyFrame(parent=None, title="explicit Knowledge Trace Visualizer (xKT-Viz)")
        self.frame.Show()
        return True
    #end OnInit
#end MyApp

def main():
    global dataset
    # html file creation (currently uses sample data):
    config = configparser.ConfigParser()
    config.read(r'viz_config.ini')
    start_date = cvt.trace_conversion(config['FIRST']['START DATE'])
    dataset = vsz.data_conversion(r'.\data\visual_data.csv')
    vsz.visualize(dataset, start_date)

    # opens wx app and keeps it running
    app = MyApp()
    app.MainLoop()
#end main

if __name__ == "__main__":
    main()
#end if