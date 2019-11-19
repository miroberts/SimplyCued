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
import select
import sys
import copy
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



        

    def rend(self, frame, Data, frameidex, frametotal, fps):
        scalerx = 0
        if Data.get('SlideIn'):
            if Data['SlideIn'][0] > 0:
                scalerx = Data['SlideIn'][0] * Data['SlideIn'][1] # -1 or 1
                Data['SlideIn'][0] = Data['SlideIn'][0] - Data['SlideIn'][2]
        if Data.get('SlideOut'):
            xrate = (Data['SlideOut'][2]/fps)*frametotal
            if Data['SlideOut'][0] > 0:
                scalerx = Data['SlideOut'][0] * Data['SlideOut'][1] # -1 or 1
                Data['SlideOut'][0] = Data['SlideOut'][0] - Data['SlideOut'][2] # rate of change

        gl.glUseProgram(self.program)
        mvMatrix=[]
        for da in Data.keys():
            if 'mvMatrix' in da:
                mvMatrix = copy.deepcopy(Data[da]['Data'])
                mvMatrix[12] = copy.deepcopy(scalerx + Data[da]['Data'][12])
            if 'Color' in da:
                if Data[da]['Data']['Nagitive']:
                    gl.glUniform4fv(self.vNgt, 1, 1.0)
                else:
                    gl.glUniform4fv(self.vNgt, 1, 0.0)

        gl.glUniformMatrix4fv(self.modelViewMatrix, 1, gl.GL_FALSE, mvMatrix)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buff)
        gl.glVertexAttribPointer(self.vPos, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        gl.glVertexAttribPointer(self.vTex, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        txFrame = Img.fromarray(frame)
        shpx = txFrame.size[0]
        shpy = txFrame.size[1]
        txFrame = txFrame.tobytes('raw', 'BGRX', 0, -1)
        

        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, shpx, shpy, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE,txFrame)
        
        



        gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)


        
        

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
    keylist = []
    Cueindexlist = []
    indexlist = []
    FullRunTime = 0
    Videodict = dict()
    Cues = dict()
    index = 0
    Cueindex = 0
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
    searchwindowsize = imgui.Vec2(800, 300)
    Inersize = imgui.Vec2(0,-45)
    Inercuesize = imgui.Vec2(0,150)
    Incuesize = imgui.Vec2(0,35)

    #save where user last was but start at home
    path = os.path.expanduser("~")
    lastpath = [os.path.expanduser("~")]
    dirlist = []
    startvideo = False
    CuesList = ["Click", "StopOnClick"] 
    Filter = ["Filter","Mask","View Port","Repeat", "Time"]
    State= ["On", "Paused", "Off"]
    ActiveCue = 0
    StagedCue = 0

    #Navication
    search = "*"
    rescan = False
    Error = False
    selectedindex = None
    Repeat = 0
    mouse = True
    starttime = time.time()
    runtime = 0.0

    def __init__(self):
        self.renderer = Renderer()

    def initCue(self, startcon, name):
        self.Cues["{0}{1}".format(name, self.Cueindex)] = {"Name":name, "StartCondition":startcon, "Index":self.Cueindex, 'starttime': None, "Filters":dict(), "Filterindex":0}
        for vid in self.Videodict.keys():
            self.AddVPLBlock(vid, 'mvMatrix', self.Cueindex, np.array([
                2, 0.0,  0.0, 0.0,
                0.0, 2,  0.0, 0.0,
                0.0, 0.0,  1.0, 0.0,
                -1.0, -1.0, 0.0, 1.0], np.float32))
            self.AddVPLBlock(vid, 'Color', self.Cueindex, {"Red": [0,.5] , "Green": [0,.5], "Blue" : [0,.5], "Distortion" : [0,0.0], "Nagitive": False})

        self.Cueindex = self.Cueindex+1
        self.rebuildCuekeylist()
    
    def AddVPLBlock(self, vid, block, cuid, data):
        for n in self.Cues.keys():
            if self.Cues[n]["Index"] == cuid:
                if self.Cues[n]["Filters"].get(vid):
                    self.Cues[n]["Filters"][vid].update({"{0}{1}".format(block, self.Cues[n]["Filterindex"]): {"Name":block, "Index":self.Cues[n]["Filterindex"], 'Data': data, "Menu": False}, 'State':0})
                else:
                    self.Cues[n]["Filters"][vid] = {"{0}{1}".format(block, self.Cues[n]["Filterindex"]): {"Name":block, "Index":self.Cues[n]["Filterindex"], 'Data': data, "Menu": False}, 'State':0}
                self.Cues[n]["Filterindex"] = self.Cues[n]["Filterindex"] + 1

    def initVideo(self, videopath):
        cuedvideo = CuedVideo()
        ret = cuedvideo.LoadVideo(videopath)
        if not (ret == -1):
            self.Videodict["{0}{1}".format(cuedvideo.name, self.index)] = {'Index':self.index, 'Name':cuedvideo.name, 'Filters':None, 'State':0, 'StartTime':None, 'PlayOffset': 0, 'StartFrame':1, 'Video': cuedvideo, 'Repeat':[0,0]}
            w, h = glfw.get_framebuffer_size(window)
            for cu in range(len(self.Cueindexlist)):
                self.AddVPLBlock("{0}{1}".format(cuedvideo.name, self.index), 'mvMatrix', cu, np.array([
                    2.0, 0.0,  0.0, 0.0,
                    0.0, 2.0,  0.0, 0.0,
                    0.0, 0.0,  1.0, 0.0,
                    -1.0, -1.0, 0.0, 1.0], np.float32))
                self.AddVPLBlock("{0}{1}".format(cuedvideo.name, self.index), 'Color', cu, {"Red": [0,.5] , "Green": [0,.5], "Blue" : [0,.5], "Distortion" : [0,0.0], "Nagitive": False})
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
        keys = self.Cues[cue]["Filters"][self.indexlist[vid]].keys()
        if Source < Destination:
            for key in keys:
                if self.Cues[cue]['Filters'][self.indexlist[vid]][key]['Index'] <= Destination and self.Cues[cue]['Filters'][self.indexlist[vid]][key]['Index'] > Source and self.Cues[cue]['Filters'][self.indexlist[vid]][key]['Index'] > 0:
                    self.Cues[cue]['Filters'][self.indexlist[vid]][key]['Index'] = self.Cues[cue]['Filters'][self.indexlist[vid]][key]['Index']-1
        if Source > Destination:
            for key in keys:
                if self.Cues[cue]['Filters'][self.indexlist[vid]][key]['Index'] >= Destination and self.Cues[cue]['Filters'][self.indexlist[vid]][key]['Index'] < Source:
                    self.Cues[cue]['Filters'][self.indexlist[vid]][key]['Index'] = self.Cues[cue]['Filters'][self.indexlist[vid]][key]['Index'] + 1
        self.Cues[cue]['Filters'][self.indexlist[vid]]['Index'] = Destination

    def VideoPlaylist(self, edit):
        for x in self.indexlist:
            frame = None
            if edit > 0 and (self.Videodict[x]['State'] == 0 or self.Videodict[x]['State'] == 1):
                self.renderer.rend(self.Videodict[x]['Video'].firstimage,self.Videodict[x]["Filters"], 0, self.Videodict[x]['Video'].frame_count, self.Videodict[x]['Video'].fps)
            elif not edit:
                if self.Videodict[x].get("Filters"):
                    if self.Videodict[x]["Filters"]['State'] == 0:#0 = get next frame
                        f = int((time.time() - self.Videodict[x]['StartTime'] + self.Videodict[x]['PlayOffset']) * self.Videodict[x]['Video'].fps)
                        if f >=0 and f <=  self.Videodict[x]['Video'].frame_count:
                            if self.Videodict[x].get('FadeIn'):
                                #not per video...
                                ##### https://stackoverflow.com/questions/28650721/cv2-python-image-blending-fade-transition
                                # ##### Not Finished######
                                n = 1
                            if self.Videodict[x].get('PushOut'):
                                #not per video...
                                ##### https://stackoverflow.com/questions/28650721/cv2-python-image-blending-fade-transition
                                # ##### Not Finished######
                                n = 1
                            if self.Videodict[x].get('PushIn'):
                                #not per video...
                                # ##### Not Finished######
                                n = 1
                            if self.Videodict[x].get('PushOut'):
                                #not per video...
                                # ##### Not Finished######
                                n = 1

                            frame =  self.Videodict[x]['Video'].nextframe(f)
                            if frame is not None:
                                self.renderer.rend(frame,self.Videodict[x]["Filters"], f,self.Videodict[x]['Video'].frame_count, self.Videodict[x]['Video'].fps)
                            elif self.Videodict[x]['Repeat'][1] > 0 and self.Videodict[x]['Repeat'][1] > self.Videodict[x]['Repeat'][0]: 
                                # play n number of times,
                                self.Videodict[x]['Video'].Seek(0)
                                self.Videodict[x]['Video'].lastframe = self.Videodict[x]['Video'].firstimage
                                self.Videodict[x]['StartTime'] = time.time()
                                self.Videodict[x]['Video'].lastframeid = 0
                                self.renderer.rend(self.Videodict[x]['Video'].firstimage,self.Videodict[x]["Filters"],self.Videodict[x]['Video'].lastframeid, self.Videodict[x]['Video'].frame_count, self.Videodict[x]['Video'].fps)
                                self.Videodict[x]['Repeat'][0] = self.Videodict[x]['Repeat'][0] + 1
                            else: 
                                self.Videodict[x]["Filters"]['State'] = 2
                                self.Videodict[x]['Video'].Seek(0)
                                self.Videodict[x]['Video'].lastframe = self.Videodict[x]['Video'].firstimage



                                
                    elif self.Videodict[x]["Filters"]['State'] == 1:#1 == paused video
                        if self.Videodict[x]['Video'].lastframe is not None:
                            frame = self.Videodict[x]['Video'].lastframe
                            self.renderer.rend(frame,self.Videodict[x]["Filters"])
                #else 2 means off

    def removeVideo(self,viid):
        removekey = {}
        if viid is not None:
            for cue in self.Cues.keys():
                self.Cues[cue]["Filters"].pop(self.indexlist[viid], None)
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
                    if self.Cueindex > 0:
                        self.Cueindex = self.Cueindex - 1
                else:
                    removekey[key] = self.Cues[key]
                    if self.Cues[key]['Index'] > cuid and self.Cues[key]['Index'] > 0:
                        removekey[key]['Index'] = self.Cues[key]['Index']-1
            self.Cues = removekey
            self.rebuildCuekeylist()
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
        for i, k in zip(range(len(temdic.keys())), temdic.keys()):
            self.keylist.append(temdic[k])
            self.indexlist.append(temdicindex[i])
    def rebuildCuekeylist(self):
        self.Cueindexlist = []
        temdicindex = {}
        for i in self.Cues.keys():
            temdicindex[self.Cues['{0}'.format(i)]['Index']] = i
        for i in range(len(temdicindex.keys())):
            self.Cueindexlist.append(temdicindex[i])
    def RunTime(self):
        return self.FullRunTime
    def getcue(self, cue):
        cuename = None
        for c in self.Cues.keys():
            if self.Cues[c]['Index'] == cue:
                cuename = c
        return cuename
    def SetVideos(self, cue):
        cuename = self.getcue(cue)
        if cuename:
            for vname in self.Videodict.keys():
                if self.Videodict[vname]["Filters"]:
                    NewFilters = {}
                    for fil in self.Cues[cuename]["Filters"][vname].keys():
                        NewFilters[fil] = copy.deepcopy(self.Cues[cuename]["Filters"][vname][fil])
                    self.Videodict[vname]["Filters"].update(NewFilters)
                elif self.Cues[cuename]["Filters"].get(vname):
                    NewFilters = {}
                    for fil in self.Cues[cuename]["Filters"][vname].keys():
                        NewFilters[fil] = copy.deepcopy(self.Cues[cuename]["Filters"][vname][fil])
                    self.Videodict[vname]["Filters"] = NewFilters
                if self.Cues[cuename]["Filters"][vname]['State'] == 0:
                    self.Videodict[vname]['StartTime'] = time.time()
                temp = copy.deepcopy(self.Cues[cuename]["Filters"][vname]['State'])
                self.Videodict[vname]["State"] = temp
                if self.Cues[cuename].get('Repeat'):
                    self.Videodict[vname]['Repeat'] = copy.deepcopy(self.Cues[cuename]['Repeat'])

    def Reload(self, vname):
        self.Videodict[vname]['Video'].Seek(0)
    def ReloadAll(self):
        for vname in self.Videodict.keys():
            self.Reload(vname)
            self.Videodict[vname]["Filters"] = None
            self.Videodict[vname]['StartTime'] = None
            self.Videodict[vname]['Video'].lastframeid = 0
    
    def Reset(self):
        if self.Cueindex < self.StagedCue:
            # glfw.set_window_monitor(window, None, 0,0, FirstWindow.x,FirstWindow.y,glfw.REFRESH_RATE)
            self.PlayVideo = False
            self.startvideo = False
            self.Pause = False
            self.StagedCue = 0
            self.ActiveCue = 0
            self.ReloadAll()
            self.SetVideos(self.ActiveCue)
            return True
        else:
            return False


    def AdvanceCue(self):
        if not self.Reset():
            self.PlayVideo = True
            self.startvideo = True
            self.Pause = False
            self.starttime = time.time()
            self.runtime = 0.0
            tmp = self.StagedCue + 1
            if self.Cueindex > self.StagedCue:
                self.ActiveCue = self.StagedCue
                self.SetVideos(self.ActiveCue)
            else:
                for vname in self.Videodict.keys():
                    self.Videodict[vname]["Filters"]['State'] = 2
            self.StagedCue = tmp
            
    def AdvanceCueFake(self):
        if not self.Reset():
            self.Pause = True        
            

#imgui Setup
m = get_monitors()

FirstWindow = imgui.Vec2(int(m[0].width*1.25), int(m[0].height*1.25))

imgui.create_context()

if not glfw.init():
    print("Could not initialize OpenGL context")
    exit(1)

# Create a windowed mode window and its OpenGL context
window = glfw.create_window(
    FirstWindow.x, FirstWindow.y, "SimplyCued", None, None
)
glfw.make_context_current(window)
glfw.set_window_monitor(window,None, 0,0, FirstWindow.x,FirstWindow.y,glfw.REFRESH_RATE)
if not window:
    glfw.terminate()
    print("Could not initialize Window")
    exit(1)

impl = GlfwRenderer(window)

TheSchedular = Schedular()

Debug = None
Debug = True

#Screen
# ##### More then one screen?
Screen = None
playtime= 0
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

def Checkbounds(val):
    if val > 0:
        if val <= 2:
            return val
        else:
            return 2
    else:
        if val >= -1:
            return val
        else:
            return -1



while(not glfw.window_should_close(window)):
    gl.glClearColor(0., 0., 0., 1)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    glfw.poll_events()
    impl.process_inputs()

    if TheSchedular.PlayVideo:
        # glfw.set_window_monitor(window,glfw.get_primary_monitor(), 0,0, FirstWindow.x,FirstWindow.y,glfw.REFRESH_RATE)
        if TheSchedular.startvideo and TheSchedular.Cueindex >= TheSchedular.StagedCue:
            # TheSchedular.SetVideos(TheSchedular.ActiveCue)
            TheSchedular.startvideo = False
            playtime = 0

        if TheSchedular.active(): 
            if not TheSchedular.Pause:
                if TheSchedular.RunTime() > TheSchedular.runtime or TheSchedular.Cues[TheSchedular.getcue(TheSchedular.ActiveCue)].get('Repeat'):
                    pl = 0
                    TheSchedular.VideoPlaylist(0)
                    TheSchedular.runtime = time.time() - TheSchedular.starttime

                else:
                    # glfw.set_window_monitor(window, None, 0,0, FirstWindow.x,FirstWindow.y,glfw.REFRESH_RATE)
                    TheSchedular.startvideo=True
                    TheSchedular.PlayVideo = False
                    TheSchedular.Pause = False

        if not imgui.is_mouse_down(0):
            TheSchedular.mouse = True
        # stop on mouse click, 
        if TheSchedular.Cues[TheSchedular.getcue(TheSchedular.ActiveCue)]['StartCondition'] == 'StopOnClick' and not TheSchedular.Pause and TheSchedular.mouse:
            if imgui.is_mouse_down(0):
                TheSchedular.AdvanceCueFake()
                TheSchedular.mouse = False
        if 'Time' in TheSchedular.Cues[TheSchedular.getcue(TheSchedular.ActiveCue)].keys(): 
            if TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]['Time'][0] > 0:
                # play for n seconds or milliseconds
                scale = 1/1000
                if TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]['Time'][1] == "Seconds":
                    scale = 1
                if TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]['Time'][0]*scale  <= TheSchedular.runtime:
                        TheSchedular.AdvanceCue()
        # play on mouse click, 
        if imgui.is_mouse_down(0) and TheSchedular.mouse:
            TheSchedular.AdvanceCue()
            TheSchedular.mouse = False
    else:

        imgui.new_frame()

        imgui.set_next_window_position(20, 20, imgui.ONCE)
        imgui.set_next_window_size(800, 500, imgui.ONCE)
        imgui.begin("Simply Cued", False, imgui.WINDOW_MENU_BAR)
        if imgui.begin_menu_bar():
            if imgui.begin_menu('Menu', True):
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
        imgui.same_line()
        if imgui.button("Delete Cue"):
            TheSchedular.removeCue(TheSchedular.ActiveCue)
            if TheSchedular.ActiveCue != 0 :
                TheSchedular.ActiveCue = TheSchedular.ActiveCue-1
        imgui.end_child()
        imgui.begin_child("Cued", TheSchedular.Inercuesize.x, TheSchedular.Inercuesize.y, border=True)
        if not len(TheSchedular.Cueindexlist) > 0:
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
            for cu in TheSchedular.Cueindexlist:
                imgui.text("{0}. ".format(queindex+1))
                imgui.next_column()
                queindex=queindex+1
                if TheSchedular.ActiveCue == queindex:
                    imgui.same_line(spacing=50)
                    if imgui.button('{0} {1}'.format(queindex,TheSchedular.Cues[TheSchedular.Cueindexlist[queindex]]['Name'])):
                        TheSchedular.ActiveCue = queindex
                    if queindex > 0:
                        imgui.same_line()
                        if imgui.button('^'):
                            TheSchedular.MoveCue(queindex,queindex-1)
                    if queindex+1 < TheSchedular.Cueindex:
                        imgui.same_line()
                        if imgui.button('v'):
                            TheSchedular.MoveCue(queindex,queindex+1)

                else:
                    if imgui.button('{0} {1}'.format(queindex,TheSchedular.Cues[TheSchedular.Cueindexlist[queindex]]['Name'])):
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
                    if "Time" not in vid and "Repeat" not in vid:
                        imgui.text("{0}. ".format(index+1))
                        imgui.next_column()
                        index=index+1 
                        
                        if imgui.button('{0}{1}'.format(index,TheSchedular.Videodict[TheSchedular.indexlist[index]]['Name'])):
                            TheSchedular.SelectedVideo = vid
                            TheSchedular.selectedindex = index
                        if index == TheSchedular.selectedindex:
                            if index > 0:
                                imgui.same_line()
                                if imgui.button('^'):
                                    TheSchedular.MoveVideo(index,index-1)
                            if index+1 < len(TheSchedular.indexlist):
                                imgui.same_line()
                                if imgui.button('v'):
                                    TheSchedular.MoveVideo(index,index+1)
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
                            TheSchedular.EditInfo = TheSchedular.indexlist[TheSchedular.movieindex]
                            TheSchedular.EditFilters = True
                            TheSchedular.SetVideos(TheSchedular.ActiveCue)
                        TheSchedular.movieindex = TheSchedular.movieindex + 1
                        if TheSchedular.movieindex >= len(TheSchedular.Videodict.keys()):
                            TheSchedular.movieindex = 0
                        if len(Filterkeys) > 0:
                            for fill in Filterkeys:
                                blockindex = blockindex + 1
                                if TheSchedular.movieindex == TheSchedular.indexlist.index(fill):
                                    for filt in TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][fill].keys():
                                        if "State" not in filt:
                                            imgui.new_line()
                                            imgui.same_line(spacing=50)
                                            imgui.text(filt)

                        imgui.next_column()
                        if vid in TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"]:
                            if imgui.begin_menu("{0} {1}".format(index,TheSchedular.State[TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][vid]['State']])):
                                for st in TheSchedular.State:
                                    if imgui.selectable(st)[0]:
                                        TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][vid]['State'] = TheSchedular.State.index(st)
                                imgui.end_menu()
                        imgui.next_column()
            imgui.end_child()
            if imgui.button("Go", 50, 50):
                TheSchedular.AdvanceCue()
            
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
        

        if TheSchedular.EditFilters and len(TheSchedular.Cueindexlist) > 0:
            # glfw.set_window_monitor(window,glfw.get_primary_monitor(), 0,0, FirstWindow.x,FirstWindow.y,glfw.REFRESH_RATE)
            videopath1 = None
            ret = -1
            imgui.set_next_window_position(TheSchedular.searchwindow.x,TheSchedular.searchwindow.y , imgui.ONCE)
            imgui.set_next_window_size(TheSchedular.searchwindowsize.x, TheSchedular.searchwindowsize.y, imgui.ONCE)
            TheSchedular.EditFilters = imgui.begin("Edit", True)[1]
            imgui.text("Cue {0} Video {1}".format(TheSchedular.ActiveCue, TheSchedular.EditInfo))
            
            filterslist = list(TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"].keys())
            for filt in filterslist:
                if TheSchedular.EditInfo == filt:
                    go = {"Time":True, "Repeat":True}
                    if 'Time' not in TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]].keys():
                        TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]['Time'] = [0, "Seconds"]
                    elif go["Time"] and TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]].get('Time') != None:
                        go["Time"] = False
                        TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]['Time'][0] = imgui.input_float("Total Cue RunTime",TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]['Time'][0],1,60)[1] 
                        imgui.same_line(spacing=50)
                        if imgui.begin_menu("{0}".format(TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]['Time'][1])):
                            for mas in "Seconds Milliseconds".split():
                                if imgui.selectable(mas)[0]:
                                    TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]['Time'][1] = mas
                            imgui.end_menu()   
                    if imgui.begin_menu("Add Transition"):
                        for f in "SlideIn SlideOut FadeIn FadeOut".split():
                            if f not in TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]['Filters'][filt].keys():
                                if imgui.selectable(f)[0]:
                                    TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]['Filters'][filt][f] = {}
                        imgui.end_menu()
                    
                    for x in TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt].keys():
                        if 'Repeat' not in TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]].keys():
                            TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]['Repeat'] = [0,0]
                        elif go["Repeat"] and TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]].get('Repeat') != None:
                            go["Repeat"] = False
                            imgui.new_line()
                            imgui.same_line(spacing=50)
                            chang, respval = imgui.input_int("Repeate",TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]['Repeat'][1],1)
                            if chang:
                                TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]['Repeat'][1] = respval
                                
                        elif "Color" in x:
                            for col in TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]["Data"]:
                                imgui.new_line()
                                imgui.same_line(spacing=50)
                                if col == "Nagitive":
                                    if imgui.radio_button("Swap GR",TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][col]):
                                        if TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]["Data"][col]:
                                            TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]["Data"][col] = False
                                        else:
                                            TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]["Data"][col] = True
                                else:
                                    TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]["Data"][col] = imgui.slider_float(col,TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][col][1],0, 1,'%.3f', 1.0)
                        elif "mvMatrix" in x:
                            imgui.new_line()
                            imgui.same_line(spacing=50)
                            if imgui.button("Reset Video Position"):
                                TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][12] = -1
                                TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][13] = -1
                                TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][0] = 2
                                TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][5] = 2
                            w, h = glfw.get_framebuffer_size(window)
                            if imgui.is_mouse_down(0):
                                pos = imgui.get_mouse_pos()

                                posx = (pos[0]/w*2)-1
                                h1 = TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][12]
                                h2 = h1+TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][0]
                                posy = -1*((pos[1]/h*2)-1)
                                h3 = TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][13]
                                h4 = h3+TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][5]
                                difx = 0
                                dify = 0

                                if posx > h1*.5 and posx < h2*.5 and posy > h3*.5 and posy < h4*.5:
                                    TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][12] =  posx - TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][0]/2
                                    TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][13] =  posy - TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][5]/2 
                                
                                elif abs(posx - h1) < .2 and abs(posy - h3) < .2:
                                    difx = TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][12] - posx
                                    dify = TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][13] - posy
                                    TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][12] = posx
                                    TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][13] = posy
                                elif abs(posx - h2) < .2 and abs(posy - h4) < .2:
                                    difx = posx - h2
                                    dify = posy - h4
                                elif abs(posx - h1) < .2 and abs(posy - h4) < .2:
                                    difx = TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][12] - posx
                                    dify = posy - h4                 
                                    TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][12] = posx
                                    TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][13] = posy - TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][5]
                                elif abs(posx - h2) < .2 and abs(posy - h3) < .2:
                                    difx = posx - h2
                                    dify = TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][13] - posy
                                    
                                    TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][12] = posx - TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][0]
                                    TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][13] = posy
                                TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][0] = TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][0] + difx
                                TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][5] = TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x]['Data'][5] + dify
                        elif "Mask" in x:
                            # ##### Not Finished######
                            #rectangle, circle, and a straight line select area
                            points = []
                        elif "Slide" in x:
                            if TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x] != {}:
                                imgui.text('Configure {0}'.format(x))
                                imgui.new_line()
                                imgui.same_line(spacing=50)
                                TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x][2] = imgui.input_float("Rate of change for {0}".format(x),TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x][2],.001,.01)[1]
                                buton = False
                                if TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x][1] > 0:
                                    buton = True
                                imgui.new_line()
                                imgui.same_line(spacing=50)                                    
                                if imgui.radio_button("Reverse direction",buton):
                                    TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x][1] = TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x][1] * -1
                            else:
                                TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x] = [2,-1,0]
                        else:
                            if x not in "Name".split():
                                if x == "State":
                                    imgui.new_line()
                                    imgui.same_line(spacing=50)
                                    if imgui.begin_menu("{0}".format(x)):
                                        for st in TheSchedular.State:
                                            if imgui.selectable(st)[0]:
                                                TheSchedular.Cues[TheSchedular.Cueindexlist[TheSchedular.ActiveCue]]["Filters"][filt][x] = TheSchedular.State.index(st)
                                        imgui.end_menu()
                    go = {"Time":True, "Repeat":True}
            TheSchedular.SetVideos(TheSchedular.ActiveCue)
            TheSchedular.VideoPlaylist(2)      
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

        imgui.end()
        
        imgui.render()
        impl.render(imgui.get_draw_data())
    glfw.swap_buffers(window)

impl.shutdown()
glfw.terminate()
# TheSchedular.renderer.destroy()