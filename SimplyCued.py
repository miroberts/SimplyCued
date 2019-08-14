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

class Schedular():
    framedone = []
    # Video List
    keylist = []

    FullRunTime = 0
    VideoCue = dict()
    index = 0
    ##Test
    test = 0
    def CueVideo(self, videopath):
        cuedvideo = CuedVideo()
        ret = cuedvideo.LoadVideo(videopath)
        if not (ret == -1):
            self.VideoCue["{0}{1}".format(cuedvideo.name, self.index)] = {"Index":self.index, 'Name':cuedvideo.name,'starttime':self.FullRunTime, 'Video': cuedvideo}
            self.index = self.index+1
            self.FullRunTime = self.FullRunTime + cuedvideo.duration
            self.rebuildkeylist()
            return False
        else:
            return True
        
    def MoveVideo(self, Source, Destination):
        name = ""
        keys = self.VideoCue.keys()
        for key in keys:
            if Source == self.VideoCue[key]['Index']:
                name = key
        if Source < Destination:
            for key in keys:
                if self.VideoCue[key]['Index'] <= Destination and self.VideoCue[key]['Index'] > Source and self.VideoCue[key]['Index'] > 0:
                    self.VideoCue[key]['Index'] = self.VideoCue[key]['Index']-1
        if Source > Destination:
            for key in keys:
                if self.VideoCue[key]['Index'] >= Destination and self.VideoCue[key]['Index'] < Source:
                    self.VideoCue[key]['Index'] = self.VideoCue[key]['Index'] + 1
        self.VideoCue[name]['Index'] = Destination
        self.rebuildkeylist()
    def GetVideoList(self):
        return self.keylist
    def GetVideoPlaylist(self, t):
        for x in self.VideoCue.keys():
            f = int((t - self.VideoCue[x]['starttime']) * self.VideoCue[x]['Video'].fps)
            self.framedone.append(f)
            if f >=0 and f <=  self.VideoCue[x]['Video'].frame_count:
                frame =  self.VideoCue[x]['Video'].nextframe(f)
                if frame is not None:
                    h, w, channels = frame.shape
                    im = bimpy.Image(frame)
                    if im:
                        ctx.init(h, w, "Image")
                        bimpy.image(im) 
                    else:
                        return False
                else:
                    return False
            bimpy.text("Frame:{0}\nLastFrame:{1} Diff{2}".format(f, self.test,(f-self.test)))
            bimpy.text('{0}'.format(self.framedone))
            self.test = f
        return True
    def removeVideo(self,viid):
        removekey = {}
        if viid is not None:
            for key, value in self.VideoCue.items():
                if viid == self.VideoCue[key]['Index']:
                    self.VideoCue[key]['Video'].CloseVideo()
                    if self.index > 0:
                        self.index = self.index - 1
                else:
                    removekey[key] = self.VideoCue[key]
                    if self.VideoCue[key]['Index'] > viid and self.VideoCue[key]['Index'] > 0:
                        removekey[key]['Index'] = self.VideoCue[key]['Index']-1
            self.VideoCue = removekey
            self.rebuildkeylist()
    def active(self):
        if len(self.VideoCue.keys()) > 0:
            return True
        else:
            return False
    def rebuildkeylist(self):
        self.keylist = []
        temdic = {}
        for i in self.VideoCue.keys():
            temdic[self.VideoCue['{0}'.format(i)]['Index']] = self.VideoCue[i]['Name']
        for i in range(len(temdic.keys())):
            self.keylist.append(temdic[i])
    def runtime(self):
        return self.FullRunTime
    def SetStartTime(self,vid, vname, t):
        self.VideoCue[vname][vid]['starttime']= t
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

starttime = time.time()
def Seek(self, t):
    starttime = time.time()

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
        TheSchedular.CueVideo(videopath)
    bimpy.same_line()
    if bimpy.button("Add Test Videos"):
        videopath = ["D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\jellyfish-30-mbps-hd-h264.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\jellyfish-60-mbps-hd-h264.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\jellyfish-100-mbps-hd-h264.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\bird20.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\bird60.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\bird90.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\Family.3gp"]   
        for vidpath in videopath:
            TheSchedular.CueVideo(vidpath)
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
            starttime = time.time()
        temptime = (time.time() - starttime)
        if TheSchedular.active(): 
            if TheSchedular.runtime() > temptime:
                pl = 0
                tmlist = TheSchedular.GetVideoPlaylist(temptime)
                if not tmlist:
                    startvideo=True
                    Pause.value = False
                    PlayVideo.value = False      
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
                        starttime = time.time()
                    else:
                        Pause.value = True
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