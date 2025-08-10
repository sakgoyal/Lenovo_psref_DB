category_names = {
    2147483647: "Category",
    2147483646: "Brand",
    41: "Country / Region",
    66: "AI (Artificial Intelligence)",
    36: "Processor Generation",
    16: "Processor",
    9: "Graphics",
    12: "Memory",
    30: "Storage Type",
    22: "Storage",
    6: "Screen Size",
    28: "Display Resolution",
    23: "Touchscreen",
    32: "WLAN",
    25: "WWAN",
    31: "Fingerprint Reader",
    15: "Pen",
    3: "Battery",
    33: "System Management",
    13: "Preload OS",
    4: "Bundled Software",
    2: "Base Warranty",
    63: "Certificates"
}

category_map = {
    2147483647: {1: "Laptops"},
    2147483646: {12: "ThinkPad", 8: "ThinkBook", 13: "IdeaPad", 1: "Legion", 10: "Yoga"},
    41: {
        211: "Africa-French-Portuguese", 212: "Africa-UK", 861: "Algeria", 213: "Argentina", 214: "Australia", 215: "Austria",
        216: "Azerbaijan", 218: "Belgium", 222: "Brazil", 223: "Bulgaria", 224: "CA Group", 225: "Cambodia, Laos", 226: "Canada",
        227: "Caribbean Group", 229: "Chile", 231: "CIS", 233: "Croatia", 234: "Croatia, Slovenia", 235: "Cyprus",
        237: "Czech Republic, Slovakia", 239: "Denmark", 241: "Egypt", 242: "Emat-FR", 244: "Emat-UK",
        245: "Estonia, Latvia, Lithuania", 248: "France", 249: "Georgia", 250: "Germany", 251: "Greece",
        252: "Hong Kong S.A.R. of China", 253: "Hungary", 254: "Iceland", 255: "India", 256: "Indonesia", 257: "Ireland",
        260: "Israel", 261: "Italy", 262: "Japan", 264: "Kazakhstan", 266: "Korea", 267: "LA Group", 268: "Lebanon",
        269: "Luxembourg", 270: "Malaysia", 271: "Mexico", 272: "Middle East", 273: "Middle East EM", 276: "Morocco",
        278: "Netherlands", 279: "New Zealand", 282: "Nordics", 283: "Norway", 284: "Pakistan", 287: "Philippines",
        289: "Poland", 290: "Portugal", 291: "Romania", 292: "Russia", 293: "Saudi Arabia", 294: "Serbia",
        295: "Singapore", 297: "Slovenia", 298: "South Africa", 299: "South Africa Off Shore Group", 811: "South East Europe",
        300: "Spain", 301: "Sri Lanka", 302: "Sweden", 303: "Switzerland", 306: "Taiwan, China", 307: "Thailand",
        310: "Türkiye", 312: "UAE", 314: "UK", 315: "UK Group", 321: "USA", 316: "Ukraine", 323: "Vietnam"
    },
    66: {907: "Copilot+ PC", 904: "AI PC", 906: "AI-Ready Workstations", 905: "AI-Powered Gaming PCs"},
    36: {
        856: "Intel Core Ultra (Series 2)", 857: "Intel Core Ultra (Series 1)", 863: "Intel Core (Series 2)",
        855: "Intel Core (Series 1)", 589: "14th Gen Intel", 588: "13th Gen Intel", 587: "12th Gen Intel",
        849: "AMD Ryzen AI 300", 913: "AMD Ryzen 200", 598: "AMD Ryzen 8000", 597: "AMD Ryzen 7000",
        595: "AMD Ryzen 5000", 594: "AMD Athlon 7000"
    },
    16: {
        569: "Intel Core Ultra 5", 570: "Intel Core Ultra 7", 571: "Intel Core Ultra 9", 561: "Intel Core",
        901: "AMD Ryzen AI 5", 862: "AMD Ryzen AI 7"
    },
    9: {419: "Integrated", 879: "NVIDIA GeForce RTX 50 Series"},
    12: {479: "8GB", 461: "16GB", 465: "24GB", 468: "32GB", 472: "48GB", 475: "64GB", 480: "96GB", 457: "128GB"},
    30: {757: "SSD", 745: "2x SSD"},
    22: {711: "128GB - 512GB (incl.)", 733: "512GB - 1TB (incl.)", 718: "1TB - 2TB (incl.)"},
    6: {364: '13"', 367: '14"', 370: '15"', 372: '16"', 378: '18-20"'},
    28: {348: "FHD", 344: "2K", 341: "2.5K", 342: "2.8K", 345: "3.2K", 347: "4K"},
    23: {839: "Touch", 838: "Non-touch"},
    32: {794: "802.11ax (Wi-Fi 6)", 795: "802.11ax (Wi-Fi 6E)", 796: "802.11be (Wi-Fi 7)"},
    25: {847: "Non-WWAN"},
    31: {834: "Fingerprint Reader", 835: "No Fingerprint Reader"},
    15: {523: "Pen Bundled", 829: "Pen Not Supported"},
    3: {807: "41~50Wh", 808: "51~60Wh", 809: "61~70Wh", 810: "71~80Wh", 33: "Above 81Wh"},
    33: {763: "AMD PRO", 764: "DASH", 766: "Intel vPro Enterprise"},
    13: {507: "Windows 11 Pro", 505: "Windows 11 Home", 502: "Windows 10 Pro"},
    4: {
        943: "Microsoft 365 Basic", 949: "Office H&S", 950: "Office Home", 953: "Office Trial",
        931: "Lenovo AI Now", 940: "Intel Connectivity Performance Suite"
    },
    2: {12: "1-year", 14: "3-year"},
    63: {868: "Intel Evo Platform"}
}

encoded = "2147483647:1;41:226-255-307-321;36:856-863-849;12:468;6:370-372-378"

# decode
for part in encoded.split(";"):
    cat_id, selections = part.split(":")
    cat_id = int(cat_id)
    cat_name = category_names.get(cat_id, f"Unknown ({cat_id})")
    ids = [int(x) for x in selections.split("-")]
    values = [category_map.get(cat_id, {}).get(i, str(i)) for i in ids]
    print(f"{cat_name}: {', '.join(values)}")
