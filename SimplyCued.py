import bimpy
import cv2
import copy
import os 
from pathlib import Path
from os.path import expanduser
from screeninfo import get_monitors
#playsound('/path/to/a/sound/file/you/want/to/play.mp3')
#pyinstaller -w -F SimplyCued.py
#D:\Documents\GradSchool\Grad Project\VideoEditor\Sample Video

class CuedVideo():
    vidcap = None
    soundcap = None
    framecount = 0
    customsize = False
    firstimage = None
    path = None
    name = None
    height = 0
    width = 0
    def LoadVideo(self, path):
        try:
            size = (175, 85)
            self.path = path
            self.name = os.path.basename(path)
            self.vidcap = cv2.VideoCapture(path)
            ret, im = self.vidcap.read()
            self.vidcap.release()
            self.vidcap = cv2.VideoCapture(path)
            self.firstimage = cv2.resize(im,size,interpolation=(cv2.INTER_AREA))
        except:
            return -1
        try:
            audioclip = AudioFileClip(path)
            self.soundcap = wave.open(audioclip, 'r')
        except:
            self.soundcap = None
        if not self.vidcap.isOpened():
            return -1
    def rendernextimage(self):
        # frame-by-frame
        ret, frame = self.vidcap.read()
        if ret:
            self.framecount=self.framecount+1
            h, w, channels = frame.shape
            self.SizeVideo(h, w)
            ctx.init(self.height, self.width, "Image")
            im = bimpy.Image(frame)
            
            s = None
            #if self.soundcap:
                #s = self.soundcap.readframes(1)
            return im, s
        else:
            frame = 0
            return False, None
    def SizeVideo(self, h, w):
        if self.customsize:
            return
        self.height = h
        self.width = w
    def CustomSizeVideo(self, h, w, c):
        self.customsize = c
        self.height = h
        self.width = w
    def ReloadVideo(self):
        self.vidcap.release()
        self.vidcap = cv2.VideoCapture(self.path)
    def CloseVideo(self):
        self.vidcap.release()

def RemoveVideo(viname, viid):
    TheSchedular.removeVideo(viid)
    if viname not in TheSchedular.GetVideoPlaylist() and viname in Videos.keys() and not viname == '':
        Videos[viname].CloseVideo()
        del Videos[viname]

class Schedular():
    VideoCue = dict()
    index = 0
    def ShedualVideo(self,videoname):
        if videoname not in self.VideoCue.keys():
            self.VideoCue[videoname] = [self.index]
            self.index = self.index+1
        else:
            temp = self.VideoCue[videoname]
            temp.append(self.index)
            self.VideoCue[videoname] = temp
            self.index = self.index+1
        return self.VideoCue[videoname]
    def MoveVideo(self, Source, Destination):
        newlist = []
        nextlist = []
        Destname = []
        name = ""
        for key in self.VideoCue.keys():
            newlist.extend(self.VideoCue[key])
            if Destination in self.VideoCue[key]:
                Destname.append(key)
            elif Source in self.VideoCue[key]:
                name = key
        self.VideoCue[name] = [x for x in self.VideoCue[name] if not x == Source]
        if Source < Destination:
            for key in self.VideoCue.keys():
                if not key == name and len(self.VideoCue[key]) > 0:
                    self.VideoCue[key] = [(x-1) if x <= Destination and x > Source and x > 0 else x for x in self.VideoCue[key]]
        if Source > Destination:
            for key in self.VideoCue.keys():
                if not key == name and len(self.VideoCue[key]) > 0:
                    self.VideoCue[key] = [(x+1) if  x >= Destination and x < Source and x < len(newlist) else x for x in self.VideoCue[key]]
        newlist.remove(Destination)
        for key in self.VideoCue.keys():
            nextlist.extend(self.VideoCue[key])
        if name not in self.VideoCue.keys():
            self.VideoCue[name] = [Destination]
        else:
            if Destination not in self.VideoCue[name]:
                self.VideoCue[name].append(Destination)
        if len(self.VideoCue[name]) < 1:
            self.removeVideoempty(name)
    def GetVideoPlaylist(self):
        runing = dict()
        for vid in self.VideoCue.keys():
            for x in self.VideoCue[vid]:
                runing[x] = vid
        ret = []
        for i in range(len(runing)):
            ret.append(runing[i])
        return ret
    def removeVideo(self,viid):
        removekey = []
        if viid is not None:
            for key in self.VideoCue.keys():
                if viid in self.VideoCue[key]:
                    self.VideoCue[key].remove(viid)
                self.VideoCue[key] = [(x-1) if x > viid else x for x in self.VideoCue[key]]
            for key in self.VideoCue.keys():
                if not len(self.VideoCue[key])>0:
                    removekey.append(key)
            for key in removekey:
                self.removeVideoempty(key)
            if self.index > 0:
                self.index = self.index - 1
    def removeVideoempty(self,viname):
        if not viname == '':
            del self.VideoCue[viname]
    def unschedual(self,Sourceindex):
        self.VideoCue[Sourceindex] = [x for x in self.VideoCue[Sourceindex] if not x == Sourceindex]
    def active(self):
        if len(self.VideoCue.keys()) > 0:
            return True
        else:
            return False


#ImGUI Verables
ctx = bimpy.Context()
m = get_monitors()
ctx.init(m[0].width, m[0].height, "SimplyCued")
str = bimpy.String()
count = bimpy.Int()
SearchFile = bimpy.Bool(False)
PlayVideo = bimpy.Bool(False)
Cue = bimpy.Bool(True)
ShowGuide = bimpy.Bool(False)
EditStyle = bimpy.Bool(False)
SelectedVideo = bimpy.String()
payload = bimpy.Int()

#save where user last was but start at home
path = expanduser("~")
lastpath = [expanduser("~")]

# Video List
Videos = dict()
TheSchedular = Schedular()

#Screen
# ##### More then one screen?
ctx.init(0, 0, "Image")
Screen = None
dirlist = []
WindowW = m[0].width
WindowH = m[0].height

#Navication
Browse = False
search = "*"
rescan = False
Error = False
selectedindex = None
playing = 0



while(not ctx.should_close()):
    ctx.new_frame()
    bimpy.set_next_window_pos(bimpy.Vec2(20, 20), bimpy.Condition.Once)
    bimpy.set_next_window_size(bimpy.Vec2(800, 500), bimpy.Condition.Once)
    bimpy.begin("Tools")
    menu = bimpy.begin_menu_bar()
    if bimpy.begin_menu('Menu'):
        bimpy.show_style_selector("Style")
        if bimpy.selectable('Edit Style'):
            EditStyle.value = True
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
            Videos[cuedvideo.name] =cuedvideo
            TheSchedular.ShedualVideo(cuedvideo.name)
    bimpy.same_line()
    if bimpy.button("Add Test Videos"):
        videopath = ["D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\jellyfish-30-mbps-hd-h264.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\jellyfish-60-mbps-hd-h264.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\jellyfish-100-mbps-hd-h264.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\bird20.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\bird60.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\bird90.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\Family.3gp"]
        
        for vidpath in videopath:
            cuedvideo = CuedVideo()
            ret = cuedvideo.LoadVideo(vidpath)
            if not (ret == -1):
                Videos[cuedvideo.name] =cuedvideo
                TheSchedular.ShedualVideo(cuedvideo.name)
    if bimpy.button("Add Video"):
        rescan = True
        SearchFile.value = True   
    if TheSchedular.active():
        bimpy.same_line()
        if bimpy.button("Delete Video"):
            RemoveVideo(SelectedVideo.value, selectedindex)
        bimpy.same_line(spacing_w=50)
        if bimpy.button("play"):
            PlayVideo.value = True
        if PlayVideo.value:
            bimpy.same_line()
            if bimpy.button("Pause"):
                PlayVideo.value = False
            bimpy.same_line()
            if bimpy.button("Stop"):
                PlayVideo.value = False
                for x in Videos.keys():
                    Videos[x].ReloadVideo()
    bimpy.begin_child("Cue", border=True)
    #bimpy.begin_drag_drop_source(0)
    #bimpy.end_drag_drop_source()
    #bimpy.begin_drag_drop_target() 
    #bimpy.end_drag_drop_target()
    if not TheSchedular.active():
        bimpy.text("No Vieos in Cue")
    else:
        index = -1
        move_from = -1
        move_to = -1
        for vid in TheSchedular.GetVideoPlaylist():
            bimpy.text("{0}. ".format(index+1))
            bimpy.same_line()
            index=index+1
            # bimpy.selectable(vid)
            if bimpy.button(vid):
                SelectedVideo.value = vid
                selectedindex = index
            # bimpy.same_line()
            # bimpy.image(bimpy.Image(Videos[vid].firstimage))
            #bimpy.DragDropFlags.SourceNoDisableHover
            #bimpy.DragDropFlags.SourceNoHoldToOpenOthers
            #bimpy.DragDropFlags.SourceNoPreviewTooltip
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
            #bimpy.begin_child(vid, bimpy.Vec2(200, 100), border=True)
            #ctx.init(175, 85, "Image")
            
            #bimpy.end_child()
    
    bimpy.end_child()
    bimpy.end()

    if PlayVideo.value:
        bimpy.set_next_window_pos(bimpy.Vec2(20, 20), bimpy.Condition.Once)
        bimpy.set_next_window_size(bimpy.Vec2(1400, 800), bimpy.Condition.Once)
        bimpy.begin("PlayVideo",PlayVideo, flags=(bimpy.WindowFlags.NoTitleBar))
        if TheSchedular.active() and playing < len(TheSchedular.GetVideoPlaylist()):
            Screen, Sound = Videos[TheSchedular.GetVideoPlaylist()[playing]].rendernextimage()
            if Screen == False: 
                Videos[TheSchedular.GetVideoPlaylist()[playing]].ReloadVideo()
                playing = playing + 1                    
            else:
                bimpy.image(Screen)
                if Sound:
                    playsound(Sound)

        elif not playing < len(TheSchedular.GetVideoPlaylist()):
            PlayVideo.value = False
            playing = 0
        else:
            bimpy.text("No video selected")
        bimpy.end()

    if EditStyle.value:
        bimpy.set_next_window_pos(bimpy.Vec2(20, 20), bimpy.Condition.Once)
        bimpy.set_next_window_size(bimpy.Vec2(335, 250), bimpy.Condition.Once)
        bimpy.begin("Edit Style", EditStyle)
        bimpy.show_style_editor()
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
        if bimpy.button("Prev"):
            path = copy.deepcopy(lastpath.pop())
            rescan = True
        bimpy.same_line()    
        if bimpy.button("<-"):
            lastpath.append(copy.deepcopy(path))
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
                    lastpath.append(copy.deepcopy(path))
                    path = fileordir._str
                    rescan = True
            else:
                if bimpy.selectable(fileordir.name):
                    videopath = fileordir._str
        bimpy.end_child()
        if videopath:
            cuedvideo = CuedVideo()
            ret = cuedvideo.LoadVideo(videopath)
            if not (ret == -1):
                Videos[cuedvideo.name] = cuedvideo
                TheSchedular.ShedualVideo(cuedvideo.name)
                SearchFile.value = False
            else:
                Error = True
        if Error:
            bimpy.begin("Error",bimpy.Bool(Error), flags=(bimpy.WindowFlags.NoResize|bimpy.WindowFlags.NoMove|bimpy.WindowFlags.NoTitleBar))
            bimpy.text("{0}".format("Could not load file"))
            if bimpy.button("OK"):
                Error = False
            bimpy.end()
        bimpy.end()
    ctx.render()