# -*- coding: utf-8 -*-

from Tkinter import *
import tkFileDialog, tkMessageBox, os, glob, fileinput, sys
from xml.dom.minidom import parse
from ESM_dictionaries import dict

class App(Frame):
    def  __init__(self, master):
        Frame.__init__(self, master)
        self.grid()
        self.create_widgets()
        
        msg = Text(master)
        
        class infoMessage():
            def write(self, s):
                msg.insert(END, s)
                msg.yview_pickplace("end")
                msg.update_idletasks()
                
        Label(master, text="").grid(row=4)
        msg.config(bg="azure")
        msg.place(x=5, y=170, height=155, width=530)
        
        sys.stdout = infoMessage()
        
        self.file_options = options = {}
        options["initialdir"] = "B:\\DTP DEPARTMENT\\_Projects MOCA"
        options['parent'] = master
        options['title'] = 'Join XML v1'
    
    def create_widgets(self):
        about = Label(master, text="\n\
                This app will generate the .xml vehicle file.\n\n")
        w = Label(master, text="          Folder Path:    ")
        var = StringVar()
        e = Entry(master, textvariable=var, width=52)
        b = Button(master, text="Browse", command=lambda:var.set(tkFileDialog.askdirectory(**self.file_options)))
        
        about.grid(row=0, column=1, columnspan=5)
        w.grid(row=1, column=1)
        e.grid(row=1, column=2, columnspan=3)
        b.grid(row=1, column=5)
        
        Label(master, text="").grid(row=2)
        
        def languages():
            dictlist = []
            for key, value in dict['vehicle'].iteritems():
                dictlist.append(value)
            return dictlist
        
        def replaceText(node, newText):
            if node.firstChild.nodeType != node.TEXT_NODE:
                raise Exception("node does not contain text")
            
            node.firstChild.replaceWholeText(newText)
        
        def join(path, filename):
#            print path
            file_list = glob.glob("%s/*_VVV_*.xml" %path)
            fn = "_" + filename
            nf = os.path.join(path, fn)
            with open(nf, "wb") as file:
                input_lines = fileinput.input(file_list)
                file.writelines(input_lines)
        
        def correctfile(path, filename):
            fn = "_" + filename
            nf = os.path.join(path, fn)
            print nf
            
            fin = open(nf)
            final_file = os.path.join(path, filename)
            fout = open(final_file, "w+")
            
            for line in fin:
                line = line.replace("</vehicle>", "")
                fout.write(line)
            fin.close()
            fout.close()
            
            f = open(final_file, 'a')
            f.write("</vehicle>")
            f.close()
            os.remove(nf)
            
        
        def gen_first_file(path):
#            print path
            prj = os.path.dirname(os.path.dirname(path))
            enpath = os.path.join(prj, "English")
            print path # for test purpose
            print enpath # for test purpose
            try:
                fl = next(os.walk(enpath))[1][0]
            except:
                tkMessageBox.showwarning("ERROR", "ERROR: \nPlease choose the correct directory. Verify to choose other language than english.\nThe application will quit.")
                print "\nERROR: \nPlease choose the correct directory. Verify to choose other language folder than english."
                quit()
            np = os.path.join(enpath, fl, "vehicle")
#            print np
            sp = path.split('\\')
            print sp
            language = sp[-2].lower()
            print language
            
            f = None
            for file in os.listdir(np):
#                print file
                if ("00.xml" or "for_pasting.xml") in file:
                    f = file
                    tf = file
                    print tf
                else:
                    pass
            if f != None:
                f = os.path.join(np, f)
                print f
            else:
                print "Please verify the vehicle folder to contain the for pasting file."
            try:
                xmldoc = parse(f)
            except:
                tkMessageBox.showwarning("ERROR", "ERROR: \nPlease verify the english vehicle folder to contain the for pasting file.\nThe application will quit.")
                print "Please verify the english vehicle folder to contain the for pasting file."
                quit()
                
            node =  xmldoc.getElementsByTagName("vehicle")
            vehicle = node[0]
            modeldesc = vehicle.firstChild.childNodes[0].data
            print "Model Description: %s" %modeldesc
            
#            attributes = vehicle.attributes.keys()
#            print attributes

            for lang in languages():
                if lang[0] == language:
                    al = lang[1]
                    lc = lang[2]
                    print al, lc
                else:
                    continue
                      
            vehicle.setAttribute("authlang", al)
            disprevdate = vehicle.attributes["disprevdate"].value
            pubcode = vehicle.attributes["pubcode"].value
            l = list(disprevdate)
            lpc = list(pubcode)
            lmd = list(modeldesc)
            print l, lpc
            try:
                l[4] = lc
            except:
                print "ERROR: Please verify the english vehicle file."
            try:
                lpc[4] = lc
            except:
                tkMessageBox.showwarning("ERROR", "ERROR: \nPlease verify the english vehicle pasting file.\nThe application will quit.")
                quit()
            lmd[8] = lc
            if len(lc) > 1:
                l[5] = ''
                lpc[5] = ''
                lmd[9] = ''
            else:
                pass
            l = ''.join(l)
            lpc = ''.join(lpc)
            lmd = ''.join(lmd)
            print l, lpc, lmd
            vehicle.setAttribute("disprevdate", l)
            vehicle.setAttribute("pubcode", lpc)
            mdesc = vehicle.getElementsByTagName('modeldesc')[0]
            replaceText(mdesc, lmd)
            
            
            print "=" * 65
            authlang = vehicle.attributes["authlang"]
            print "Authoring Language: %s" %authlang.value
            disprevdate = vehicle.attributes["disprevdate"]
            print "Publication number: %s" %disprevdate.value
            modelcode = vehicle.attributes["modelcode"]
            print "Model Code: %s" %modelcode.value
            pubcode = vehicle.attributes["pubcode"]
            print "Publication Code: %s" %pubcode.value
            print "=" * 65
            
            nf = open(os.path.join(path, tf), 'w')
            xmldoc.writexml(nf)
            nf.close()
            
            newfilename = lmd + '.xml'
            join(path, newfilename)
            correctfile(path, newfilename)
                        
            print ('\nTASK COMPLETED')
            tkMessageBox.showwarning("TASK COMPLETED", "The .xml files are joined. \nYou can now close the application.")
        
        def confirm_path():
            path = var.get()
            if path != "":
                if tkMessageBox.askyesno("Working Folder", "The selected working folder is: \n\n" + path + "\n\nIs this correct?"):
                    print ("Joining files... \nPlease wait until you see the message TASK COMPLETED.\n")
#                    print (path)
                    gen_first_file(path)
            else:
                print "Please try again!"
            
        start = Button(master, text="         Start         ", command=confirm_path)
        start.grid(row=3, column=3, columnspan=1)
            
            
if __name__ == "__main__":        
    master = Tk()
    master.title("Join XML v1")
    master.geometry("540x330")
    master.resizable(width=FALSE, height=FALSE)
    
    app = App(master)
    master.mainloop()