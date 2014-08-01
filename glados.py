# -*- coding: utf-8 -*-
import psyco
psyco.full()
import os, sys, subprocess, time, random, threading, traceback
from ctypes import *
from SendKeys import SendKeys as key
import win32gui
import Image, ImageGrab

subprocess.Popen(['C:\\taskkill.exe','/F','/T','/IM','Melodyne.exe']).wait()

PUL = POINTER(c_ulong)

class KeyBdInput(Structure):
    _fields_ = [("wVk", c_ushort),
    ("wScan", c_ushort),
    ("dwFlags", c_ulong),
    ("time", c_ulong),
    ("dwExtraInfo", PUL)]

class HardwareInput(Structure):
    _fields_ = [("uMsg", c_ulong),
    ("wParamL", c_short),
    ("wParamH", c_ushort)]

class MouseInput(Structure):
    _fields_ = [("dx", c_long),
    ("dy", c_long),
    ("mouseData", c_ulong),
    ("dwFlags", c_ulong),
    ("time",c_ulong),
    ("dwExtraInfo", PUL)]

class Input_I(Union):
    _fields_ = [("ki", KeyBdInput),
    ("mi", MouseInput),
    ("hi", HardwareInput)]

class Input(Structure):
    _fields_ = [("type", c_ulong),
    ("ii", Input_I)]

class POINT(Structure):
    _fields_ = [("x", c_ulong),
    ("y", c_ulong)]
streamrunners=[]
def flushrunners():
    print >> sys.stderr, 'Flushing streamrunners.'
    for s in streamrunners:
        print >> sys.stderr, s.content
        s.content = ''
    sys.stderr.flush()
def catch(t, v, trace):
    flushrunners()
    print >> sys.stderr, '\n'.join(traceback.format_exception(t,v,trace))
    sys.stderr.flush()
    sys.exit(1)
sys.excepthook = catch
class streamrunner(threading.Thread):
    def __init__(self, stream, prefix='>'):
        self.stream = stream
        self.prefix = prefix
        self.content = 'Begin streamrun: '+self.prefix+'\n'
        threading.Thread.__init__(self)
        streamrunners.append(self)
    def run(self):
        try:
            for i in self.stream:
                print >> sys.stderr, i.strip()
                try:
                    self.content += self.prefix + ' [' + time.strftime('%H:%M:%S') + '] ' + i.strip() + '\n'
                except:
                    self.content += 'Error in streamrunner, '+str(len(i))+' bytes omitted\n'
        except:
            self.content += 'Error while looping streamrunner.\n'
        self.content = 'End streamrun: '+self.prefix+'\n'
        try:
            self.stream.close()
        except:
            pass
logFile = open('C:\\log.txt', 'wb')
def say(*args):
    global logFile
    s = []
    for i in args:
        if type(i) is type(''):
            s.append(unicode(i))
        elif type(i) is type(u''):
            s.append(i)
        else:
            s.append(unicode(i))
    s=' '.join(s)
    print s.strip()
    logFile.write(s.strip() + '\r\n')
    logFile.flush()
    sys.stdout.flush()
    return s
def sleep(t,stfu=False):
    slowfactor=3.5
    if not stfu:
        say('Sleeping for', t, 'seconds with slowness factor', slowfactor)
    return time.sleep(t*slowfactor)
def ensurealt(delay=.1):
    sleep(delay)
    say('Ensuring ALT is not pressed...')
    key('%')
    time.sleep(1)
    key('%')
    sleep(delay)
def mouse(x, y):
    orig = POINT()
    windll.user32.GetCursorPos(byref(orig))
    windll.user32.SetCursorPos(x,y)
    return (orig.x, orig.y)
def click(x,y=None,delay=0.1,fixalt=True):
    if y is None and type(x) in (type(()), type([])):
        return click(x[0], x[1],delay=delay,fixalt=fixalt)
    if fixalt:
        ensurealt()
    m=mouse(x, y)
    if delay:
        sleep(delay,stfu=True)
    FInputs = Input * 2
    extra = c_ulong(0)
    ii_ = Input_I()
    ii_.mi = MouseInput( 0, 0, 0, 2, 0, pointer(extra) )
    ii2_ = Input_I()
    ii2_.mi = MouseInput( 0, 0, 0, 4, 0, pointer(extra) )
    x = FInputs( ( 0, ii_ ), ( 0, ii2_ ) )
    windll.user32.SendInput(2, pointer(x), sizeof(x[0]))
    return m
def doubleclick(x, y=None, delay=.02):
    click(x,y,delay=0,fixalt=False)
    sleep(delay)
    result = click(x,y,delay=0,fixalt=False)
    sleep(delay * 2)
    return result
def find(findimg, insideimg=None, fail=False, clickpoint=False):
    r = subfind(findimg, insideimg=insideimg)
    if r is None:
        if fail:
            say('Finding fail:', fail)
            sys.exit(1)
        return None
    if clickpoint:
        click(r)
    return r
def subfind(findimg,insideimg=None):
    if type(findimg) in(type(()),type([])):
        for i in findimg:
            r = subfind(i, insideimg=insideimg)
            if r is not None:
                return r
        return None
    if type(findimg) is type({}):
        for i in findimg.keys():
            r = subfind(i, insideimg=insideimg)
            if r is not None:
                return (r[0] + findimg[i][0], r[1] + findimg[i][1])
        return None
    if type(findimg) in (type(''),type(u'')):
        findimg=Image.open(findimg).convert('RGB')
    else:
        findimg=findimg.convert('RGB')
    if insideimg is None:
        insideimg=ImageGrab.grab().convert('RGB')
    elif type(insideimg) in (type(''),type(u'')):
        insideimg=Image.open(insideimg).convert('RGB')
    else:
        insideimg=insideimg.convert('RGB')
    findload=findimg.load()
    insideload=insideimg.load()
    #insideimg.save('C:\\tmptest'+str(random.random())+'.png','PNG')
    point=None
    for x in range(insideimg.size[0]-findimg.size[0]):
        for y in range(insideimg.size[1]-findimg.size[1]):
            sofarsogood=True
            for x2 in range(findimg.size[0]):
                for y2 in range(findimg.size[1]):
                    p1=findload[x2,y2]
                    p2=insideload[x+x2,y+y2]
                    if abs(p1[0]-p2[0])>8 or abs(p1[1]-p2[1])>8 or abs(p1[2]-p2[2])>8:
                        sofarsogood=False
                        break
                if not sofarsogood:
                    break
            if sofarsogood:
                say('Found point at',(x,y))
                point=(x,y)
        if point is not None:
            break
    return point
p=subprocess.Popen('C:\\Program Files\\Celemony\\Melodyne.3.2\\Melodyne.exe',stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
streamrunner(p.stdout, prefix='Melodyne>').start()
streamrunner(p.stderr, prefix='Melodyne>2').start()
melodynepid=p.pid
sleep(11)
ensurealt()
key('{ESC}') # Closes bug report window if it appears
find({'C:\\Cancel.png':(8,8)},clickpoint=True) # Closes bug report window if it is still not closed
sleep(3)
key('^o')
ensurealt()
sleep(4)
soundfile=None
for f in os.listdir('Z:\\files'):
    if f[-11:].lower()=='.glados.wav':
        soundfile=f
        break
if soundfile is None:
    say('No sound file found.')
    sys.exit(1)
say('Sound file is:',soundfile)
sys.stdout.flush()
sleep(1)
ensurealt()
key('{BACKSPACE}')
sleep(1)
key('+z')
sleep(1)
key(':\\files\\'+soundfile+'{ENTER}') # Open file
ensurealt()
sleep(8)
key('s') # Select all
sleep(1)
key('p') # Change to Pitch tool
sleep(.5)
key('a') # Open pitch correction dialog (Edit commands -> Correction macros -> Correct Pitch)
sleep(1)
pitchpoint=find({
    'C:\\PitchDialog.png':(5,59),
    'C:\\PitchDialog2.png':(1,36)
}, clickpoint=True, fail='Pitch point')
sleep(.5)
click(pitchpoint[0]+375,pitchpoint[1]+40)
sleep(5)
ensurealt()
key('m') # Change to Pitch Modulation tool
sleep(.5)
key('s') # Select all
sleep(2)
key('i') # Invert selection (since all is selected, it deselects everything)
sleep(4)
imgbefore=ImageGrab.grab().convert('RGB')
beforeload=imgbefore.load()
sleep(4)
key('s') # Select all again
sleep(12)
imgafter=ImageGrab.grab().convert('RGB')
afterload=imgafter.load()
sleep(2)
# Attempt to find a point where the notes are
notepixel=None
for x in range(imgbefore.size[0]):
    for y in range(imgbefore.size[1]):
        p=beforeload[x,y]
        p2=afterload[x,y]
        if p2[0]>160 and p2[0]>p[1]*2 and p2[0]>p[2]*2:
            if p[0]!=p2[0] or p[1]!=p2[1] or p[2]!=p2[2]:
                notepixel=(x,y)
                say('Found note pixel:',notepixel)
                break
    if notepixel is not None:
        break
if notepixel is None:
    say('Could not find note pixel.')
    sys.exit(1)
say('Found note pixel:',notepixel)
doubleclick(notepixel[0],notepixel[1]) # Double click on note
sleep(5)
key('f') # Select formant tool
sleep(1)
formantpoint=find({
  'C:\\Formant.png':(84,7),
  'C:\\Formant2.png':(83,5)
},fail='Formant point')
doubleclick(formantpoint)
sleep(.2)
key('100{ENTER}')
sleep(5)
key('^e') # Open export dialog
ensurealt()
sleep(1)
frequencypoint=find('C:\\WaveFrequency.png')
if frequencypoint is not None:
    click(frequencypoint[0],frequencypoint[1]) # Open Frequency menu
    time.sleep(.5)
    mouse(frequencypoint[0]+1,frequencypoint[1]+1) # move mouse to make the menu lose focus to remove highlight which may conflict with the next find()
    mouse(frequencypoint[0]+2,frequencypoint[1]+2)
    freq44100=find('C:\\44100kHz.png')
    if freq44100 is not None:
        click(freq44100[0]+25,freq44100[1]+6) # Change frequency to 44100 kHz
    else:
        say('WARNING: No 44100 kHz point found.')
        click(frequencypoint[0],frequencypoint[1]) # Close the menu
    time.sleep(1)
else:
    say('WARNING: No frequency point found.')
saveaspoint=find('C:\\SaveAs.png')
if saveaspoint is None:
    say('Could not find "save as" point.')
    sys.exit(1)
click(saveaspoint[0]+53,saveaspoint[1]+12)
sleep(3)
ensurealt()
key('{BACKSPACE}')
sleep(1)
key('+z')
sleep(1)
key(':\\files\\ok-'+soundfile[:-11]+'.done.wav{ENTER}')
sleep(17.5)
key('q') # Exit
sleep(3)
ensurealt()
key('{RIGHT}{RIGHT}{ENTER}') # Close exit confirmation dialog
sleep(5)
flushrunners()
subprocess.Popen(['C:\\taskkill.exe','/F','/T','/IM','Melodyne.exe']).wait()
logFile.close()
