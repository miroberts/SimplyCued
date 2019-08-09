import bimpy
import cv2
import os 
import time
#import pyopengl
import psutil 
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

class Clock():
    starttime = time.time()
    playtime = 0
    def gettime(self):
        self.playtime = self.playtime + time.time() - self.starttime
        return self.playtime
    def play(self):
        self.starttime = time.time()

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
    duration = None
    def LoadVideo(self, videopath):
        try:
            self.videopath = videopath
            self.name = os.path.basename(videopath)
            self.vidcap = cv2.VideoCapture(videopath)
            self.fps = (1000/self.vidcap.get(cv2.CAP_PROP_FPS))
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
            self.vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame_number-1)
            ret, frame = self.vidcap.read()
            if ret:       
                return frame
            else:
                return None
        else: 
            return None
    def CloseVideo(self):
        self.vidcap.release()       

class Schedular():
    framedone = []
    # Video List
    Videos = dict()
    runclock = None
    FullRunTime = 0
    VideoCue = dict()
    index = 0
    ##Test
    test = 0
    def CueVideo(self, videopath):
        cuedvideo = CuedVideo()
        ret = cuedvideo.LoadVideo(videopath)
        if not (ret == -1):
            self.Videos[cuedvideo.name] = cuedvideo
            self.ShedualVideo(cuedvideo.name)
            return False
        else:
            return True
    def ShedualVideo(self,videoname):
        if videoname not in self.VideoCue.keys():
            self.VideoCue[videoname] = {"{0}".format(self.index):{'starttime':self.FullRunTime}}
        else:
            self.VideoCue[videoname]["{0}".format(self.index)] = {'starttime':self.FullRunTime}
        self.index = self.index+1
        self.FullRunTime = self.FullRunTime + self.Videos[videoname].duration* 1000
    def MoveVideo(self, Source, Destination):
        newlist = []
        Destname = []
        tempinfo = None
        name = ""
        for key in self.VideoCue.keys():
            newlist.extend(self.VideoCue[key].keys())
            if "{0}".format(Destination) in self.VideoCue[key].keys():
                Destname.append(key)
            elif "{0}".format(Source) in self.VideoCue[key].keys():
                name = key
        tempinfo = self.VideoCue[name].pop("{0}".format(Source))
        if Source < Destination:
            for key in self.VideoCue.keys():
                newone = 0
                tempone = {}
                for ind in self.VideoCue[key].keys():
                    if int(ind) <= Destination and int(ind) > Source and int(ind) > 0:
                        newone = int(ind)-1
                        tempone["{0}".format(newone)] = self.VideoCue[key][ind]
                    else:
                        tempone["{0}".format(ind)] = self.VideoCue[key][ind]
                self.VideoCue[key] = tempone
        if Source > Destination:
            for key in self.VideoCue.keys():
                newone = 0
                tempone = {}
                for ind in self.VideoCue[key].keys():
                    if int(ind) >= Destination and int(ind) < Source and int(ind) < len(newlist):
                        newone = int(ind)+1
                        tempone["{0}".format(newone)] = self.VideoCue[key][ind]
                    else:
                        tempone["{0}".format(ind)] = self.VideoCue[key][ind]
                self.VideoCue[key] =  tempone
        # ##Test
        # newlist.remove("{0}".format(Destination))
        # listtmp = []
        # for x in self.VideoCue.keys():
        #     listtmp.extend([i for i in self.VideoCue[x].keys()])
        # if len(set(newlist) - set(listtmp)) > 0:
        #     tem = 0
        # ####
        self.VideoCue[name]["{0}".format(Destination)] = tempinfo
        if len(self.VideoCue[name].keys()) < 1:
            self.removeVideoempty(name)
    def GetVideoList(self):
        runing = dict()
        for vid in self.VideoCue.keys():
            for x in self.VideoCue[vid].keys():
                runing[x] = vid

        for i in range(len(runing)):
            ret.append(runing["{0}".format(i)])
        return ret
    def Seek(self, t):
        self.runclock.playtime = t
        self.runclock.play()
    def GetVideoPlaylist(self):
        playingVideos = {}
        for x in self.GetVideoList():
            for i in self.VideoCue[x].keys():
                tim = self.runclock.gettime()
                f = tim - self.VideoCue[x][i]['starttime'] * self.Videos[x].fps
                self.framedone.append(f)
                if f >=0 and f <= self.Videos[x].frame_count:
                    im, h, w = self.GetNextFrame(x,int(f))
                    playingVideos[i] = {"im":im,"h":h,"w":w}
                    if self.VideoCue[x][i].get('VLP'):
                        playingVideos[i]["VLP"] = self.VideoCue[x][i]['VLP']
            bimpy.text("Frame:{0} = Gettime:{1} - starttime:{2} * fps:{3}\nLastFrame:{4} Diff{5}".format(f,tim, self.VideoCue[x][i]['starttime'], self.Videos[x].fps,self.test,(f-self.test)))
            self.test = f
        if len(playingVideos)> 1:
            alk = False
        return playingVideos
    def removeVideo(self,viid):
        removekey = []
        if viid is not None:
            for key in self.VideoCue.keys():
                if viid in self.VideoCue[key].keys():
                    del self.VideoCue[key][viid]
                newone = 0
                tempone = {}
                for ind in self.VideoCue[key].keys():
                    if int(ind) > viid and int(ind) > 0:
                        newone = int(ind)-1
                        tempone["{0}".format(newone)] = self.VideoCue[key][ind]
                    else:
                        tempone["{0}".format(ind)] = self.VideoCue[key][ind]
                self.VideoCue[key] = tempone
            for key in self.VideoCue.keys():
                if not len(self.VideoCue[key].keys())>0:
                    removekey.append(key)
            for key in removekey:
                self.removeVideoempty(key)
            if self.index > 0:
                self.index = self.index - 1
    def removeVideoempty(self,viname):
        if not viname == '':
            del self.VideoCue[viname]
            del self.Videos[viname]
    def active(self):
        if len(self.VideoCue.keys()) > 0:
            return True
        else:
            return False
    def GetNextFrame(self, n, f):
        frame = self.Videos[n].nextframe(f)
        h, w, channels = frame.shape
        im = bimpy.Image(frame)
        return im, h, w
    def StartClock(self):
        self.runclock = Clock()
    def SetStartTime(self,vid, vname, t):
        self.VideoCue[vname][vid]['starttime']= t
    def PlayClock(self):
        self.runclock.play() #Pause
    def ActivePlay(self):
        return self.runclock.gettime()<self.FullRunTime
    def cuevplblock(self, videoid,type,starttime,**kwargs):
        #Where kwargs holds the info needed for the type of VPLblock being made. 
        #The result is returned as success or not. 
        return True


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

#Screen
# ##### More then one screen?
Screen = None

#save where user last was but start at home
path = os.path.expanduser("~")
lastpath = [os.path.expanduser("~")]
dirlist = []
startvideo = False

#Navication
search = "*"
rescan = False
Error = False
selectedindex = None
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
            TheSchedular.removeVideo(selectedindex)
            selectedindex = None
        bimpy.same_line(spacing_w=50)
        if not PlayVideo.value:
            if bimpy.button("play"):
                PlayVideo.value = True
                startvideo = True
                Pause.value = False
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
                if ("{0}".format(payload.value) == tempval):
                    move_from = payload.value
                    move_to = index
            if (move_from != -1 and move_to != -1):
                # #Reorder items
                TheSchedular.MoveVideo(move_from,move_to)
                move_from = -1
                move_to = -1
            bimpy.next_column()    
    bimpy.end_child()
    bimpy.end()
    if PlayVideo.value:
        bimpy.set_next_window_pos(window, bimpy.Condition.Once)
        bimpy.set_next_window_size(windowsize, bimpy.Condition.Once)
        bimpy.begin("PlayVideo",PlayVideo, flags=(bimpy.WindowFlags.NoTitleBar))
        if startvideo:
            startvideo = False
            TheSchedular.StartClock()
        if TheSchedular.active() and TheSchedular.ActivePlay():
            
            pl = 0
            tmlist = TheSchedular.GetVideoPlaylist()
            for pl in tmlist:
                if not Pause.value:
                    Screen = tmlist[pl]['im'] 
                    ctx.init(tmlist[pl]['h'], tmlist[pl]['w'], "Image")
                if Screen: 
                    bimpy.image(Screen)                                       

            if Pause.value:
                if bimpy.button("Restart"):
                    startvideo=True
                    Pause.value = False
                    bimpy.same_line()
                if bimpy.button("Stop"):
                    startvideo=True
                    Pause.value = False
                    PlayVideo.value = False
            if bimpy.invisible_button("Pause/Play",windowsize):
                if Pause.value:
                    PlayVideo.value = True
                    Pause.value = False
                    TheSchedular.PlayClock()
                else:
                    Pause.value = True
            if 0 == len(tmlist) and TheSchedular.ActivePlay():
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
        videopath = None
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
            if bimpy.button("OK"):
                Error = False
            bimpy.end()
        bimpy.end()
    ctx.render()