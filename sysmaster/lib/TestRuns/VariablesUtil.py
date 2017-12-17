

VgcConfigRegex = r'/dev/vgc[a-z]+\d+\s+mode=max(capacity|performance)\s+sector-size=(512|4096)\s+raid=(enabled|disabled)'

helpManString = {
                # putting III? will match II and III
                "vgc-monitor" : {"help": "Utility to monitor \S* (FlashMAX \S+|EMC vPCIe SSD|Seagate X8 Accelerator) drives",
                                 "man": "Utility to monitor \S* (FlashMAX \S+|EMC vPCIe SSD|Seagate X8 Accelerator) drives" },
                "vgc-config" : {"help": "reset to factory defaults",
                                "man": "(FlashMAX \S+|EMC vPCIe SSD|Seagate X8 Accelerator) drive Configuration Utility" },
                "vgc-beacon" : {"help": "drive name",
                                #"man": "Locate a .* card by blinking its LEDs" },
                                "man": "Locate" },
                "vgc-diags" : {"help": "dumps quite detailed information",
                                "man": "(Utility  to dump diagnostic|vgc-diags)" },
                }


