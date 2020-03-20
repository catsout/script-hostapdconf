# import the kodi python modules we are going to use
# see the kodi api docs to find out what functionality each module provides
import xbmc
import xbmcgui
import xbmcaddon

# create a class for your addon, we need this to get info about your addon
ADDON = xbmcaddon.Addon()
# get the full path to your addon, decode it to unicode to handle special (non-ascii) characters in the path
#CWD = ADDON.getAddonInfo('path') # for kodi 19 and up..
CWD = ADDON.getAddonInfo('path').decode('utf-8')

# add a class to create your xml based window
class GUI(xbmcgui.WindowXMLDialog):
    # [optional] this function is only needed of you are passing optional data to your window
    def __init__(self, *args, **kwargs):
        # get the optional data and add it to a variable you can use elsewhere in your script
        self.main = kwargs['main']

    # until now we have a blank window, the onInit function will parse your xml file
    def onInit(self):
        # select a view mode, '50' in our case, as defined in the skin file
        xbmc.executebuiltin('Container.SetViewMode(50)')
        # define a temporary list where we are going to add all the listitems to
        # give kodi a bit of (processing) time to add all items to the container
        xbmc.sleep(100)
        # this puts the focus on the top item of the container
        self.setFocusId(121)

    def onClick(self,controlId):
        if controlId == 122:
            self.main.read_settings()
            self.main.open_settings()


class main():
    kodi_settings = [ 
        ["interface","wlan0","text"],
        ["bridge",None,"text"],
        #2.4g,5g,2.4g 5g
        ["mode",0,"int"],
        ["channel",1,"int"],
        ["country_code","CN","text"],
        ["ieee80211n",1,"bool"],
        ["wmm",1,"bool"],
        ["ssid","kodi","text"],
        ["wpa_passphrase","11111111","text"]
    ] 
    conf = {
        "ieee80211ac":0,
        "wpa":2,
        "wpa_key_mgmt":"WPA-PSK",
        "rsn_pairwise":"CCMP"
    }
    def __init__(self,*arg,**kwargs):
        self.ADDON = kwargs["ADDON"]
    def open_settings(self):
        self.ADDON.openSettings()
    def restart_hostapd(self):
        pass
    def read_settings(self):
        def get_setting(conf):
            if conf[2] == "text":
                return self.ADDON.getSetting(conf[0])
            elif conf[2] == "int":
                return self.ADDON.getSettingInt(conf[0])
            elif conf[2] == "bool":
                return self.ADDON.getSettingBool(conf[0])

        for c in self.kodi_settings:
            setting = get_setting(c)
            if c[0] == "mode":
                mode = ["g","a"]
                self.conf["hw_mode"] = mode[setting]
                if setting == 1:
                    self.conf["ieee80211ac"] = 1
            elif c[0] == "wmm":
                self.conf["wmm_enable"] = setting
            elif c[0] == "channel" and self.conf["hw_mode"] == 1 and setting < 20:
                self.conf[c[0]] = 44   
            elif setting != "None":
                if c[2] == "bool":
                    self.conf[c[0]] = int(setting)
                else:
                    self.conf[c[0]] = setting
        with open("/home/out/1.log",mode="w+") as f:
            t = ""
            for k,v in self.conf.items():
                t = t + k + ":" +str(v) + '\n'
            f.write(t)

# this is the entry point of your addon, execution of your script will start here
if (__name__ == '__main__'):
    # define your xml window and pass these four (kodi 17) or five (kodi 18) arguments (more optional items can be passed as well):
    # 1 'the name of the xml file for this window', 
    # 2 'the path to your addon',
    # 3 'the name of the folder that contains the skin',
    # 4 'the name of the folder that contains the skin xml files'
    # 5 [kodi 18] set to True for a media window (a window that will list music / videos / pictures), set to False otherwise
    # 6 [optional] if you need to pass additional data to your window, simply add them to the list
    # you'll have to add them as key=value pairs: key1=value1, key2=value2, etc...
    MAIN = main(ADDON=ADDON)
    ui = GUI('script-hostapdconf.xml', CWD, 'main', '1080i',main=MAIN) # for kodi 18 and up..
#    ui = GUI('script-testwindow.xml', CWD, 'default', '1080i', optional1='some data') # use this line instead for kodi 17 and earlier
    # now open your window. the window will be shown until you close your addon
    ui.doModal()
    # window closed, now cleanup a bit: delete your window before the script fully exits
    del ui

# the end!
