#!/usr/bin/env python3

import json

# *******************************************
# Program config class
# *******************************************
class Config():
    # Initializer / Instance Attributes
    def __init__(self, configFile):

        # Configuration filename.
        self.cf = configFile

        # Version of configuration.
        self.ConfigVersion = 2

        # Logger configuration values
        self.DebugLevel = 10
        self.LogFileSize = 100000
        self.LogBackups = 3

        # Conversation configuration values.
        self.MyHandle = ""
        self.MaxMessages = 100

        # Image name status indication.
        self.PicRendering = {
            "PicCodedBgCol": "#dddddd",
            "PicCodedBorderColDef": "#000000",
            "PicCodedBorderColFileCoded": "#00e600",
            "PicCodedFileButton": "#99ff99",
            "PicCodedBorderColSmsCoded": "#ff8c1a",
            "PicCodedSmsButton": "#ffcc99"
        }

        # Conversation rendering.
        self.SmsRender = {
            "TextWidth" : 450,
            "SameMsgTime" : 15,
            "BubbleRadius" : 20,
            "BorderColMax" : 70,
            "FillColMin" : 225,
            "FontSizePx" : 14
        }

        # Maximum embedded file size ratio.
        self.MaxEmbedRatio = 0.5

        # Include password when embedding.
        self.IncludePasswd = 0
        self.KeepPassword = 1

        # Read / update configuration from file.
        self.readConfig()

    # *******************************************
    # Read Json configuration file.
    # *******************************************
    def readConfig(self):
        try:
            with open(self.cf) as config_file:
                config = json.load(config_file)

                # Check configuration version.
                # If version not a match then update completely.
                if config["ConfigVersion"] != self.ConfigVersion:
                    print("Upgrading configuration file.")
                    # Save configuration to file.
                    self.saveConfig()

                # Update configuration values if possible.
                # If not, just update with default + whatever values read.
                updateConfig = False
                paramSaved = ""
                try:
                    self.DebugLevel = config["DebugLevel"]
                except Exception:
                    updateConfig = True
                try:
                    self.LogFileSize = config["LogFileSize"]
                except Exception:
                    updateConfig = True
                try:
                    self.LogBackups = config["LogBackups"]
                except Exception:
                    updateConfig = True
                try:
                    paramSaved = self.MyHandle
                    self.MyHandle = config["MyHandle"]
                except Exception:
                    self.MyHandle = paramSaved
                    updateConfig = True
                try:
                    paramSaved = self.MaxMessages
                    self.MaxMessages = config["MaxMessages"]
                except Exception:
                    self.MaxMessages = paramSaved
                    updateConfig = True
                try:
                    paramSaved = self.PicRendering["PicCodedBgCol"]
                    self.PicRendering["PicCodedBgCol"] = config["PicRendering"]["PicCodedBgCol"]
                except Exception:
                    self.PicRendering["PicCodedBgCol"] = paramSaved
                    updateConfig = True
                try:
                    paramSaved = self.PicRendering["PicCodedBorderColDef"]
                    self.PicRendering["PicCodedBorderColDef"] = config["PicRendering"]["PicCodedBorderColDef"]
                except Exception:
                    self.PicRendering["PicCodedBorderColDef"] = paramSaved
                    updateConfig = True
                try:
                    paramSaved = self.PicRendering["PicCodedBorderColFileCoded"]
                    self.PicRendering["PicCodedBorderColFileCoded"] = config["PicRendering"]["PicCodedBorderColFileCoded"]
                except Exception:
                    self.PicRendering["PicCodedBorderColFileCoded"] = paramSaved
                    updateConfig = True
                try:
                    paramSaved = self.PicRendering["PicCodedFileButton"]
                    self.PicRendering["PicCodedFileButton"] = config["PicRendering"]["PicCodedFileButton"]
                except Exception:
                    self.PicRendering["PicCodedFileButton"] = paramSaved
                    updateConfig = True
                try:
                    paramSaved = self.PicRendering["PicCodedBorderColSmsCoded"]
                    self.PicRendering["PicCodedBorderColSmsCoded"] = config["PicRendering"]["PicCodedBorderColSmsCoded"]
                except Exception:
                    self.PicRendering["PicCodedBorderColSmsCoded"] = paramSaved
                    updateConfig = True
                try:
                    paramSaved = self.PicRendering["PicCodedSmsButton"]
                    self.PicRendering["PicCodedSmsButton"] = config["PicRendering"]["PicCodedSmsButton"]
                except Exception:
                    self.PicRendering["PicCodedSmsButton"] = paramSaved
                    updateConfig = True
                try:
                    paramSaved = self.SmsRender["TextWidth"]
                    self.SmsRender["TextWidth"] = config["SmsRender"]["TextWidth"]
                except Exception:
                    self.SmsRender["TextWidth"] = paramSaved
                    updateConfig = True
                try:
                    paramSaved = self.SmsRender["SameMsgTime"]
                    self.SmsRender["SameMsgTime"] = config["SmsRender"]["SameMsgTime"]
                except Exception:
                    self.SmsRender["SameMsgTime"] = paramSaved
                    updateConfig = True
                try:
                    paramSaved = self.SmsRender["BubbleRadius"]
                    self.SmsRender["BubbleRadius"] = config["SmsRender"]["BubbleRadius"]
                except Exception:
                    self.SmsRender["BubbleRadius"] = paramSaved
                    updateConfig = True
                try:
                    paramSaved = self.SmsRender["BorderColMax"]
                    self.SmsRender["BorderColMax"] = config["SmsRender"]["BorderColMax"]
                except Exception:
                    self.SmsRender["BorderColMax"] = paramSaved
                    updateConfig = True
                try:
                    paramSaved = self.SmsRender["FillColMin"]
                    self.SmsRender["FillColMin"] = config["SmsRender"]["FillColMin"]
                except Exception:
                    self.SmsRender["FillColMin"] = paramSaved
                    updateConfig = True
                try:
                    paramSaved = self.SmsRender["FontSizePx"]
                    self.SmsRender["FontSizePx"] = config["SmsRender"]["FontSizePx"]
                except Exception:
                    self.SmsRender["FontSizePx"] = paramSaved
                    updateConfig = True
                try:
                    paramSaved = self.MaxEmbedRatio
                    self.MaxEmbedRatio = config["MaxEmbedRatio"]
                except Exception:
                    self.MaxEmbedRatio = paramSaved
                    updateConfig = True
                try:
                    paramSaved = self.IncludePasswd
                    self.IncludePasswd = config["IncludePasswd"]
                except Exception:
                    self.IncludePasswd = paramSaved
                    updateConfig = True
                try:
                    paramSaved = self.KeepPassword
                    self.KeepPassword = config["KeepPassword"]
                except Exception:
                    self.KeepPassword = paramSaved
                    updateConfig = True

                # If required, i.e. couldn't update all data from user configuration, then save default.
                if updateConfig:
                    print("Saving configuration file due to user changed parameter.")
                    self.saveConfig()

        except Exception:
            # Create default configuration file.
            print("Saving default configuration data.")
            self.saveConfig()
        
    # *******************************************
    # Save Json configuration file.
    # *******************************************
    def saveConfig(self):

        # Format configuration data.
        cfgDict = {
            "ConfigVersion" : self.ConfigVersion,
            "DebugLevel" : self.DebugLevel,
            "LogFileSize" : self.LogFileSize,
            "LogBackups" : self.LogBackups,
            "MyHandle" : self.MyHandle,
            "MaxMessages" : self.MaxMessages,
            "PicRendering" : self.PicRendering,
            "SmsRender" : self.SmsRender,
            "MaxEmbedRatio" : self.MaxEmbedRatio,
            "IncludePasswd" : self.IncludePasswd,
            "KeepPassword" : self.KeepPassword,
        }

        # Open file for writing.
        try:
            outfile = open(self.cf, 'w')
            outfile.write(json.dumps(cfgDict, sort_keys=False, indent=4, ensure_ascii=False))
            outfile.close()
        except Exception:
            print("Failed to create default configuration file : {0:s}".format('autonav.json'))
