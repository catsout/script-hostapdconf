import xbmc
import xbmcgui
import xbmcaddon
import subprocess
import os
import shutil

ADDON = xbmcaddon.Addon()
CWD = ADDON.getAddonInfo('path').decode('utf-8')

class GUI(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        self.main = kwargs['main']

    def onInit(self):
        self.main.read_settings()
        self.main.write_to_conf_file()

        self.tb = self.getControl(111)
        self.tb.setText(self.main.get_info())
        xbmc.executebuiltin('Container.SetViewMode(50)')
        # define a temporary list where we are going to add all the listitems to
        # give kodi a bit of (processing) time to add all items to the container
        xbmc.sleep(100)
        # this puts the focus on the top item of the container
        self.setFocusId(121)

    def onClick(self,controlId):
        if controlId == 121:
            self.main.read_settings()
            self.main.write_to_conf_file()
            self.tb.setText(self.main.ADDON.getLocalizedString(32004))
            self.main.restart_hostapd()
            self.tb.setText(self.main.get_info())

        if controlId == 122:
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
        ["wpa_passphrase","11111111","text"],
        ["addition_conf_file","/storage/.config/hostapd/addition.conf","text"]
    ] 
    conf = {
        "ieee80211ac":0,
        "wpa":2,
        "wpa_key_mgmt":"WPA-PSK",
        "rsn_pairwise":"CCMP"
    }
    conf_file = "/storage/.config/hostapd/hostapd.conf"
    def __init__(self,*arg,**kwargs):
        self.ADDON = kwargs["ADDON"]

    def open_settings(self):
        self.ADDON.openSettings()
    def get_info(self):
        def id_to_str(str_id):
            return self.ADDON.getLocalizedString(str_id)
       
        popen = subprocess.Popen(["systemctl","is-active","hostapd.service"],universal_newlines=True,stdout=subprocess.PIPE)
        if popen.communicate()[0] != 'active\n':
            return id_to_str(32005)

        self.read_settings()
        str_ids = [
            ["ssid",32101],
            ["wpa_passphrase",32102],
            ["hw_mode",32103],
            ["channel",32104]
        ]
        info = ""
        for str_id in str_ids:
            value = self.conf[str_id[0]]
            if str_id[0] == "hw_mode":
                mode = {"g":"2.4G","a":"5G"}
                value = mode[value]
            info = info + id_to_str(str_id[1]) +':'+ str(value).decode('utf-8') +'\n'
        return info

    def restart_hostapd(self):
        popen = subprocess.Popen(["systemctl","restart","hostapd.service"])
        popen.wait()
        return popen.poll()
        
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
                else:
                    self.conf["ieee80211ac"] = 0
            elif c[0] == "wmm":
                self.conf["wmm_enabled"] = setting
            elif c[0] == "channel" and self.conf["hw_mode"] == 1 and setting < 20:
                self.conf[c[0]] = 44   
            elif setting != "":
                if c[2] == "bool":
                    self.conf[c[0]] = int(setting)
                else:
                    self.conf[c[0]] = setting
    def write_to_conf_file(self):
        conf_text = ""
        addition_conf_file = ""
        for k,v in self.conf.items():
            if k == "addition_conf_file":
                addition_conf_file = v
                continue
            conf_text +=  k + "=" + str(v) + '\n'
        if os.path.exists(addition_conf_file):
            with open(addition_conf_file,mode="r") as add_f:
                conf_text += "\n" + add_f.read()
        with open(self.conf_file,mode="w+") as conf_f:
            conf_f.write(conf_text)
            

if (__name__ == '__main__'):
    MAIN = main(ADDON=ADDON)
    ui = GUI('script-hostapdconf.xml', CWD, 'main', '1080i',main=MAIN) # for kodi 18 and up..
    ui.doModal()
    # window closed, now cleanup a bit: delete your window before the script fully exits
    del ui

