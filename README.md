# CVE-2021-21086 Exploit
This exploit allows to execute a shellcode in the context of the rendering process of Adobe Acrobat Reader DC 2020.013.20074 and earlier versions on Windows 10.
Note: the shellcode used in this example pops a calc. For it to work you must disable Adobe Reader's sandbox or you can replace it with other shellcode.
You can see it in action (with the sandbox disabled) [here](https://www.youtube.com/watch?v=DlgtEqGRzwU)

For more info on how it works, read our [blogpost](https://medium.com/faraday/who-needs-js-when-youve-got-turing-complete-fonts-c6a9cadbb665).


## How to use:
1. Generate exploit charstring: `python3 .\generate_exploit_charstring.py --output charstring`.
2. Embed charstring into a pdf file: `python3 .\charstring2pdf.py --filename .\charstring --out exploit.pdf`.
3. Open pdf file with Adobe Reader DC.
