

VgcConfigRegex = r'/dev/vgc[a-z]+\d+\s+mode=max(capacity|performance)\s+sector-size=(512|4096)\s+raid=(enabled|disabled)'

helpManString = {
                "vgc-monitor" : {"help": "Utility to monitor (Virident FlashMAX II|EMC vPCIe SSD|Seagate X8 Accelerator) drives",
                                 "man": "Utility to monitor (Virident FlashMAX II|EMC vPCIe SSD|Seagate X8 Accelerator) drives" },
                "vgc-config" : {"help": "reset to factory defaults1",
                                "man": "(Virident FlashMAX II|EMC vPCIe SSD|Seagate X8 Accelerator) drive Configuration Utility" },
                "vgc-beacon" : {"help": "drive name",
                                "man": "Locate a (Virident FlashMAX II|EMC vPCIe SSD |Seagate X8 Accelerator) card by blinking its LEDs" },
                "vgc-diags" : {"help": "dumps quite detailed information",
                                "man": "(Utility  to dump diagnostic|vgc-diags)" },
                }


