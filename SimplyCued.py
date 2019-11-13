import imgui
import cv2
import os 
import time
import glfw
import OpenGL.GL as gl
from imgui.integrations.glfw import GlfwRenderer
from PIL import Image as Img
import numpy as np
from mathutils import Matrix
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

class Renderer():
    def __init__(self):
        # Create a windowed mode window and its OpenGL context
        m = get_monitors()

        VerShadeText = None
        try:
            with open('VerShadeText.hlsl', 'r') as file:
                VerShadeText = file.read()
        except:
            exit()

    

        VerShader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        gl.glShaderSource(VerShader, VerShadeText)
        gl.glCompileShader(VerShader)
        error = gl.glGetShaderiv(VerShader, gl.GL_COMPILE_STATUS)
        if error != gl.GL_TRUE:
            info = gl.glGetShaderInfoLog(VerShader)
            raise Exception(info)
        

        FragShadeText = None
        try:
            with open('FragShadeText.hlsl', 'r') as file:
                FragShadeText = file.read()
        except:
            exit()
        FragShader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        gl.glShaderSource(FragShader, FragShadeText)
        gl.glCompileShader(FragShader)
        error = gl.glGetShaderiv(FragShader, gl.GL_COMPILE_STATUS)
        if error != gl.GL_TRUE:
            info = gl.glGetShaderInfoLog(FragShader)
            raise Exception(info)


        self.program = gl.glCreateProgram()
        gl.glAttachShader(self.program, VerShader)
        gl.glAttachShader(self.program, FragShader)
        gl.glLinkProgram(self.program) 
        error = gl.glGetProgramiv(self.program, gl.GL_LINK_STATUS)
        if error != gl.GL_TRUE:
            info = gl.glGetShaderInfoLog(self.program)
            raise Exception(info)

        gl.glDeleteShader(VerShader)
        gl.glDeleteShader(FragShader)
        
        self.buff = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buff)
        square = [0.0, 1.0,0.0,0.0,0.0,0.0,1.0,1.0,0.0,1.0,0.0,0.0]
        data = np.array(square, np.float32)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, data.nbytes, data, gl.GL_STATIC_DRAW)
        
        self.vPos = gl.glGetAttribLocation(self.program, 'vPos')
        self.vTex = gl.glGetAttribLocation(self.program, "vTex")

        self.vNgt = gl.glGetAttribLocation(self.program, "vNgt")
        
        gl.glEnableVertexAttribArray(self.vPos)
        gl.glEnableVertexAttribArray(self.vTex)

        self.projectionMatrix = gl.glGetUniformLocation(self.program, "projection")
        self.modelViewMatrix = gl.glGetUniformLocation(self.program, "modelView")

        self.texture = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)

        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)

        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)



        

    def rend(self, frame, Data):
        gl.glUseProgram(self.program)
        mvMatrix=[]
        for da in Data.keys():
            if 'mvMatrix' in da:
                mvMatrix = Data[da]['Data']
            if 'Color' in da:
                if Data[da]['Data']['Nagitive']:
                    self.vNgt = 1
                else:
                    self.vNgt = 0
        gl.glUniformMatrix4fv(self.modelViewMatrix, 1, gl.GL_FALSE, mvMatrix)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buff)
        gl.glVertexAttribPointer(self.vPos, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        gl.glVertexAttribPointer(self.vTex, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        gl.glVertexAttribPointer(self.vTex, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        txFrame = Img.fromarray(frame)
        shpx = txFrame.size[0]
        shpy = txFrame.size[1]
        txFrame = txFrame.tobytes('raw', 'BGRX', 0, -1)
        

        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, shpx, shpy, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE,txFrame)
        
        



        gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)


        
        
        

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
            if self.vidcap.get(cv2.CAP_PROP_FPS) > 0:
                self.duration = self.frame_count/self.vidcap.get(cv2.CAP_PROP_FPS)
            else:
                self.duration = 0
            ret, im = self.vidcap.read()
            self.x_axis = 0.0
            self.y_axis = 0.0
            self.z_axis = 0.0
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
            # imgui.text('Set Time: {0}'.format(time.time()-temptime))
            if self.lastframeid < frame_number:
                ret, frame = self.vidcap.read()
                if ret:       
                    self.lastframe = frame
                    self.lastframeid = frame_number
                    return frame
                else:
                    return None
            elif self.lastframe is not None:
                return self.lastframe
            else:
                return None
        else: 
            return None
    def CloseVideo(self):
        self.vidcap.release()     
    def Seek(self, f):
        #cvSetCaptureProperty(self.vidcap, CV_CAP_POS_FRAMES, f)
        self.vidcap.set(2,f)  

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
    EditFilters = False
    EditInfo = None
    movieindex = 0
    SearchFile = False
    PlayVideo = False
    ShowGuide = False
    ShowStyle = False
    SelectedVideo = ""
    payload = 0
    Pause = False
    windowpos = imgui.Vec2(20,20)
    windowsize = imgui.Vec2(200, 200)
    searchwindow = imgui.Vec2(20,20)
    searchwindowsize = imgui.Vec2(200, 200)
    Inersize = imgui.Vec2(0,-45)
    Inercuesize = imgui.Vec2(0,150)
    Incuesize = imgui.Vec2(0,35)

    #save where user last was but start at home
    path = os.path.expanduser("~")
    lastpath = [os.path.expanduser("~")]
    dirlist = []
    startvideo = False
    CuesList = ["Click", "Key", "Repeat", "Time", "Transition"] 
    Filter = ["Filter","Mask","View Port"]
    State= ["Unchanged", "On", "Off", "Paused"]
    ActiveCue = 0
    StagedCue = 0

    #Navication
    search = "*"
    rescan = False
    Error = False
    selectedindex = None
    Repeated = 0

    def __init__(self):
        self.renderer = Renderer()

    def initCue(self, startcon, name):
        self.Cues["{0}{1}".format(name, self.Cueindex)] = {"Name":name, "StartCondition":startcon, "Index":self.Cueindex, 'starttime': None, "Filters":dict(), "Filterindex":0}
        for vid in range(len(self.Videodict.keys())):
            self.AddVPLBlock(self.index, 'mvMatrix', self.Cueindex, np.array([
                1.0, 0.0,  0.0, 0.0,
                0.0, 1.0,  0.0, 0.0,
                0.0, 0.0,  1.0, 0.0,
                0.0, 0.0, 0.0, 1.0], np.float32))
            self.AddVPLBlock(vid, 'Color', self.Cueindex, {"Red": [0,.5] , "Green": [0,.5], "Blue" : [0,.5], "Nagitive": False})
        self.Cueindex = self.Cueindex+1
        self.rebuildCuekeylist()
    
    def AddVPLBlock(self, vid, block, cuid, data):
        for n in self.Cues.keys():
            if self.Cues[n]["Index"] == cuid:
                self.Cues[n]["Filters"]["{0}{1}".format(block, self.Cues[n]["Filterindex"])] = {"Name":block, "Index":self.Cues[n]["Filterindex"], 'Data': data, 'videoindex':vid, "Menu": False}
                self.Cues[n]["Filterindex"] = self.Cues[n]["Filterindex"] + 1
        #TheSchedular.Cues[TheSchedular.Cueindexlist[ActiveCue]]["Filters"][vid]['Menu']
    def initVideo(self, videopath):
        cuedvideo = CuedVideo()
        ret = cuedvideo.LoadVideo(videopath)
        if not (ret == -1):
            self.Videodict["{0}{1}".format(cuedvideo.name, self.index)] = {'Index':self.index, 'Name':cuedvideo.name, 'Filters':None, 'State':0, 'StartTime':None, 'PlayOffset': 0, 'StartFrame':1, 'Video': cuedvideo}
            
            for cu in range(len(self.CuesList)):
                self.AddVPLBlock(self.index, 'mvMatrix', cu, np.array([
                    1.0, 0.0,  0.0, 0.0,
                    0.0, 1.0,  0.0, 0.0,
                    0.0, 0.0,  1.0, 0.0,
                    0.0, 0.0, 0.0, 1.0], np.float32))
                self.AddVPLBlock(self.index, 'Color', cu, {"Red": [0,.5] , "Green": [0,.5], "Blue" : [0,.5], "Nagitive": False})
            self.index = self.index+1
            self.FullRunTime = self.FullRunTime + cuedvideo.duration
            self.rebuildVideokeylist()
            self.SetVideos(self.ActiveCue)
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

    def VideoPlaylist(self, edit):
        for x in self.Videodict.keys():
            frame = None
            if edit and (self.Videodict[x]['State'] == 1 or self.Videodict[x]['State'] == 2):
                self.renderer.rend(self.Videodict[x]['Video'].firstimage,self.Videodict[x]["Filters"])
            else:
                if self.Videodict[x].get("Filters"):
                    if self.Videodict[x]["Filters"]['State'] == 1:#1 = get next frame
                        f = int((time.time() - self.Videodict[x]['StartTime'] + self.Videodict[x]['PlayOffset']) * self.Videodict[x]['Video'].fps)
                        self.framedone.append(f)
                        if f >=0 and f <=  self.Videodict[x]['Video'].frame_count:
                            frame =  self.Videodict[x]['Video'].nextframe(f)
                            if frame is not None:
                                self.renderer.rend(frame,self.Videodict[x]["Filters"])
                                
                    elif self.Videodict[x]["Filters"]['State'] == 2:#2 == paused video
                        if self.Videodict[x]['Video'].lastframe is not None:
                            frame = self.Videodict[x]['Video'].lastframe
                            self.renderer.rend(frame,self.Videodict[x]["Filters"])
            
                #else 0 means off

    # def applyfilters(self, viid, frame, ):
    #     return frame
    #     finishedFrame = frame
    #     h, w, channels = frame.shape
    #     for fil in self.Videodict[viid]["Filters"]:
    #         if fil == "Resize":
    #             # https://stackoverflow.com/questions/4195453/how-to-resize-an-image-with-opencv2-0-and-python2-6
    #             finishedFrame = cv2.resize(finishedFrame, self.Videodict[viid]["Filters"]['Resize'])
    #         elif fil == 'Mask':
    #             # https://stackoverflow.com/questions/10469235/opencv-apply-mask-to-a-color-image
    #             # https://www.programcreek.com/python/example/85661/cv2.bitwise_and
    #             finishedFrame = cv2.bitwise_and(finishedFrame,self.Videodict[viid]["Filters"]['Mask'])
    #         elif fil == 'Viewport':
    #             # https://stackoverflow.com/questions/18573784/how-can-i-resample-a-subarea-of-an-image-for-a-viewport-application
    #             finishedFrame = cv2.remap(finishedFrame,self.Videodict[viid]["Filters"]['Remap']['map1'], self.Videodict[viid]["Filters"]['Remap']['map2'])
    #         elif fil == 'Blur':
    #             # https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_filtering/py_filtering.html
    #             # https://www.tutorialkart.com/opencv/python/opencv-python-gaussian-image-smoothing/
    #             finishedFrame = cv2.GaussianBlur(finishedFrame,self.Videodict[viid]["Filters"]['Blur']['ksize'],self.Videodict[viid]["Filters"]['Blur']['sigma'])
    #         elif fil == 'Color':
    #             # https://stackoverflow.com/questions/50716214/python-opencv-apply-colored-mask-to-image
    #             finishedFrame = np.power(finishedFrame, self.Videodict[viid]["Filters"]['Color'])

    #     return finishedFrame

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
    def getcue(self, cue):
        cuename = None
        for c in self.Cues.keys():
            if self.Cues[c]['Index'] == cue:
                cuename = c
        return cuename
    def SetVideos(self, cue):
        cuename = self.getcue(cue)
        if cuename:
            for vname in  self.Videodict.keys():
                if self.Videodict[vname]["Filters"]:
                    self.Videodict[vname]["Filters"].update(self.Cues[cuename]["Filters"])
                elif self.Cues[cuename]["Filters"].get(vname):
                    self.Videodict[vname]["Filters"] = self.Cues[cuename]["Filters"].get(vname)
                    if self.Cues[cuename]["Filters"][vname]['State'] == 1:
                        self.Videodict[vname]['StartTime'] = time.time()
        else:
            n = 3

    def Reload(self, vname):
        self.Videodict[vname]['Video'].Seek(self.Videodict[vname]['StartFrame'])
    def ReloadAll(self):
        self.FullRunTime = 0
        for vname in self.Videodict.keys():
            self.Reload(vname)
            self.Videodict[vname]["Filters"] = None
            self.Videodict[vname]['StartTime'] = None
            self.Videodict[vname]['Video'].lastframeid = 0

    def AdvanceCue(self):
        if TheSchedular.Cueindex <= self.StagedCue:
            self.PlayVideo = False
            self.startvideo = False
            self.Pause = False
            self.StagedCue = 0
            self.ActiveCue = 0
            self.ReloadAll()
            self.SetVideos(self.ActiveCue)
        else:
            self.PlayVideo = True
            self.startvideo = True
            self.Pause = False
            tmp = self.StagedCue + 1
            self.ActiveCue = self.StagedCue
            self.StagedCue = tmp
            self.SetVideos(self.ActiveCue)
            

#imgui Setup
m = get_monitors()
# ctx.init(m[0].width, m[0].height, "SimplyCued")

FirstWindow = imgui.Vec2(int(m[0].width), int(m[0].height))

imgui.create_context()

if not glfw.init():
    print("Could not initialize OpenGL context")
    exit(1)

# Create a windowed mode window and its OpenGL context
window = glfw.create_window(
    FirstWindow.x, FirstWindow.y, "SimplyCued", None, None
)
glfw.make_context_current(window)

if not window:
    glfw.terminate()
    print("Could not initialize Window")
    exit(1)

def windowResize(windo, inx, iny):
    w, h = glfw.get_framebuffer_size(windo)
    gl.glViewport(0, 0, w, h)

glfw.set_window_size_callback(window, windowResize)

impl = GlfwRenderer(window)

TheSchedular = Schedular()

Debug = None
Debug = True

#Screen
# ##### More then one screen?
Screen = None
playtime= 0
runtime = 0.0
starttime = time.time()
curenttime=0
accuracy =5


def Load(self, file):
    # write a file
    f = open(file, "w")
    dill.dump(TheSchedular, f)
    dill.dump(playtime, f)
    f.close()
# def Save(file):
#     f = open(file, "r")
#     TheSchedular = dill.load(f)
#     playtime = dill.load(f)
#     f.close()


while(not glfw.window_should_close(window)):
    gl.glClearColor(0., 0., 0., 1)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    glfw.poll_events()
    impl.process_inputs()

    if TheSchedular.PlayVideo:
        if TheSchedular.startvideo:
            TheSchedular.SetVideos(TheSchedular.ActiveCue)
            TheSchedular.startvideo = False
            starttime = time.time()
            playtime = 0

        if TheSchedular.active(): 
            if TheSchedular.runtime() > runtime:
                pl = 0
                TheSchedular.VideoPlaylist(False)
                runtime = time.time() - starttime
            else:
                TheSchedular.startvideo=True
                TheSchedular.PlayVideo = False
                TheSchedular.Pause = False

        if TheSchedular.Cueindex-1 > TheSchedular.ActiveCue:
            NextCue = TheSchedular.Cues[TheSchedular.getcue(TheSchedular.ActiveCue+1)]
            if NextCue['StartCondition'] == 'Click':
                if imgui.is_mouse_clicked(0, False):
                    AdvanceCue()
            elif NextCue['StartCondition'] == 'Key':
                if imgui.is_key_pressed(0,False): # is_key_down(,):
                    AdvanceCue()
            elif NextCue['StartCondition'] == 'Repeat':
                if Repeated <= NextCue['Repeat']:
                    AdvanceCue()
            elif NextCue['StartCondition'] == 'Time':
                if playtime >= NextCue['starttime'] - NextCue['RunTime']:
                    AdvanceCue()
            elif NextCue['StartCondition'] == 'Transition':
                ##### https://stackoverflow.com/questions/28650721/cv2-python-image-blending-fade-transition

                # fading
                # sliding in/out
                # pushing in/out
                TheSchedular.AdvanceCue()
    else:

        imgui.new_frame()

        imgui.set_next_window_position(20, 20, imgui.ONCE)
        imgui.set_next_window_size(800, 500, imgui.ONCE)
        imgui.begin("Tools", False, imgui.WINDOW_MENU_BAR)
        if imgui.begin_menu_bar():
            if imgui.begin_menu('Menu', True):
                # imgui.show_style_selector("Style")
                if imgui.selectable('Style')[0]:
                    TheSchedular.ShowStyle = True
                if imgui.selectable('Help')[0]:
                    TheSchedular.ShowGuide = True
                imgui.end_menu()
            imgui.end_menu_bar()

        imgui.begin_child("Cues", TheSchedular.Incuesize.x, TheSchedular.Incuesize.y, border=True)
        imgui.text("Add New Cue")
        for n in TheSchedular.CuesList:
            imgui.same_line()
            if imgui.button(n):
                TheSchedular.initCue(n, "New{0}".format(n))
        imgui.end_child()
        imgui.begin_child("Cued", TheSchedular.Inercuesize.x, TheSchedular.Inercuesize.y, border=True)
        if not len(TheSchedular.cuekeylist) > 0:
            imgui.text("No Cues")
        else:
            imgui.columns(2, "Cued Videos", True)
            imgui.separator()
            imgui.text("ID")
            imgui.next_column()
            imgui.text("Cues")
            imgui.next_column()

            imgui.separator()
            imgui.set_column_offset(1, 40)
            quemove_from = -1
            quemove_to = -1
            queindex = -1
            for cu in TheSchedular.cuekeylist:
                imgui.text("{0}. ".format(queindex+1))
                imgui.next_column()
                queindex=queindex+1
                if TheSchedular.ActiveCue == queindex:
                    if TheSchedular.Cues[TheSchedular.Cueindexlist[queindex]]['Name']:
                        imgui.same_line(spacing=50)
                        if imgui.button('{0} {1}'.format(queindex,TheSchedular.Cues[TheSchedular.Cueindexlist[queindex]]['Name'])):
                            TheSchedular.ActiveCue = queindex
                    else:
                        if imgui.button('{0} {1}'.format(queindex,TheSchedular.Cueindexlist[queindex])):
                            TheSchedular.ActiveCue = queindex
                else:
                    if TheSchedular.Cues[TheSchedular.Cueindexlist[queindex]]['Name']:
                        if imgui.button('{0} {1}'.format(queindex,TheSchedular.Cues[TheSchedular.Cueindexlist[queindex]]['Name'])):
                            TheSchedular.ActiveCue = queindex
                    else:
                        if imgui.button('{0} {1}'.format(queindex,TheSchedular.Cueindexlist[queindex])):
                            TheSchedular.ActiveCue = queindex
                
                # if imgui.core.BeginDragDropSource():
                #     if (not(imgui.DRAG_DROP_SOURCE_NO_DISABLE_HOVER and imgui.DRAG_DROP_SOURCE_NO_HOLD_TO_OPEN_OTHERS)):# and imgui.DragDropFlags.SourceNoPreviewTooltip)):
                #         imgui.text("Moving \"%s\"", cu)
                #     tempval ="{0}".format(queindex)
                #     TheSchedular.payload = queindex
                #     imgui.end()
                # if imgui.begin_drag_drop_target(imgui.DRAG_DROP_ACCEPT_BEFORE_DELIVERY, imgui.DRAG_DROP_ACCEPT_NO_DRAW_DEFAULT_RECT):
                #     if ("{0}".format(TheSchedular.payload) == tempval):
                #         quemove_from = TheSchedular.payload
                #         quemove_to = queindex
                # if (quemove_from != -1 and quemove_to != -1):
                #     # #Reorder items
                #     TheSchedular.MoveCue(quemove_from,quemove_to)
                #     quemove_from = -1
                #     quemove_to = -1   
                imgui.next_column()

        imgui.end_child()

        
        if len(TheSchedular.Cueindexlist) > 0:
            if imgui.button("Add Video"):
                TheSchedular.rescan = True
                TheSchedular.SearchFile = True   
            if TheSchedular.active():
                imgui.same_line()
                if imgui.button("Delete Video"):
                    TheSchedular.removeVideo(TheSchedular.selectedindex)
                    TheSchedular.selectedindex = None
            imgui.begin_child("Videos", TheSchedular.Inersize.x, TheSchedular.Inersize.y, border=True)
            if not TheSchedular.active():
                imgui.text("No Vieos")
            else:
                imgui.columns(4, "Cued Videos", True)
                imgui.separator()
                imgui.text("ID")
                imgui.next_column()
                imgui.text("Videos")
                imgui.next_column()
                imgui.text("Filters")
                imgui.next_column()
                imgui.text("State")
                imgui.next_column()
            

                imgui.separator()
                imgui.set_column_offset(1, 40)
                move_from = -1
                move_to = -1
                index = -1
                for vid in TheSchedular.indexlist:
                    imgui.text("{0}. ".format(index+1))
                    imgui.next_column()
                    index=index+1
                    if imgui.button('{0}{1}'.format(index,TheSchedular.Videodict[TheSchedular.indexlist[index]]['Name'])):
                        TheSchedular.SelectedVideo = vid
                        TheSchedular.selectedindex = index
                    # if imgui.begin_drag_drop_source(imgui.DragDropFlags.__flags__):
                    #     if (not(imgui.DragDropFlags.SourceNoDisableHover and imgui.DragDropFlags.SourceNoHoldToOpenOthers)):# and imgui.DragDropFlags.SourceNoPreviewTooltip)):
                    #         imgui.text("Moving \"%s\"", vid)
                    #     tempval ="{0}".format(index)
                    #     imgui.set_drag_drop_payload_string(tempval)
                    #     TheSchedular.payload = index
                    #     imgui.end_drag_drop_source()

                    # imgui.DragDropFlags.AcceptBeforeDelivery
                    # imgui.DragDropFlags.AcceptNoDrawDefaultRect
                    # if imgui.begin_drag_drop_target():
                    #     if ("{0}".format(payload) == tempval):
                    #         move_from = payload
                    #         move_to = index
                    # if (move_from != -1 and move_to != -1):
                    #     # #Reorder items
                    #     TheSchedular.MoveVideo(move_from,move_to)
                    #     move_from = -1
                    #     move_to = -1   
                    
                    imgui.next_column()
                    Filterkeys = []
                    if TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"]:
                        Filterkeys = TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"].keys()
                    blockindex = -1
                    if imgui.selectable('{0} Edit Filters'.format(TheSchedular.movieindex))[0]:
                        TheSchedular.EditInfo = TheSchedular.movieindex
                        TheSchedular.EditFilters = True
                        TheSchedular.SetVideos(TheSchedular.ActiveCue)
                    TheSchedular.movieindex = TheSchedular.movieindex + 1
                    if TheSchedular.movieindex >= len(TheSchedular.Videodict.keys()):
                        TheSchedular.movieindex = 0
                    if len(Filterkeys) > 0:
                        for fill in Filterkeys:
                            blockindex = blockindex + 1
                            tp = TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][fill].get('videoindex')
                            if TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][fill].get('videoindex') or TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][fill].get('videoindex') == 0:
                                if index == TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][fill]['videoindex']:
                                    imgui.new_line()
                                    imgui.same_line(spacing=50)
                                    imgui.text(TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][fill]['Name'])

                    imgui.next_column()
                    if vid in TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"]:
                        if imgui.begin_menu("{0} {1}".format(index,TheSchedular.State[TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][vid]['State']])):
                            for st in TheSchedular.State:
                                if imgui.selectable(st)[0]:
                                    TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][vid]['State'] = TheSchedular.State.index(st)
                            imgui.end_menu()
                    else:
                        if imgui.begin_menu("{0} Unchanged".format(index), True):
                            for st in TheSchedular.State:
                                if imgui.selectable(st)[0]:
                                    if vid in TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"]:
                                        TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][vid]['State'] = TheSchedular.State.index(st)
                                    else:
                                        TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"].update({vid:{'State': TheSchedular.State.index(st)}})
                            imgui.end_menu()
                    imgui.next_column()
            imgui.end_child()
            
        if TheSchedular.ShowGuide:
            imgui.set_next_window_position(20, 20, imgui.ONCE)
            imgui.set_next_window_size(500, 300, imgui.ONCE)
            TheSchedular.ShowGuide = imgui.begin("User guide", True)[1]
            imgui.show_user_guide()
            imgui.end()

        if TheSchedular.ShowStyle:
            TheSchedular.ShowStyle = imgui.begin("Style Editor", True)[1]
            imgui.show_style_editor()
            imgui.end()

        if TheSchedular.SearchFile:
            videopath1 = None
            ret = -1
            imgui.set_next_window_position(TheSchedular.searchwindow.x,TheSchedular.searchwindow.y , imgui.ONCE)
            imgui.set_next_window_size(TheSchedular.searchwindowsize.x, TheSchedular.searchwindowsize.y, imgui.ONCE)
            TheSchedular.SearchFile = imgui.begin("Search", True)[1]
            if TheSchedular.rescan:
                dirlist= Path(TheSchedular.path).glob(TheSchedular.search)
                TheSchedular.rescan = False
            if imgui.button("Prev") and len(TheSchedular.lastpath) > 0:
                TheSchedular.path = TheSchedular.lastpath.pop()
                TheSchedular.rescan = True
            imgui.same_line()    
            if imgui.button("<-"):
                TheSchedular.lastpath.append(TheSchedular.path)
                TheSchedular.path = os.path.split(TheSchedular.path)[0]
                TheSchedular.rescan = True
            imgui.same_line()
            ChangePath = None
            ChangePath = imgui.input_text('path', TheSchedular.path, 256, flags=(imgui.INPUT_TEXT_ENTER_RETURNS_TRUE))
            if ChangePath[0]:
                try: 
                    if Path(ChangePath[1]).is_file():
                        videopath1 = ChangePath[1]
                    elif Path(ChangePath[1]).is_dir():
                        TheSchedular.path = ChangePath[1]
                        TheSchedular.rescan = True
                    else:
                        imgui.text("Invalid Path")
                except:
                    imgui.text("Invalid Path")
            imgui.same_line()
            if imgui.button("{0}".format(TheSchedular.search)):
                imgui.open_popup("Search")
                imgui.same_line()
            if imgui.begin_popup("Search"):
                types = []
                files = [x for x in dirlist if x.is_file()]
                types = ['*'+x.suffix.lower() for x in files if x.suffix.lower() not in types and x.suffix is not '']
                types = list(dict.fromkeys(types))
                types.append("*")
                for x in types:
                    if imgui.selectable(x)[0]:
                        TheSchedular.search = x
                        TheSchedular.rescan = True
                imgui.end_popup()
            imgui.begin_child(TheSchedular.path)
            imgui.separator()
            tempdirlist = []
            for fileordir in dirlist:
                tempdirlist.append(fileordir)
                if fileordir.is_dir():
                    if imgui.selectable("(Dir)" + fileordir.name + "/")[0]:
                        TheSchedular.lastpath.append(TheSchedular.path)
                        TheSchedular.path = fileordir._str
                        TheSchedular.rescan = True
                else:
                    if imgui.selectable(fileordir.name)[0]:
                        videopath1 = fileordir._str
            dirlist = tempdirlist
            imgui.end_child()
            if videopath1:
                cued = TheSchedular.initVideo(videopath1)
                if cued:
                    TheSchedular.Error = True       
                else:
                    TheSchedular.SearchFile = False
            if TheSchedular.Error:
                imgui.begin("Error", True, flags=(imgui.WindowFlags.NoResize|imgui.WindowFlags.NoMove|imgui.WindowFlags.NoTitleBar))
                imgui.text("{0}".format("Could not load file"))
                if imgui.button("OK"):
                    TheSchedular.Error = False
                imgui.end()
            imgui.end()
        if imgui.button("Go", 50, 50):
            TheSchedular.AdvanceCue()

        if TheSchedular.EditFilters:
            videopath1 = None
            ret = -1
            imgui.set_next_window_position(TheSchedular.searchwindow.x,TheSchedular.searchwindow.y , imgui.ONCE)
            imgui.set_next_window_size(TheSchedular.searchwindowsize.x, TheSchedular.searchwindowsize.y, imgui.ONCE)
            TheSchedular.EditFilters = imgui.begin("Edit", True)[1]
            imgui.text("Cue {0} Video {1}".format(TheSchedular.ActiveCue, TheSchedular.indexlist[TheSchedular.EditInfo]))
            if imgui.begin_menu('Add'):
                for fil in TheSchedular.Filter:
                    if fil not in TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"].keys():
                        if imgui.selectable('Add {0}'.format(fil))[0]:
                            TheSchedular.AddVPLBlock(TheSchedular.EditInfo, fil, TheSchedular.ActiveCue, blockindex)
                imgui.end_menu()
            
            filterslist = []
            for k in TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"].keys():
                filterslist.append(k)
            for filt in filterslist:
                if not TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt].get('videoindex', True):
                    if TheSchedular.EditInfo == TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt]['videoindex']:
                        for x in TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt].keys():
                            if x not in "Index Menu videoindex".split():
                                if x == "Name":
                                    imgui.text(x)
                                elif x == "State":
                                    if imgui.radio_button(x,TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]):
                                        TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x] = True
                        if "Color" in filt:
                            for col in TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt]["Data"]:
                                imgui.new_line()
                                imgui.same_line(spacing=50)
                                if col == "Nagitive":
                                    if imgui.radio_button(col,TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt]['Data'][col]):
                                        if TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt]["Data"][col]:
                                            TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt]["Data"][col] = False
                                        else:
                                            TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt]["Data"][col] = True
                                else:
                                    TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt]["Data"][col] = imgui.slider_float(col,TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt]['Data'][col][1],0, 1,'%.3f', 1.0)
                        elif "mvMatrix" in filt:
                            if imgui.is_mouse_dragging(0,-1.0):
                                w, h = glfw.get_framebuffer_size(window)
                                pos = imgui.get_mouse_drag_delta(0,-1.0)
                                
                                TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][TheSchedular.indexlist[TheSchedular.EditInfo]][filt]['Data'][12] = (pos[0]/w*2)-1
                                TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][TheSchedular.indexlist[TheSchedular.EditInfo]][filt]['Data'][13] = -1*((pos[1]/h*2)-1)
                        else:
                            imgui.selectable(filt)[0]
            TheSchedular.SetVideos(TheSchedular.ActiveCue)
            TheSchedular.VideoPlaylist(True)
            
             # react to mouse drags and what not.
            


            imgui.end()

        if Debug is not None:
            imgui.text("Viewport:{0}".format(FirstWindow))
            if imgui.button("Add Test Videos"):
                TheSchedular.initCue("Click", "Click")
                videopath = ["D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\jellyfish-30-mbps-hd-h264.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\jellyfish-60-mbps-hd-h264.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\jellyfish-100-mbps-hd-h264.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\bird20.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\bird60.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\bird90.mkv","D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\Family.3gp"]   
                for vidpath in videopath:
                    TheSchedular.initVideo(vidpath)
            if imgui.button("Add Test Cue"):
                TheSchedular.initCue("Click", "Click")
                TheSchedular.initVideo("D:\\Documents\\GradSchool\\Grad Project\\VideoEditor\\Sample Video\\jellyfish-100-mbps-hd-h264.mkv")

            if imgui.button("Reset", 50, 50):
                TheSchedular.PlayVideo = False
                TheSchedular.startvideo = True
                TheSchedular.Pause = False
                TheSchedular.ActiveCue = 0
                TheSchedular.StagedCue = 1
                TheSchedular.ReloadAll()
                TheSchedular.SetVideos(TheSchedular.ActiveCue)

        imgui.end()
        
        imgui.render()
        impl.render(imgui.get_draw_data())
    glfw.swap_buffers(window)

impl.shutdown()
glfw.terminate()
# TheSchedular.renderer.destroy()