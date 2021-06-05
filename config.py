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
        self.ConfigVersion = 1

        # Logger configuration values
        self.DebugLevel = 10
        self.LogFileSize = 100000
        self.LogBackups = 3

        # My handle for text messaging.
        self.MyHandle = ""

        # Image name status indication.
        self.PicRendering = {
            "PicCodedBgCol" : "#dddddd",
            "PicCodedBorderColDef" : "#000000",
            "PicCodedBorderColCoded" : "#00ff00",
            "PicCodedButton": "#00aa00"
        }

        # Conversation rendering.
        self.SmsRender = {
            "TextWidth" : 450,
            "SameMsgTime" : 30,
            "BubbleRadius" : 20,
            "MeSMSBorderCol" : "#0080ff",
            "ThemSMSBorderCol" : "#ff6600",
            "MeSMSBkGrndCol" : "#e6f2ff",
            "ThemSMSBkGrndCol" : "#ffe0cc"
        }

        # Maximum embedded file size ratio.
        self.MaxEmbedRatio = 0.5

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
                    self.MyHandle = config["MyHandle"]
                except Exception:
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
                    paramSaved = self.PicRendering["PicCodedBorderColCoded"]
                    self.PicRendering["PicCodedBorderColCoded"] = config["PicRendering"]["PicCodedBorderColCoded"]
                except Exception:
                    self.PicRendering["PicCodedBorderColCoded"] = paramSaved
                    updateConfig = True
                try:
                    paramSaved = self.PicRendering["PicCodedButton"]
                    self.PicRendering["PicCodedButton"] = config["PicRendering"]["PicCodedButton"]
                except Exception:
                    self.PicRendering["PicCodedButton"] = paramSaved
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
                    paramSaved = self.SmsRender["MeSMSBorderCol"]
                    self.SmsRender["MeSMSBorderCol"] = config["SmsRender"]["MeSMSBorderCol"]
                except Exception:
                    self.SmsRender["MeSMSBorderCol"] = paramSaved
                    updateConfig = True
                try:
                    paramSaved = self.SmsRender["ThemSMSBorderCol"]
                    self.SmsRender["ThemSMSBorderCol"] = config["SmsRender"]["ThemSMSBorderCol"]
                except Exception:
                    self.SmsRender["ThemSMSBorderCol"] = paramSaved
                    updateConfig = True
                try:
                    paramSaved = self.SmsRender["MeSMSBkGrndCol"]
                    self.SmsRender["MeSMSBkGrndCol"] = config["SmsRender"]["MeSMSBkGrndCol"]
                except Exception:
                    self.SmsRender["MeSMSBkGrndCol"] = paramSaved
                    updateConfig = True
                try:
                    paramSaved = self.SmsRender["ThemSMSBkGrndCol"]
                    self.SmsRender["ThemSMSBkGrndCol"] = config["SmsRender"]["ThemSMSBkGrndCol"]
                except Exception:
                    self.SmsRender["ThemSMSBkGrndCol"] = paramSaved
                    updateConfig = True
                try:
                    self.MaxEmbedRatio = config["MaxEmbedRatio"]
                except Exception:
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
            "PicRendering" : self.PicRendering,
            "MaxEmbedRatio" : self.MaxEmbedRatio,
            "SmsRender" : self.SmsRender,
        }

        # Open file for writing.
        try:
            outfile = open(self.cf, 'w')
            outfile.write(json.dumps(cfgDict, sort_keys=False, indent=4, ensure_ascii=False))
            outfile.close()
        except Exception:
            print("Failed to create default configuration file : {0:s}".format('autonav.json'))
