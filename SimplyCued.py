import bimpy
import cv2
import os 
import time
import pyopengl
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

class Clock():
    starttime = time.perf_counter()
    playtime = 0
    def gettime(self):
        self.playtime = self.playtime + time.perf_counter() - self.starttime
        return self.playtime
    def pause(self):
        self.starttime = time.perf_counter()

class CuedVideo():
    vidcap = None
    soundcap = None
    framecount = 0
    firstimage = None
    videopath = None
    name = None
    fps = 0
    frame_count = 0
    duration = None
    def LoadVideo(self, videopath):
        try:
            self.videopath = videopath
            self.name = os.path.basename(videopath)
            self.vidcap = cv2.VideoCapture(videopath)
            self.fps = self.vidcap.get(cv2.CAP_PROP_FPS)      # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
            self.frame_count = int(self.vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.duration = self.frame_count/self.fps
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
    def nextframe(self,t,frame_number):
        # frame-by-frame

        if self.Playing(t, frame_number):
            self.vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame_number-1)
            ret, frame = self.vidcap.read()
            if ret:
                self.framecount=self.framecount+1          
                return frame
            else:
                frame = 0
                return None
        else: 
            return None
    def CloseVideo(self):
        self.vidcap.release()
    def Playing(self, t, f):
        if type(t) == float:
            if f < self.frame_count:
                return True
            else: 
                return False
        else:
            return False
def RemoveVideo(viname, viid):
    TheSchedular.removeVideo(viid)
    if viname not in TheSchedular.GetVideoList() and viname in Videos.keys() and not viname == '':
        Videos[viname].CloseVideo()
        del Videos[viname]

class Schedular():
    # Video List
    Videos = dict()
    startvideo = False
    runclock = None
    FullRunTime = 0
    VideoCue = dict()
    index = 0
    def CueVideo(self, videopath):
        cuedvideo = ()
        ret = cuedvideo.LoadVideo(videopath)
        if not (ret == -1):
            self.Videos[cuedvideo.name] = cuedvideo
            self.ShedualVideo(cuedvideo.name)
            return False
        else:
            return True
    def ShedualVideo(self,videoname):
        if videoname not in self.VideoCue.keys():
            self.VideoCue[videoname] = {'index':[self.index]}
        else:
            self.VideoCue[videoname]['index'].append(self.index)
        self.VideoCue[videoname]["Frames"] = {"{0}".format(self.index):0}
        self.VideoCue[videoname]["starttime"] = {"{0}".format(self.index):self.FullRunTime}
        self.index = self.index+1
        self.FullRunTime = self.FullRunTime + self.VideoCue[videoname].duration
    def MoveVideo(self, Source, Destination):
        newlist = []
        Destname = []
        tempframe = None
        name = ""
        for ind in self.VideoCue.keys():
            for key in key
            newlist.extend(self.VideoCue[key]['index'])
            if Destination in self.VideoCue[key]['index']:
                Destname.append(key)
            elif Source in self.VideoCue[key]['index']:
                name = key
        frame = self.VideoCue[name]["Frames"]["{0}".format(Source)]
        del self.VideoCue[name]["Frames"]["{0}".format(Source)]
        self.VideoCue[name]['index'] = [x for x in self.VideoCue[name]['index'] if not x == Source]
        if Source < Destination:
            for key in self.VideoCue.keys():
                if not key == name and len(self.VideoCue[key]['index']) > 0:
                    for fra in self.VideoCue[key]['Frames'].keys():
                        if int(fra) <= Destination and int(fra) > Source and int(fra) > 0:
                            self.VideoCue[key]['Frames']["{0}".format(int(fra)-1)] = self.VideoCue[key]['Frames'].pop(fra)
        if Source > Destination:
            for key in self.VideoCue.keys():
                if not key == name and len(self.VideoCue[key]['index']) > 0:
                    for fra in self.VideoCue[key]['Frames'].keys():
                        if int(fra) >= Destination and int(fra) < Source and int(fra) < len(newlist):
                            newone = int(fra)+1
                            self.VideoCue[key]['Frames']["{0}".format(newone)] =  self.VideoCue[key]['Frames'].pop(fra)
        # ##Test
        newlist.remove(Destination)
        listtmp = []
        for x in self.VideoCue.keys():
            listtmp.extend([int(i) for i in self.VideoCue[x]["Frames"].keys()])

        if len(set(newlist) - set(listtmp)) > 0:
            tem = 0
        # ####

        if name not in self.VideoCue.keys():
            self.VideoCue[name]['index'] = [Destination]
        else:
            if Destination not in self.VideoCue[name]['index']:
                self.VideoCue[name]['index'].append(Destination)
        self.VideoCue[name]["Frames"]["{0}".format(Destination)] = tempframe
        if len(self.VideoCue[name]['index']) < 1:
            self.removeVideoempty(name)
    def GetVideoList(self):
        runing = dict()
        for vid in self.VideoCue.keys():
            for x in self.VideoCue[vid]['index']:
                runing[x] = vid
        ret = []
        for i in range(len(runing)):
            ret.append(runing[i])
        return ret
    def Seek(self, vid, vname, fra):
        self.VideoCue[vname]['Frames']["{0}".format(vid)] = fra
    def GetVideoPlaylist(self):
        playingVideos = [x for x in self.Videos if self.Videos[x].Playing(fra) and if runclock.gettime() >= self.VideoCue[vname][vid]["starttime"] and not runclock.gettime() > (self.VideoCue[vname][vid]["starttime"] + self.Videos[vname].duration)]
        return playingVideos
    def removeVideo(self,viid):
        removekey = []
        if viid is not None:
            for key in self.VideoCue.keys():
                if viid in self.VideoCue[key]['index']:
                    self.VideoCue[key]['index'].remove(viid)
                self.VideoCue[key]['index'] = [(x-1) if x > viid else x for x in self.VideoCue[key]['index']]
            for key in self.VideoCue.keys():
                if not len(self.VideoCue[key]['index'])>0:
                    removekey.append(key)
            for key in removekey:
                self.removeVideoempty(key)
            if self.index > 0:
                self.index = self.index - 1
    def removeVideoempty(self,viname):
        if not viname == '':
            del self.VideoCue[viname]
    def active(self):
        if len(self.VideoCue.keys()) > 0:
            return True
        else:
            return False
    def RestVideos(self):
        for x in self.Videos.keys():
            for i in self.Videos[]
            self.Seek(pl["id"], pl["Name"],0) self.Videos[x]
    def GetNextFrame(self, n, f):
        frame = self.Videos[n].nextframe(runclock.gettime(),f)
        h, w, channels = frame.shape
        im = bimpy.Image(frame)
        return im, h, w
    def StartClock(self):
        self.runclock = Clock()
    def SetStartTime(self,vid, vname, t):
        self.Videos[vname][''].StartTime()


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

#Screen
# ##### More then one screen?
Screen = None

#save where user last was but start at home
path = os.path.expanduser("~")
lastpath = [os.path.expanduser("~")]
dirlist = []

#Navication
search = "*"
rescan = False
Error = False
selectedindex = None
playing = 0
editdict= dict(ViewPort=bimpy.Bool(False), Mask=bimpy.Bool(False), CodeBlocks=bimpy.Bool(False))


TheSchedular = Schedular()

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
    if bimpy.button("Add Test Video"):
        videopath = "D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\jellyfish-100-mbps-hd-h264.mkv"
        cuedvideo = CuedVideo()
        ret = cuedvideo.LoadVideo(videopath)
        if not (ret == -1):
            TheSchedular.Videos[cuedvideo.name] =cuedvideo
            TheSchedular.ShedualVideo(cuedvideo.name)
    bimpy.same_line()
    if bimpy.button("Add Test Videos"):
        videopath = ["D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\jellyfish-30-mbps-hd-h264.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\jellyfish-60-mbps-hd-h264.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\jellyfish-100-mbps-hd-h264.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\bird20.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\bird60.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\bird90.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\Family.3gp"]
        
        for vidpath in videopath:
            cuedvideo = CuedVideo()
            ret = cuedvideo.LoadVideo(vidpath)
            if not (ret == -1):
                TheSchedular.Videos[cuedvideo.name] =cuedvideo
                TheSchedular.ShedualVideo(cuedvideo.name)
    if bimpy.button("Add Video"):
        rescan = True
        SearchFile.value = True   
    if TheSchedular.active():
        bimpy.same_line()
        if bimpy.button("Delete Video"):
            RemoveVideo(SelectedVideo.value, selectedindex)
            selectedindex = None
        bimpy.same_line(spacing_w=50)
        if bimpy.button("play"):
            PlayVideo.value = True
            startvideo=True
        if PlayVideo.value:
            bimpy.same_line()
            if bimpy.button("Pause"):
                PlayVideo.value = False
            bimpy.same_line()
            if bimpy.button("Stop"):
                PlayVideo.value = False
                TheSchedular.RestVideos()
    bimpy.begin_child("Cue", border=True)

    if not TheSchedular.active():
        bimpy.text("No Vieos in Cue")
    else:
        bimpy.columns(2, "Cued Videos", True)
        bimpy.separator()
        bimpy.text("ID")
        bimpy.next_column()
        bimpy.text("Videos")
        bimpy.next_column()

        bimpy.separator()
        bimpy.set_column_offset(1, 40)
        move_from = -1
        move_to = -1
        index = -1
        for vid in TheSchedular.GetVideoList():
            bimpy.text("{0}. ".format(index+1))
            bimpy.next_column()
            index=index+1
            if bimpy.button(vid):
                SelectedVideo.value = vid
                selectedindex = index
                bimpy.open_popup("Edit Video {0}".format(vid))
            if bimpy.begin_popup("Edit Video {0}".format(vid)):
                bimpy.same_line()
                bimpy.text("Edit Video's")
                bimpy.separator()
                for edkey in editdict.keys():
                    if bimpy.selectable(edkey):
                        for edkey2 in editdict.keys():
                            if edkey2 == edkey:
                                editdict[edkey].value = True
                            else:
                                editdict[edkey].value = False
                bimpy.end_popup()
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
                #tmpval = bimpy.accept_drag_drop_payload_string(bimpy.DragDropFlags.__flags__)
                if ("{0}".format(payload.value) == tempval):
                    move_from = payload.value
                    move_to = index
            if (move_from != -1 and move_to != -1):
                # Reorder items
                TheSchedular.MoveVideo(move_from,move_to)
                move_from = -1
                move_to = -1
            
            bimpy.next_column()
            #bimpy.begin_child(vid, bimpy.Vec2(200, 100), border=True)
            #ctx.init(175, 85, "Image")
            
            #bimpy.end_child()
    
    bimpy.end_child()
    bimpy.end()

    if PlayVideo.value:
        if TheSchedular.active() and playing < len(TheSchedular.GetVideoPlaylist()):
            if startvideo:
                TheSchedular.StartClock()
                startvideo = False
            pl = 0
            for pl in TheSchedular.GetVideoPlaylist():
                if not Pause.value:
                    Screen, height. width = TheSchedular.GetNextFrame(pl["Name"],pl["Frame"])
                    ctx.init(height, width, "Image")
                if Screen: 
                    bimpy.set_next_window_pos(window.value, bimpy.Condition.Once)
                    bimpy.set_next_window_size(windowsize.value, bimpy.Condition.Once)
                    bimpy.begin("PlayVideo",PlayVideo, flags=(bimpy.WindowFlags.NoTitleBar))
                    bimpy.image(Screen)
                else:
                    playing = playing + 1                                        

            if not playing < len(TheSchedular.GetVideoPlaylist()):
                if bimpy.button("Restart"):
                    TheSchedular.RestVideos()
                    playing = 0
                if bimpy.button("Stop"):
                    TheSchedular.RestVideos()
                    PlayVideo.value = False
                    playing = 0
            if bimpy.invisible_button("Pause/Play",windowsize.value):
                if Pause.value:
                    Pause.value = False
                else:
                    Pause.value = True
        bimpy.end()

    if ShowGuide.value:
        bimpy.set_next_window_pos(bimpy.Vec2(20, 20), bimpy.Condition.Once)
        bimpy.set_next_window_size(bimpy.Vec2(500, 300), bimpy.Condition.Once)
        bimpy.begin("User Guide", ShowGuide)
        bimpy.show_user_guide()
        bimpy.end

    if SearchFile.value:
        videopath = None
        ret = -1
        bimpy.set_next_window_pos(bimpy.Vec2(850, 20), bimpy.Condition.Once)
        bimpy.set_next_window_size(bimpy.Vec2(600, 400), bimpy.Condition.Once)
        bimpy.begin("Search", SearchFile)
        if rescan:
            dirlist= Path(path).glob(search)
            rescan = False
        if bimpy.button("Prev"):
            path = lastpath.pop()
            rescan = True
        bimpy.same_line()    
        if bimpy.button("<-"):
            lastpath.append((path)
            path = os.path.split(path)[0]
            rescan = True
        bimpy.same_line()
        ChangePath = None
        text_val = bimpy.String(path)
        ChangePath = bimpy.input_text('path', text_val, 256, flags=(bimpy.InputTextFlags.EnterReturnsTrue))
        if ChangePath:
            try: 
                if Path(text_val.val).is_file():
                    videopath = text_val.value
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
        for fileordir in dirlist:
            if fileordir.is_dir():
                if bimpy.selectable("(Dir)" + fileordir.name):
                    lastpath.append(path)
                    path = fileordir._str
                    rescan = True
            else:
                if bimpy.selectable(fileordir.name):
                    videopath = fileordir._str
        bimpy.end_child()
        if videopath:
            cued = Schedular.CueVideo(videopath)
            if cued:
                Error = True       
            else:
                SearchFile.value = False
        if Error:
            bimpy.begin("Error",bimpy.Bool(Error), flags=(bimpy.WindowFlags.NoResize|bimpy.WindowFlags.NoMove|bimpy.WindowFlags.NoTitleBar))
            bimpy.text("{0}".format("Could not load file"))
            if bimpy.button("OK")CuedVideo:
                Error = False
            bimpy.end()
        bimpy.end()
    ctx.render()