import bimpy
import cv2
import os 
import time
# import OpenGL
# import psutil 
import dill   #save and load data in memory
from pathlib import Path
from screeninfo import get_monitors

#playsound('/path/to/a/sound/file/you/want/to/play.mp3')
#pyinstaller -w -F SimplyCued.py
#D:\Documents\GradSchool\Grad Project\VideoEditor\Sample Video



# class CuedSound():
    # try:
    #     audioclip = AudioFileClip(path)
    #     self.soundcap = wave.open(audioclip, 'r')
    # except:
    #     self.soundcap = None

# class MemoryManager():
#     process = psutil.Process(os.getpid())
#     print(process.memory_info()) #pmem(rss=15491072, vms=84025344, shared=5206016, text=2555904, lib=0, data=9891840, dirty=0)


class CuingBlock():
    # play on mouse click or key, 
    # stop on mouse click or key, 
    # play n number of times, and 
    # play for n seconds or milliseconds . 
    Cuetype = None
    kwargs = {}
    def SetCue(self, typ, **kwargs):
        self.Cuetyep = typ

class CuedVideo():
    vidcap = None
    soundcap = None
    framecount = 0
    firstimage = None
    videopath = None
    name = None
    fps = 0
    frame_count = 0
    lastframeid = -1
    lastframe = None
    duration = None
    def LoadVideo(self, videopath):
        try:
            self.videopath = videopath
            self.name = os.path.basename(videopath)
            self.vidcap = cv2.VideoCapture(videopath)
            self.fps = self.vidcap.get(cv2.CAP_PROP_FPS)
            self.frame_count = int(self.vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.duration = self.frame_count/self.vidcap.get(cv2.CAP_PROP_FPS)
            ret, im = self.vidcap.read()
            if ret:
                self.firstimage = cv2.resize(im,(1024,1024),interpolation=cv2.INTER_AREA)
                self.vidcap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            else:
                return -1
        except:
            return -1
        if not self.vidcap.isOpened():
            return -1
    def nextframe(self,frame_number):
        # frame-by-frame
        if frame_number < self.frame_count:
            # temptime = time.time()
            # 
            # bimpy.text('Set Time: {0}'.format(time.time()-temptime))
            if self.lastframeid < frame_number:
                ret, frame = self.vidcap.read()
                if ret:       
                    self.lastframe = frame
                    self.lastframeid = frame_number
                    return frame
                else:
                    return None
            else:
                return self.lastframe
        else: 
            return None
    def CloseVideo(self):
        self.vidcap.release()     
    def Seek(self, f):
        self.vidcap.set(cv2.CV_CAP_PROP_POS_FRAMES, f)  

class Schedular():
    framedone = []
    # Video List
    keylist = []
    cuekeylist = []
    Cueindexlist = []
    indexlist = []
    FullRunTime = 0
    Videodict = dict()
    Cues = dict()
    index = 0
    Cueindex = 0
    ##Test
    test = 0
    def initCue(self, startcon, name):
        self.Cues["{0}{1}".format(name, self.Cueindex)] = {"Name":None, "StartCondition":startcon, "Index":self.Cueindex, 'starttime': None, "Filters":dict(), "Filterindex":0, "FiltersMenu": bimpy.Bool(False)}
        self.Cueindex = self.Cueindex+1
        self.rebuildCuekeylist()
    
    def AddVPLBlock(self, block, cuid, blid, Data):
        for n in self.Cues.keys():
            if self.Cues[n]["Index"] == cuid:
                self.Cues[n]["Filters"]["{0}{1}".format(block, self.Cues[n]["Filterindex"])] = {"Name":None, "Index":self.Cues[n]["Filterindex"], "Data": Data}
                self.Cues[n]["Filterindex"] = self.Cues[n]["Filterindex"] + 1

    def initVideo(self, videopath):
        cuedvideo = CuedVideo()
        ret = cuedvideo.LoadVideo(videopath)
        if not (ret == -1):
            self.Videodict["{0}{1}".format(cuedvideo.name, self.index)] = {'Index':self.index, 'Name':cuedvideo.name, 'Filters':None, 'State':0, 'StartTime':None, 'PlayOffset': 0, 'Video': cuedvideo}
            self.index = self.index+1
            self.FullRunTime = self.FullRunTime + cuedvideo.duration
            self.rebuildVideokeylist()
            return False
        else:
            return True
        
    def MoveVideo(self, Source, Destination):
        name = ""
        keys = self.Videodict.keys()
        for key in keys:
            if Source == self.Videodict[key]['Index']:
                name = key
        if Source < Destination:
            for key in keys:
                if self.Videodict[key]['Index'] <= Destination and self.Videodict[key]['Index'] > Source and self.Videodict[key]['Index'] > 0:
                    self.Videodict[key]['Index'] = self.Videodict[key]['Index']-1
        if Source > Destination:
            for key in keys:
                if self.Videodict[key]['Index'] >= Destination and self.Videodict[key]['Index'] < Source:
                    self.Videodict[key]['Index'] = self.Videodict[key]['Index'] + 1
        self.Videodict[name]['Index'] = Destination
        self.rebuildVideokeylist()
    def MoveCue(self, Source, Destination):
        name = ""
        keys = self.Cues.keys()
        for key in keys:
            if Source == self.Cues[key]['Index']:
                name = key
        if Source < Destination:
            for key in keys:
                if self.Cues[key]['Index'] <= Destination and self.Cues[key]['Index'] > Source and self.Cues[key]['Index'] > 0:
                    self.Cues[key]['Index'] = self.Cues[key]['Index']-1
        if Source > Destination:
            for key in keys:
                if self.Cues[key]['Index'] >= Destination and self.Cues[key]['Index'] < Source:
                    self.Cues[key]['Index'] = self.Cues[key]['Index'] + 1
        self.Cues[name]['Index'] = Destination
        self.rebuildCuekeylist()

    def MoveVPLBlock(self, cue, vid, Source, Destination):
        name = ""
        keys = self.Cues[cue]["Filters"].keys()
        for key in keys:
            if Source == self.Cues[cue]['Filters'][key]['Index']:
                name = key
        if Source < Destination:
            for key in keys:
                if self.Cues[cue]['Filters'][key]['Index'] <= Destination and self.Cues[cue]['Filters'][key]['Index'] > Source and self.Cues[cue]['Filters'][key]['Index'] > 0:
                    self.Cues[cue]['Filters'][key]['Index'] = self.Cues[cue]['Filters'][key]['Index']-1
        if Source > Destination:
            for key in keys:
                if self.Cues[cue]['Filters'][key]['Index'] >= Destination and self.Cues[cue]['Filters'][key]['Index'] < Source:
                    self.Cues[cue]['Filters'][key]['Index'] = self.Cues[cue]['Filters'][key]['Index'] + 1
        self.Cues[cue]['Filters'][name]['Index'] = Destination

    def VideoPlaylist(self, t):
        for x in self.Videodict.keys():
            if self.Videodict[x]['State'] == 1:#1 = get next frame
                f = int((t - self.Videodict[x]['StartTime'] + self.Videodict[x]['PlayOffset']) * self.Videodict[x]['Video'].fps)
                self.framedone.append(f)
                if f >=0 and f <=  self.Videodict[x]['Video'].frame_count:
                    frame =  self.Videodict[x]['Video'].nextframe(f)
                    if frame is not None:
                        h, w, channels = frame.shape
                        #need to add OpenGL code
                        bimpy.image(frame)
                bimpy.text("Frame:{0}\nLastFrame:{1} Diff{2}".format(f, self.test,(f-self.test)))
                bimpy.text('{0}'.format(self.framedone))
                self.test = f
            elif self.Videodict[x]['State'] == 2:#2 == paused video
                if self.Videodict[x]['Video'].lastframe is not None:
                    h, w, channels = self.Videodict[x]['Video'].lastframe().shape
                    #need to add OpenGL code

                    bimpy.text("Frame:{0}\nLastFrame:{1} Diff{2}".format(self.Videodict[x]['Video'].lastframe, self.test,(self.Videodict[x]['Video'].lastframe-self.test)))
                    bimpy.text('{0}'.format(self.framedone))
                    self.test = self.Videodict[x]['Video'].lastframe
            #else 0 means off

        return True

    def removeVideo(self,viid):
        removekey = {}
        if viid is not None:
            for key, value in self.Videodict.items():
                if viid == self.Videodict[key]['Index']:
                    self.Videodict[key]['Video'].CloseVideo()
                    if self.index > 0:
                        self.index = self.index - 1
                else:
                    removekey[key] = self.Videodict[key]
                    if self.Videodict[key]['Index'] > viid and self.Videodict[key]['Index'] > 0:
                        removekey[key]['Index'] = self.Videodict[key]['Index']-1
            self.Videodict = removekey
            self.rebuildVideokeylist()
    def removeCue(self,cuid):
        removekey = {}
        if cuid is not None:
            for key, value in self.Cues.items():
                if cuid == self.Cues[key]['Index']:
                    self.Cues[key]['Video'].CloseVideo()
                    if self.Cueindex > 0:
                        self.Cueindex = self.Cueindex - 1
                else:
                    removekey[key] = self.Cues[key]
                    if self.Cues[key]['Index'] > cuid and self.Cues[key]['Index'] > 0:
                        removekey[key]['Index'] = self.Cues[key]['Index']-1
            self.Cues = removekey
            self.rebuildVideokeylist()
    def active(self):
        if len(self.Videodict.keys()) > 0:
            return True
        else:
            return False
    def rebuildVideokeylist(self):
        self.keylist = []
        self.indexlist = []
        temdic = {}
        temdicindex = {}
        for i in self.Videodict.keys():
            temdic[self.Videodict['{0}'.format(i)]['Index']] = self.Videodict[i]['Name']
            temdicindex[self.Videodict['{0}'.format(i)]['Index']] = i
        for i in range(len(temdic.keys())):
            self.keylist.append(temdic[i])
            self.indexlist.append(temdicindex[i])
    def rebuildCuekeylist(self):
        self.cuekeylist = []
        self.Cueindexlist = []
        temdic = {}
        temdicindex = {}
        for i in self.Cues.keys():
            temdic[self.Cues['{0}'.format(i)]['Index']] = self.Cues[i]['Name']
            temdicindex[self.Cues['{0}'.format(i)]['Index']] = i
        for i in range(len(temdic.keys())):
            self.cuekeylist.append(temdic[i])
            self.Cueindexlist.append(temdicindex[i])
    def runtime(self):
        return self.FullRunTime
    def SetStartTime(self, cname, t):
        self.Cues[cname]['starttime']= t
    def SetStateVideo(self, vname, state):
        if state == 1:
            self.Videodict[vname]['State']= state
            self.Videodict[vname]['StartTime'] = time.time()
        else:
            self.Videodict[vname]['State']= state


#ImGUI Verables
ctx = bimpy.Context()
m = get_monitors()
ctx.init(m[0].width, m[0].height, "SimplyCued")
str = bimpy.String()
SearchFile = bimpy.Bool(False)
PlayVideo = bimpy.Bool(False)
ShowGuide = bimpy.Bool(False)
SelectedVideo = bimpy.String()
payload = bimpy.Int()
Pause = bimpy.Bool(False)
window = bimpy.Vec2(20,20)
windowsize = bimpy.Vec2(200, 200)
searchwindow = bimpy.Vec2(20,20)
searchwindowsize = bimpy.Vec2(200, 200)
Inersize = bimpy.Vec2(0,-45)
Inercuesize = bimpy.Vec2(0,150)
Incuesize = bimpy.Vec2(0,35)

#Screen
# ##### More then one screen?
Screen = None

#save where user last was but start at home
path = os.path.expanduser("~")
lastpath = [os.path.expanduser("~")]
dirlist = []
startvideo = False
Cues = ["Click", "Key", "Repeat", "Time", "Transition"] 
Filter = ["Filter","Mask","View Port"]
State= ["Unchanged", "On", "Off", "Paused"]
ActiveCue = 0

#Navication
search = "*"
rescan = False
Error = False
selectedindex = None

TheSchedular = Schedular()
playtime= 0
runtime = bimpy.Float(0)
starttime = time.time()
curenttime=0
accuracy =5

def Load(file):
    # write a file
    f = open(file, "w")
    dill.dump(TheSchedular, f)
    dill.dump(playtime, f)
    f.close()
def Save(file):
    f = open(file, "r")
    TheSchedular = dill.load(f)
    playtime = dill.load(f)
    f.close()

while(not ctx.should_close()):
    ctx.new_frame()
    bimpy.set_next_window_pos(bimpy.Vec2(20, 20), bimpy.Condition.Once)
    bimpy.set_next_window_size(bimpy.Vec2(800, 500), bimpy.Condition.Once)
    bimpy.begin("Tools")
    menu = bimpy.begin_menu_bar()
    if bimpy.begin_menu('Menu'):
        bimpy.show_style_selector("Style")
        if bimpy.selectable('help'):
            ShowGuide.value = True
        bimpy.end_menu()
    if menu:
        bimpy.end_menu_bar()
    bimpy.text("Time:{0}".format(time.time()))
    if bimpy.button("Add Test Video"):
        videopath = "D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\jellyfish-100-mbps-hd-h264.mkv"
        TheSchedular.initVideo(videopath)
    bimpy.same_line()
    if bimpy.button("Add Test Videos"):
        videopath = ["D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\jellyfish-30-mbps-hd-h264.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\jellyfish-60-mbps-hd-h264.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\jellyfish-100-mbps-hd-h264.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\bird20.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\bird60.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\bird90.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\Family.3gp"]   
        for vidpath in videopath:
            TheSchedular.initVideo(vidpath)
    if bimpy.button("Add Test Cue"):
        TheSchedular.initCue("Click", "Click")
    
    

    # ####################################################
    # ####################################################
    # ####################################################
    bimpy.begin_child("Cues", Incuesize, border=True)
    bimpy.text("Add New Cue")
    for n in Cues:
        bimpy.same_line()
        if bimpy.button(n):
            TheSchedular.initCue(n, "New{0}".format(n))
    bimpy.end_child()
    bimpy.begin_child("Cued", Inercuesize, border=True)
    if not len(TheSchedular.cuekeylist) > 0:
        bimpy.text("No Cues")
    else:
        bimpy.columns(2, "Cued Videos", True)
        bimpy.separator()
        bimpy.text("ID")
        bimpy.next_column()
        bimpy.text("Cues")
        bimpy.next_column()

        bimpy.separator()
        bimpy.set_column_offset(1, 40)
        quemove_from = -1
        quemove_to = -1
        queindex = -1
        for cu in TheSchedular.cuekeylist:
            bimpy.text("{0}. ".format(queindex+1))
            bimpy.next_column()
            queindex=queindex+1
            if ActiveCue == queindex:
                bimpy.push_style_color(bimpy.Button, bimpy.Vec4(1.0, 0.0, 0.0, 0.0))
                if TheSchedular.Cues[TheSchedular.Cueindexlist[queindex]]['Name']:
                    if bimpy.button(TheSchedular.Cues[TheSchedular.Cueindexlist[queindex]]['Name']):
                        ActiveCue = queindex
                else:
                    if bimpy.button(TheSchedular.Cueindexlist[queindex]):
                        ActiveCue = queindex
                bimpy.pop_style_color(1)
            else:
                if TheSchedular.Cues[TheSchedular.Cueindexlist[queindex]]['Name']:
                    if bimpy.button(TheSchedular.Cues[TheSchedular.Cueindexlist[queindex]]['Name']):
                        ActiveCue = queindex
                else:
                    if bimpy.button(TheSchedular.Cueindexlist[queindex]):
                        ActiveCue = queindex
            
            if bimpy.begin_drag_drop_source(bimpy.DragDropFlags.__flags__):
                if (not(bimpy.DragDropFlags.SourceNoDisableHover and bimpy.DragDropFlags.SourceNoHoldToOpenOthers)):# and bimpy.DragDropFlags.SourceNoPreviewTooltip)):
                    bimpy.text("Moving \"%s\"", cu)
                tempval ="{0}".format(queindex)
                bimpy.set_drag_drop_payload_string(tempval)
                payload.value = queindex
                bimpy.end_drag_drop_source()

            bimpy.DragDropFlags.AcceptBeforeDelivery
            bimpy.DragDropFlags.AcceptNoDrawDefaultRect
            if bimpy.begin_drag_drop_target():
                if ("{0}".format(payload.value) == tempval):
                    quemove_from = payload.value
                    quemove_to = queindex
            if (quemove_from != -1 and quemove_to != -1):
                # #Reorder items
                TheSchedular.MoveCue(quemove_from,quemove_to)
                quemove_from = -1
                quemove_to = -1   
            bimpy.next_column()

    bimpy.end_child()

    # ####################################################
    # ####################################################
    # ####################################################
    if bimpy.button("Add Video"):
        rescan = True
        SearchFile.value = True   
    if TheSchedular.active():
        bimpy.same_line()
        if bimpy.button("Delete Video"):
            TheSchedular.removeVideo(selectedindex)
            selectedindex = None
        # bimpy.same_line(spacing_w=50)
    if len(TheSchedular.Cueindexlist) > 0:
        bimpy.begin_child("Videos", Inersize, border=True)
        if not TheSchedular.active():
            bimpy.text("No Vieos")
        else:
            bimpy.columns(4, "Cued Videos", True)
            bimpy.separator()
            bimpy.text("ID")
            bimpy.next_column()
            bimpy.text("Videos")
            bimpy.next_column()
            bimpy.text("State")
            bimpy.next_column()
            bimpy.text("Filters")
            bimpy.next_column()

            bimpy.separator()
            bimpy.set_column_offset(1, 40)
            move_from = -1
            move_to = -1
            index = -1
            for vid in TheSchedular.indexlist:
                bimpy.text("{0}. ".format(index+1))
                bimpy.next_column()
                index=index+1
                if bimpy.button(TheSchedular.Videodict[TheSchedular.indexlist[index]]['Name']):
                    SelectedVideo.value = vid
                    selectedindex = index
                if bimpy.begin_drag_drop_source(bimpy.DragDropFlags.__flags__):
                    if (not(bimpy.DragDropFlags.SourceNoDisableHover and bimpy.DragDropFlags.SourceNoHoldToOpenOthers)):# and bimpy.DragDropFlags.SourceNoPreviewTooltip)):
                        bimpy.text("Moving \"%s\"", vid)
                    tempval ="{0}".format(index)
                    bimpy.set_drag_drop_payload_string(tempval)
                    payload.value = index
                    bimpy.end_drag_drop_source()

                bimpy.DragDropFlags.AcceptBeforeDelivery
                bimpy.DragDropFlags.AcceptNoDrawDefaultRect
                if bimpy.begin_drag_drop_target():
                    if ("{0}".format(payload.value) == tempval):
                        move_from = payload.value
                        move_to = index
                if (move_from != -1 and move_to != -1):
                    # #Reorder items
                    TheSchedular.MoveVideo(move_from,move_to)
                    move_from = -1
                    move_to = -1   
                bimpy.next_column()
                if vid in TheSchedular.Cues[TheSchedular.Cueindexlist[ActiveCue]]["Filters"]:
                    if bimpy.begin_menu(State[TheSchedular.Cues[TheSchedular.Cueindexlist[ActiveCue]]["Filters"][vid]['State']]):
                        for st in State:
                            if bimpy.menu_item(st, 'set', bimpy.Bool(False), True):
                                TheSchedular.Cues[TheSchedular.Cueindexlist[ActiveCue]]["Filters"][vid]['State'] = State.index(st)
                        bimpy.end_menu()
                else:
                    if bimpy.begin_menu('Unchanged'):
                        for st in State:
                            if bimpy.menu_item(st, 'set', bimpy.Bool(False), True):
                                if vid in TheSchedular.Cues[TheSchedular.Cueindexlist[ActiveCue]]["Filters"]:
                                    TheSchedular.Cues[TheSchedular.Cueindexlist[ActiveCue]]["Filters"][vid]['State'] = State.index(st)
                                else:
                                    TheSchedular.Cues[TheSchedular.Cueindexlist[ActiveCue]]["Filters"].update({vid:{'State': State.index(st)}})
                        bimpy.end_menu()
                bimpy.next_column()
                Filterkeys = []
                if len(TheSchedular.Cueindexlist) > 0:
                    if TheSchedular.Cues[TheSchedular.Cueindexlist[ActiveCue]]["Filters"]:
                        Filterkeys = TheSchedular.Cues[TheSchedular.Cueindexlist[ActiveCue]]["Filters"].keys()
                    blockmove_from = -1
                    blockmove_to = -1
                    blockindex = -1
                    if bimpy.begin_menu('Add A Block'):
                        for fil in Filter:
                            if bimpy.menu_item(fil, 'Add', bimpy.Bool(False), True):
                                TheSchedular.AddVPLBlock(fil, ActiveCue, blockindex, None)
                        bimpy.end_menu()
                    if len(Filterkeys) > 0:
                        for que in Filterkeys:
                            bimpy.same_line()
                            blockindex = blockindex + 1
                            if bimpy.begin_menu(que):
                                for n in TheSchedular.Cues[TheSchedular.Cueindexlist[ActiveCue]]["Filters"][que].keys():
                                    bimpy.menu_item(n, 'Add', bimpy.Bool(False), True)
                                bimpy.end_menu()
                            
                            if bimpy.begin_drag_drop_source(bimpy.DragDropFlags.__flags__):
                                if (not(bimpy.DragDropFlags.SourceNoDisableHover and bimpy.DragDropFlags.SourceNoHoldToOpenOthers)):# and bimpy.DragDropFlags.SourceNoPreviewTooltip)):
                                    bimpy.text("Moving \"%s\"", vid)
                                tempval ="{0}".format(blockindex)
                                bimpy.set_drag_drop_payload_string(tempval)
                                payload.value = blockindex
                                bimpy.end_drag_drop_source()

                            bimpy.DragDropFlags.AcceptBeforeDelivery
                            bimpy.DragDropFlags.AcceptNoDrawDefaultRect
                            if bimpy.begin_drag_drop_target():
                                if ("{0}".format(payload.value) == tempval):
                                    blockmove_from = payload.value
                                    blockmove_to = blockindex
                            if (blockmove_from != -1 and blockmove_to != -1):
                                # #Reorder items
                                TheSchedular.MoveBlock(ActiveCue, vid, blockmove_from,blockmove_to)
                                blockmove_from = -1
                                blockmove_to = -1
                else:
                    if bimpy.begin_menu('Add A Block'):
                        for fil in Filter:
                            if bimpy.menu_item(fil, 'Add', bimpy.Bool(False), True):
                                TheSchedular.AddVPLBlock(fil, ActiveCue, blockindex, None)
                        bimpy.end_menu()
                bimpy.next_column()
        bimpy.end_child()
        
        if bimpy.button("Play"):
            PlayVideo.value = True
            startvideo = True
            Pause.value = False
        # bimpy.same_line()
        # if bimpy.button("Restart"):
        #         startvideo=True
        #         Pause.value = False
        bimpy.same_line()
        if bimpy.button("Stop"):
            startvideo=True
            Pause.value = False
            PlayVideo.value = False
        # bimpy.same_line()
        # if bimpy.button("Pause"):
        #     if Pause.value:
        #         PlayVideo.value = True
        #         Pause.value = False
        #         starttime = time.time()
        #     else:
        #         Pause.value = True
        #         playtime = curenttime
        # if bimpy.slider_float("Play Back", runtime, 0.0, TheSchedular.FullRunTime):
        #     if not Pause.value:
        #         starttime = time.time()
        #     playtime = runtime.value


    bimpy.end()
    if PlayVideo.value:
        bimpy.set_next_window_pos(window, bimpy.Condition.Once)
        bimpy.set_next_window_size(windowsize, bimpy.Condition.Once)
        bimpy.begin("PlayVideo",PlayVideo, flags=(bimpy.WindowFlags.NoTitleBar))
        if startvideo:
            startvideo = False
            starttime = time.time()
            playtime = 0
        if not Pause.value:
            curenttime = (time.time() - starttime)
            runtime.value = curenttime + playtime
        if TheSchedular.active(): 
            if TheSchedular.runtime() > runtime.value:
                pl = 0
                tmlist = TheSchedular.VideoPlaylist(runtime.value)
                if not tmlist:
                    startvideo=True
                    Pause.value = False
                    PlayVideo.value = False      
            else:
                startvideo=True
                PlayVideo.value = False
                Pause.value = False
        bimpy.end()

    if ShowGuide.value:
        bimpy.set_next_window_pos(bimpy.Vec2(20, 20), bimpy.Condition.Once)
        bimpy.set_next_window_size(bimpy.Vec2(500, 300), bimpy.Condition.Once)
        bimpy.begin("User Guide", ShowGuide)
        bimpy.show_user_guide()
        bimpy.end

    if SearchFile.value:
        videopath1 = None
        ret = -1
        bimpy.set_next_window_pos(searchwindow, bimpy.Condition.Once)
        bimpy.set_next_window_size(searchwindowsize, bimpy.Condition.Once)
        bimpy.begin("Search", SearchFile)
        if rescan:
            dirlist= Path(path).glob(search)
            rescan = False
        if bimpy.button("Prev"):
            path = lastpath.pop()
            rescan = True
        bimpy.same_line()    
        if bimpy.button("<-"):
            lastpath.append(path)
            path = os.path.split(path)[0]
            rescan = True
        bimpy.same_line()
        ChangePath = None
        text_val = bimpy.String(path)
        ChangePath = bimpy.input_text('path', text_val, 256, flags=(bimpy.InputTextFlags.EnterReturnsTrue))
        if ChangePath:
            try: 
                if Path(text_val.val).is_file():
                    videopath1 = text_val.value
            except:
                try:
                    if Path(text_val.value).is_dir():
                        path = text_val.value
                        rescan = True
                except:
                    bimpy.text("Invalid Path")
        bimpy.same_line()
        if bimpy.button("{0}".format(search)):
            bimpy.open_popup("Search")
            bimpy.same_line()
        if bimpy.begin_popup("Search"):
            types = []
            files = [x for x in dirlist if x.is_file()]
            types = ['*'+x.suffix.lower() for x in files if x.suffix.lower() not in types and x.suffix is not '']
            types = list(dict.fromkeys(types))
            types.append("*")
            for x in types:
                if bimpy.selectable(x):
                    search = x
            bimpy.end_popup()
        bimpy.begin_child(path)
        bimpy.separator()
        tempdirlist = []
        for fileordir in dirlist:
            tempdirlist.append(fileordir)
            if fileordir.is_dir():
                if bimpy.selectable("(Dir)" + fileordir.name + "/"):
                    lastpath.append(path)
                    path = fileordir._str
                    rescan = True
            else:
                if bimpy.selectable(fileordir.name):
                    videopath1 = fileordir._str
        dirlist = tempdirlist
        bimpy.end_child()
        if videopath1:
            cued = Schedular.initVideo(videopath1)
            if cued:
                Error = True       
            else:
                SearchFile.value = False
        if Error:
            bimpy.begin("Error",bimpy.Bool(Error), flags=(bimpy.WindowFlags.NoResize|bimpy.WindowFlags.NoMove|bimpy.WindowFlags.NoTitleBar))
            bimpy.text("{0}".format("Could not load file"))
            if bimpy.button("OK"):
                Error = False
            bimpy.end()
        bimpy.end()
    ctx.render()