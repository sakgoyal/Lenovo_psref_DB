export const transforms = {
"Processor": Processor,
"Graphics": Graphics,
// "Chipset": "",
// "Memory": "",
// "Memory Slots": "",
// "Max Memory": "",
// "Storage": "",
// "Storage Slot": "",
// "Max Storage Support": "",
// "Card Reader": "",
// "Audio Chip": "",
// "Speakers": "",
// "Microphone": "",
// "Camera": "",
// "Battery": "",
// "Power Adapter": "",
// "Touchscreen": "",
// "Pen": "",
// "Keyboard": "",
// "Touchpad": "",
// "Weight": "",
// "Case Color": "",
// "Case Material": "",
// "Surface Treatment": "",
// "Bundled Software": "",
// "WLAN + Bluetooth": "",
// "WWAN": "",
// "Ethernet": "",
// "NFC": "",
// "Security Chip": "",
// "Fingerprint Reader": "",
// "Bundled Accessories": "",
// "Green Certifications": "",
// "Physical Locks": "",
// "Other Security": "",
// "Screen-to-Body Ratio": "",
// "AI PC Category": "",
// "NPU": "",
// "Color Calibration": "",
// "Mil-Spec Test": "",
// "Optional Ports (configured)": "",
// "Special Features": "",
// "RAID Preset": "",
// "SIM Card": "",
// "System Management": "",
// "Smart Card Reader": "",
} as const;

function Processor(input: string): string {
	  return input.replace(/\(.*\)/, "");
}

function Graphics(input: string): string {
	let ret = input;
	ret = ret.replace(/GPU,?/, "");
	ret = ret.replace(/GDDR[6-7],?/, "");
	ret = ret.replace(/\d+MHz,?/, "");
	ret = ret.replace(/\d+ AI TOPS,?/, "");
	ret = ret.replace(/Generation(\t?),?/, "");
	ret = ret.replace(/RTX,?/, "");
	ret = ret.replace(/GTX,?/, "");
	ret = ret.replace(/GeForce/, "");
	ret = ret.replace(/NVIDIA/, "");
	ret = ret.replace(/Intel/, "");
	ret = ret.replace(/AMD/, "");
	return ret;
}
