import kivy
kivy.require('2.2.1') # replace with your current kivy version !

import os
import thsGen
import requests
from getSVG import getSVG
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.event import EventDispatcher

kv = Builder.load_file("thsGenerator.kv")

Window.size = (1500,900)

class MyEventDispatcher(EventDispatcher):
    def __init__(self, **kwargs):
        self.register_event_type('on_thsGen')
        super(MyEventDispatcher, self).__init__(**kwargs)

    def on_thsGen(self):
        pass

    def on_strucShowRequest(self):
        pass
    
ev = MyEventDispatcher()

def strucShow(self):
    App.get_running_app().root.get_screen("strucShowWindow").ids.strucShowBox.clear_widgets()

    for file in os.listdir():
        if file.startswith("struc_"):
            os.remove(file)

    print(self.text)
    fileName = getSVG(self.text)

    App.get_running_app().root.current = "strucShowWindow"
    App.get_running_app().root.get_screen("strucShowWindow").ids.strucLabel.text = f"polymer graph visual for: {self.text}"
    App.get_running_app().root.get_screen("strucShowWindow").ids.strucShowBox.add_widget(Image(source = f"struc_{fileName}.png", size_hint = (1, 1), allow_stretch = True))

class fileManager(Screen):

    names = []
    sequences = []

    def submitFromFasta(self):    
        if self.manager.get_screen("fileManager").ids.fastaSelectBox.children:
            print("submitting miRNA")
            print(names)
            print(sequences)

            reverseList = []

            for i, child in enumerate(self.manager.get_screen("fileManager").ids.fastaSelectBox.children):
                if i % 3 == 0:
                    reverseList.append(child.active)

            for i, val in enumerate(reverseList):
                if val:
                    sequences[i] = thsGen.reverse(sequences[i])
                    print("reversing")

            self.ids.fastaSubmitButton.disabled = True
            submitDict = dict(zip(names, sequences))  
            thsGen.miRNADict = submitDict
            print(thsGen.miRNADict)
            thsGen.start()
            thsGen.thsPlotSave()
            thsGen.triggerPlotSave()
            thsGen.complexPlotSave()
            self.ids.nextButton3.disabled = False
            ev.dispatch("on_thsGen")
        else:
            print("input something, dingus")

    def selected(self, fileName):

        global manager
        manager = self.manager

        self.ids.fastaSearchGrid.clear_widgets()

        def removemiRNA(self):
            print("removing miRNA")
            selfIdx = manager.get_screen("fileManager").ids.fastaSelectBox.children.index(self)
            buttonList = manager.get_screen("fileManager").ids.fastaSearchGrid.children[0::3]
            labelList = [x.text for x in manager.get_screen("fileManager").ids.fastaSearchGrid.children[2::3]]

            name = manager.get_screen("fileManager").ids.fastaSelectBox.children[selfIdx + 1].text

            findButtonIdx = labelList.index(name)

            buttonList[findButtonIdx].disabled = False  

            manager.get_screen("fileManager").ids.fastaSelectBox.remove_widget(manager.get_screen("fileManager").ids.fastaSelectBox.children[selfIdx])
            manager.get_screen("fileManager").ids.fastaSelectBox.remove_widget(manager.get_screen("fileManager").ids.fastaSelectBox.children[selfIdx])
            manager.get_screen("fileManager").ids.fastaSelectBox.remove_widget(manager.get_screen("fileManager").ids.fastaSelectBox.children[selfIdx - 1])

            delIdx = names.index(name)

            del names[delIdx]
            del sequences[delIdx]   

        def addmiRNA(self):
            print("adding miRNA")
            if len(names) < 3:
                self.disabled = True
                selfIdx = manager.get_screen("fileManager").ids.fastaSearchGrid.children.index(self)
                name = manager.get_screen("fileManager").ids.fastaSearchGrid.children[selfIdx + 2].text
                sequence = manager.get_screen("fileManager").ids.fastaSearchGrid.children[selfIdx + 1].text
                names.append(name)
                sequences.append(sequence.strip())
                manager.get_screen("fileManager").ids.fastaSelectBox.add_widget(Label(text = name, size_hint = (0.7, 1/3)))
                manager.get_screen("fileManager").ids.fastaSelectBox.add_widget(Button(text = "remove", font_size = 12, size_hint = (0.2, 1/3), on_press = removemiRNA))
                manager.get_screen("fileManager").ids.fastaSelectBox.add_widget(CheckBox(size_hint = (0.1, 1/3)))
                
            else:
                manager.get_screen("fileManager").ids.fastaSelectText.text = "> 3 miRNA is not supported" 
            
            print(names)
            print(sequences)

        print(fileName[0])
        if str(fileName[0].split("/")[-1]).endswith('.fa'):
            with open(fileName[0], "r") as file:
                print(len(file.readlines()))
                print(set([x.strip() for x in open(fileName[0], "r").readlines()]))
                print([x.strip() for x in open(fileName[0], "r").readlines()])
                if len(set([x.strip() for x in open(fileName[0], "r").readlines()])) == len([x.strip() for x in open(fileName[0], "r").readlines()]):    
                    print("no repeats detected")
                    if len(open(fileName[0], "r").readlines()) % 2 == 0 and len(open(fileName[0], "r").readlines()) < 7:
                        print("correct number of lines")
                        if all([x.startswith(">") for x in open(fileName[0], "r").readlines()[::2]]):
                            print("all name lines begin with >")
                            if all(thsGen.checkCorrectCharacters(x.strip()) and len(x) > 14 and len(x) < 30 for x in open(fileName[0], "r").readlines()[1::2]):
                                print("sequences correct")
                                for line in open(fileName[0], "r").readlines():
                                    if line.startswith(">"): 
                                        self.ids.fastaSearchGrid.add_widget(Label(text = line[1::].strip(), size_hint_y = None, size = (10, 20), size_hint = (0.3, None)))
                                    else:
                                        self.ids.fastaSearchGrid.add_widget(Label(text = line.strip(), size_hint_y = None, size = (10, 20), size_hint = (0.7, None)))
                                        self.ids.fastaSearchGrid.add_widget(Button(text = "Add miRNA", size = (10, 50),  size_hint = (0.2, None), on_press = addmiRNA))
                            else:
                                self.ids.fastaSearchGrid.add_widget(Label(text = "Invalid sequences"))
                        else:
                            self.ids.fastaSearchGrid.add_widget(Label(text = "Invalid strand names"))
                    else:
                        self.ids.fastaSearchGrid.add_widget(Label(text = "Invalid file layout"))              
                else:
                    self.ids.fastaSearchGrid.add_widget(Label(text = "Invalid file layout"))
        else:
            self.ids.fastaSearchGrid.add_widget(Label(text = "Invalid file type"))
        
        print(sequences)
        buttons = []
        text = []
        print(manager.get_screen("fileManager").ids.fastaSearchGrid.children)
        for x in manager.get_screen("fileManager").ids.fastaSearchGrid.children[0::3]:
            print(x.text)
            buttons.append(x)
        for x in manager.get_screen("fileManager").ids.fastaSearchGrid.children[1::3]:
            print(x.text)
            text.append(x)

        print(buttons)
        print(text)

        for sequence in sequences:
            for (label, button) in zip(text, buttons):
                if sequence == label.text:
                    button.disabled = True

class strucShowScreen(Screen):
    pass

class mainWindow(Screen):

    def reverse(self, instance, value):
        print(self, value)

    def addMiRNA(self):
        print("miRNA added")

        if len(self.children[0].children[1].children) != 9:
            self.ids.inputGrid.add_widget(TextInput(multiline = False, size_hint_x = 0.3, font_size = 18, size_hint_y = None, height = 45))

            self.ids.inputGrid.add_widget(TextInput(multiline = False, size_hint_x = 0.5, font_size = 18, size_hint_y = None, height = 45))

            self.ids.inputGrid.add_widget(CheckBox(size_hint_x = 0.2, size_hint_y = None, height = 45))
            

        else:
            self.ids.promptLabel.text = "The software does not support more than 3 miRNA strands"
    
    def removeMiRNA(self):
        print("miRNA removed")
        
        if len(self.children[0].children[1].children) > 4:
            for i in range(0, 3):
                self.ids.inputGrid.remove_widget(self.children[0].children[1].children[0])
        else:
            self.ids.promptLabel.text = "You must input 1 or more miRNA"

    def getMirBase(self):
        print("getting miRBase!")
        with open("mature.fa", 'wb') as f:
            f.write(requests.get("https://mirbase.org/download/mature.fa").content)
        self.manager.current = "mirBaseWindow"

    def browseFasta(self):
        print("opening file manager")
        self.manager.current = "fileManager"

    def clear(self):
        for i, child in enumerate(self.children[0].children[1].children):
            if (i % 3 != 0):
                child.text = ""
            else:
                print(child.active)
        
    
    def submit(self):
        print("submitted")
        
        global manager
        manager = self.manager

        contents = []
        for i, child in enumerate(self.children[0].children[1].children):
            if (i % 3 != 0):
                contents.append(child.text)

        if all([i != "" for i in contents]):

            reverseList = []

            for i, child in enumerate(self.children[0].children[1].children):
                if (i % 3 == 0):
                    reverseList.append(child.active)
                    print(reverseList)

            miRNANames = contents[1:][::2]
            namesCheckSet = set(miRNANames)

            miRNASequences = contents[::2]
            seqCheckSet = set(miRNASequences)

            for i, val in enumerate(reverseList):
                if val:
                    miRNASequences[i] = thsGen.reverse(miRNASequences[i])
                    print("reversing")

            if (len(seqCheckSet) == len(miRNASequences) and len(namesCheckSet) == len(miRNANames)):

                checkList = [thsGen.checkCorrectCharacters(i) for i in miRNASequences]

                if all(checkList):

                    if all(len(i) > 14 for i in miRNASequences):
                        self.ids.submitButton.disabled = True
                        dict = {miRNANames[i]: str(miRNASequences[i]).upper() for i in range(len(contents[1:][::2]))}
                        print(dict)
                        thsGen.miRNADict = dict
                        thsGen.start()
                        thsGen.thsPlotSave()
                        thsGen.triggerPlotSave()
                        thsGen.complexPlotSave()
                        self.ids.promptLabel.text = "Done!"
                        self.ids.nextButton1.disabled = False
                        ev.dispatch("on_thsGen")
                    else:
                        self.ids.promptLabel.text = "Sorry, our software doesn't support miRNA strands shorter than 15nt"
                else:
                    self.ids.promptLabel.text = "One or more of your sequences contains illegal characters"
            else:
                self.ids.promptLabel.text = "Multipule miRNA strands cannot share the same name or sequence"
        else:
            self.ids.promptLabel.text = "Please fill in all of the boxes"
    
    def received(self):
        print("test event received")  
            

        # Toehold switch screen
        manager.get_screen("second").ids.thsBox.add_widget(Image(source = "ths.png"))

        thsGridText = BoxLayout(orientation = "vertical")
        manager.get_screen("second").ids.thsBox.add_widget(thsGridText)

        thsGridText.add_widget(Label(text = "Toehold switch sequence and Boltzmann sampled structures:"))
        thsGridText.add_widget(Label(text = thsGen.bestThs.sequence, font_size = 12, text_size = ((Window.size[0] - 200)/2, 50), halign = "center", valign = "top"))
        for x in thsGen.bestThs.thsSamples:
            thsGridText.add_widget(Button(text = str(x), font_size = 11, size_hint = (1, 1), on_press = strucShow))
        thsGridText.add_widget(Label(text = f"Toehold binding percentage of: {str(round(thsGen.bestThs.exposure, 2))}% Approximate minimum free energy of: {str(round(thsGen.bestThs.strucEnergy.energy, 2))} (kcal/mol)"))
        
        # Trigger screen
        if thsGen.numMiRNA > 1:
            manager.get_screen("third").ids.triggerBox.add_widget(Image(source = "trigger.png"))

            triggerGridText = BoxLayout(orientation = "vertical")
            manager.get_screen("third").ids.triggerBox.add_widget(triggerGridText)

            triggerGridText.add_widget(Label(text = "Trigger complex strand order and Boltzmann sampled structures:"))

            global bestThsOrderedStrands
            bestThsOrderedStrands = thsGen.listAddition(thsGen.bestThs.strandsUsed[0:int((len(thsGen.strands)-1)/2)], thsGen.strands[int((len(thsGen.strands)-1)/2):int(len(thsGen.strands))])
            triggerGridText.add_widget(Label(text = ", ".join(bestThsOrderedStrands), font_size = 12, text_size = ((Window.size[0] - 200)/2, 50), halign = "center", valign = "top"))
            for x in thsGen.bestThs.triggerSamples[:10]:
                triggerGridText.add_widget(Button(text = str(x), font_size = 11, size_hint = (1, 1), on_press = strucShow))
            triggerGridText.add_widget(Label(text = f"Approximate minimum free energy of: {str(round(thsGen.triggerMFEStruc.energy, 2))} (kcal/mol)"))
            for i, j in enumerate(bestThsOrderedStrands):
                if (i % 2 == 1):
                    triggerGridText.add_widget(Label(text = "".join((j, " is the and gate between ", thsGen.getKey(bestThsOrderedStrands[i-1]), " (", bestThsOrderedStrands[i-1], ") ", " and ", thsGen.getKey(bestThsOrderedStrands[i+1]), " (", bestThsOrderedStrands[i+1], ") ")), text_size = ((Window.size[0] - 200)/2, 50), font_size = 12, halign = "center", valign = "center"))
        else:
            print("no trigger for 1 miRNA")
            manager.get_screen("third").ids.triggerBox.add_widget(Label(text = "No trigger complex is needed for 1 miRNA strand", font_size = 20))


        # Complex screen
        manager.get_screen("fourth").ids.complexBox.add_widget(Image(source = "complex.png"))
        complexGridText = BoxLayout(orientation = "vertical")
        manager.get_screen("fourth").ids.complexBox.add_widget(complexGridText)
        complexGridText.add_widget(Label(text = "Activated toehold switch suboptimal energy structures:"))
        for x in thsGen.finalComplex.subopt[:10]:
            complexGridText.add_widget(Button(text = str(x.structure), font_size = 10, size_hint = (1, 1), on_press = strucShow))
        global bindingSites
        bindingSites = ""
        for x in thsGen.finalComplex.subopt:
            bindingSite = str(x.structure)[:int(str(x.structure).find("+"))]
            bindingSites += bindingSite
        global thsActivationString
        thsActivationString = "".join(("Toehold switch activation percentage: ", str(round(100-bindingSites.count(".")*100/len(bindingSites), 2)), "%", " Approximate free energy of: ", str(round(thsGen.finalComplex.mfe[0].energy, 2)), " (kcal/mol)"))
        complexGridText.add_widget(Label(text = thsActivationString, text_size = (Window.size[0]/2, 30), size_hint_y = 0.75, font_size = 12))
        complexGridText.add_widget(Label(text = "*Toehold switch activation percentage is a measure of how many bases of the switch bind at equilibrium when the switch is open, it isn't a representation of what percentage of switches will be open", size_hint_y = 0.5, font_size = 12, text_size = (Window.size[0]/2, 40))) 

    ev.bind(on_thsGen = received)

        


class thsWindow(Screen):
    pass

class triggerWindow(Screen):
    pass

class complexWindow(Screen):

    def resultsOutput(self):
        if thsGen.numMiRNA > 1:
            print("outputting txt file")
            outputFile = open("results.txt","w")
            outputFile.write("~~~~~~~~~~~~~~~~~Toehold Switch~~~~~~~~~~~~~~~~~ \n")
            outputFile.write(f"{thsGen.bestThs.sequence} \n")
            outputFile.write(f"MFE structure: {thsGen.bestThs.strucEnergy.structure} ({str(round(thsGen.bestThs.strucEnergy.energy, 2))} kcal/mol) with a toehold exposure of {str(round(thsGen.bestThs.exposure, 2))}% \n")
            outputFile.write(f"Boltzmann sampled structures: \n")
            for x in thsGen.bestThs.thsSamples:
                outputFile.write(f"{x} \n")
            outputFile.write("\n ~~~~~~~~~~~~~~~~~Trigger Complex~~~~~~~~~~~~~~~~~ \n")
            if thsGen.numMiRNA == 1:
                outputFile.write("There is no trigger complex for a toehold switch using 1 miRNA")
                for i, j in enumerate(bestThsOrderedStrands):
                    if (i % 2 == 1):
                        outputFile.write(f'{"".join((j, " is the and gate between ", thsGen.getKey(bestThsOrderedStrands[i-1]), " (", bestThsOrderedStrands[i-1], ") ", " and ", thsGen.getKey(bestThsOrderedStrands[i+1]), " (", bestThsOrderedStrands[i+1], ") "))}')
            
            else:
                outputFile.write(f"Best strand order including and gate sequences: {', '.join(bestThsOrderedStrands)} \n")
                outputFile.write(f"Structure considering Boltzmann sampled structures: {thsGen.bestThs.triggerStruc} \n")
                outputFile.write(f"Structure considering MFE structure: {thsGen.triggerMFEStruc.structure} ({round(thsGen.triggerMFEStruc.energy, 2)} kcal/mol) \n")
                for i, j in enumerate(bestThsOrderedStrands):
                    if (i % 2 == 1):
                        outputFile.write(f'{"".join((j, " is the and gate between ", thsGen.getKey(bestThsOrderedStrands[i-1]), " (", bestThsOrderedStrands[i-1], ") ", " and ", thsGen.getKey(bestThsOrderedStrands[i+1]), " (", bestThsOrderedStrands[i+1], ") "))} \n')
                outputFile.write("With these other possible structures*: \n")
            for x in thsGen.bestThs.triggerSamples:
                outputFile.write(f"{str(x)} \n")
            outputFile.write(f"*Several trigger Boltzmann samples are given in this file because the trigger structure tends to be much more volitile and subject to forming off-target complexes so 50 of the samples are shown here to assess how likely it is for the correct complex to form \n")
            outputFile.write(f"*MFE structure may not be fully representative of the trigger complex's structure, which is why Boltzmann samples are taken. If the MFE structure closely resembles the boltzmann sampled ones, it is extremely likely to form, if not it will still be possible although at lower concentrations \n")
            outputFile.write(f"*Boltzmann samples will be more reliable and representative of in vitro reactions as hundreds of samples are taken, MFE structure is only taken into account to give an approximate free energy value and equilibrium pair probability matrix \n")
            outputFile.write("\n ~~~~~~~~~~~~~~~~~Activated Toehold Switch~~~~~~~~~~~~~~~~~ \n")
            outputFile.write(f"MFE structure: {thsGen.finalComplex.mfe[0].structure} ({round(thsGen.finalComplex.mfe[0].energy, 2)} kcal/mol) \n")
            outputFile.write(f"Toehold switch activation percentage: {round(100-bindingSites.count('.')*100/len(bindingSites), 2)}% \n")
            outputFile.write("Suboptimal energy structures: \n")
            for x in thsGen.finalComplex.subopt:
                outputFile.write(f"{x.structure} ({round(x.energy, 2)} kcal/mol) \n")
            outputFile.write("Toehold switch activation percentage is a measure of how many bases of the switch bind at equilibrium when the switch is open, it isn't a representation of what percentage of switches will be open")
            outputFile.write("Here suboptimal energy structures are used as they are incredibly similar to taking Boltzmann samples while also giving a free energy value")
            outputFile.close()
        else:
            outputFile = open("results.txt","w")
            outputFile.write("~~~~~~~~~~~~~~~~~Toehold Switch~~~~~~~~~~~~~~~~~ \n")
            outputFile.write(f"{thsGen.bestThs.sequence} \n")
            outputFile.write(f"MFE structure: {thsGen.bestThs.strucEnergy.structure} ({str(round(thsGen.bestThs.strucEnergy.energy, 2))} kcal/mol) with a toehold exposure of {str(round(thsGen.bestThs.exposure, 2))}% \n")
            outputFile.write(f"Boltzmann sampled structures: \n")
            for x in thsGen.bestThs.thsSamples:
                outputFile.write(f"{x} \n")
            outputFile.write("\n ~~~~~~~~~~~~~~~~~Activated Toehold Switch~~~~~~~~~~~~~~~~~ \n")
            outputFile.write(f"MFE structure: {thsGen.finalComplex.mfe[0].structure} ({round(thsGen.finalComplex.mfe[0].energy, 2)} kcal/mol) \n")
            outputFile.write(f"Toehold switch activation percentage: {round(100-bindingSites.count('.')*100/len(bindingSites), 2)}% \n")
            outputFile.write("Suboptimal energy structures: \n")
            for x in thsGen.finalComplex.subopt:
                outputFile.write(f"{x.structure} ({round(x.energy, 2)} kcal/mol) \n")
            outputFile.write("Toehold switch activation percentage is a measure of how many bases of the switch bind at equilibrium when the switch is open, it isn't a representation of what percentage of switches will be open")
            outputFile.write("Here suboptimal energy structures are used as they are incredibly similar to taking Boltzmann samples while also giving a free energy value")
            outputFile.close()


    def fastaOutput(self):
        print("outputting fasta file")
        fastaFile = open("output.fa", "w")
        if thsGen.numMiRNA > 1:
            fastaFile.write(">Toehold Switch \n")
            fastaFile.write(f"{thsGen.bestThs.sequence} \n")
            for i, j in enumerate(bestThsOrderedStrands):
                    if (i % 2 == 1):
                        fastaFile.write(f'{"".join((">And gate between ", thsGen.getKey(bestThsOrderedStrands[i-1]), " (", bestThsOrderedStrands[i-1], ") ", " and ", thsGen.getKey(bestThsOrderedStrands[i+1]), " (", bestThsOrderedStrands[i+1], ") "))} \n')
                        fastaFile.write(f"{j} \n")
            fastaFile.close()
        else:
            fastaFile.write(">Toehold Switch \n")
            fastaFile.write(f"{thsGen.bestThs.sequence} \n")

    
class mirBaseWindow(Screen):

    global names, sequences
    names = []
    sequences = []
    
    def search(self):

        self.ids.searchGrid.clear_widgets()

        global manager
        manager = self.manager

        global names, sequences                
        
        def removemiRNA(self):
            print("removing miRNA")
            selfIdx = manager.get_screen("mirBaseWindow").ids.mirnaSelectBox.children.index(self)
            buttonList = manager.get_screen("mirBaseWindow").ids.searchGrid.children[0::4]
            labelList = [x.text for x in manager.get_screen("mirBaseWindow").ids.searchGrid.children[3::4]]

            name = manager.get_screen("mirBaseWindow").ids.mirnaSelectBox.children[selfIdx + 1].text

            findButtonIdx = labelList.index(name)

            buttonList[findButtonIdx].disabled = False  

            manager.get_screen("mirBaseWindow").ids.mirnaSelectBox.remove_widget(manager.get_screen("mirBaseWindow").ids.mirnaSelectBox.children[selfIdx])
            manager.get_screen("mirBaseWindow").ids.mirnaSelectBox.remove_widget(manager.get_screen("mirBaseWindow").ids.mirnaSelectBox.children[selfIdx])
            manager.get_screen("mirBaseWindow").ids.mirnaSelectBox.remove_widget(manager.get_screen("mirBaseWindow").ids.mirnaSelectBox.children[selfIdx - 1])

            print(names)
            print(sequences)

            print(names.index(name))

            delIdx = names.index(name)

            del names[delIdx]
            del sequences[delIdx]  

            print(names)
            print(sequences)

        def addmiRNA(self):
            print("adding miRNA")
            if len(names) < 3:
                self.disabled = True
                selfIdx = manager.get_screen("mirBaseWindow").ids.searchGrid.children.index(self)
                name = manager.get_screen("mirBaseWindow").ids.searchGrid.children[selfIdx + 3].text
                sequence = manager.get_screen("mirBaseWindow").ids.searchGrid.children[selfIdx + 1].text
                names.append(name)
                sequences.append(sequence.strip())
                manager.get_screen("mirBaseWindow").ids.mirnaSelectBox.add_widget(Label(text = name, size_hint = (0.7, 1/3)))
                manager.get_screen("mirBaseWindow").ids.mirnaSelectBox.add_widget(Button(text = "remove", font_size = 12, size_hint = (0.2, 1/3), on_press = removemiRNA))
                manager.get_screen("mirBaseWindow").ids.mirnaSelectBox.add_widget(CheckBox(size_hint = (0.1, 1/3)))
                
            else:
                manager.get_screen("mirBaseWindow").ids.mirnaSelectText.text = "> 3 miRNA is not supported" 
        
        if self.children[0].children[-1].children[1].text:
            print("searching for miRNA")
            miRBase = open("mature.fa")
            query = self.children[0].children[-1].children[1].text
            for i, x in enumerate(miRBase.readlines()):
                if x.startswith(">hsa"):
                    if query in x.split(" ")[0]:
                        name = x.split(" ")[0][1:]
                        accession = x.split(" ")[1]
                        sequence = open("mature.fa").readlines()[i+1]
                        self.ids.searchGrid.add_widget(Label(text = name, size_hint_y = None, size = (10, 20), size_hint = (0.2, None)))
                        self.ids.searchGrid.add_widget(Label(text = accession, size_hint_y = None, size = (10, 20), size_hint = (0.2, None)))
                        self.ids.searchGrid.add_widget(Label(text = sequence, size_hint_y = None, size = (10, 20), size_hint = (0.4, None)))
                        self.ids.searchGrid.add_widget(Button(text = "Add miRNA", size = (10, 50),  size_hint = (0.2, None), on_press = addmiRNA))
        
        for name in names:
            for (label, button) in zip([x.text for x in manager.get_screen("mirBaseWindow").ids.searchGrid.children[3::4]], manager.get_screen("mirBaseWindow").ids.searchGrid.children[0::4]):
                if name == label:
                    button.disabled = True

        
    
    def submitFromBase(self):
        if self.manager.get_screen("mirBaseWindow").ids.mirnaSelectBox.children:
            print("submitting miRNA")
            print(names)
            print(sequences)

            reverseList = []

            for i, child in enumerate(self.manager.get_screen("mirBaseWindow").ids.mirnaSelectBox.children):
                if i % 3 == 0:
                    reverseList.append(child.active)

            for i, val in enumerate(reverseList):
                if val:
                    sequences[i] = thsGen.reverse(sequences[i])
                    print("reversing")

            self.ids.mirBaseSubmitButton.disabled = True
            submitDict = dict(zip(names, sequences))  
            thsGen.miRNADict = submitDict
            print(thsGen.miRNADict)
            thsGen.start()
            thsGen.thsPlotSave()
            thsGen.triggerPlotSave()
            thsGen.complexPlotSave()
            self.ids.nextButton2.disabled = False
            ev.dispatch("on_thsGen")
        else:
            print("input something, dingus")

class loadScreen(Screen):
    pass

    
class ToeholdSwitchGenerator(App):

    def build(self):
        
        Window.clearcolor = (10/225.0, 22/255.0, 40/255.0, 1)
        sm = ScreenManager()
        sm.add_widget(mainWindow())
        sm.add_widget(thsWindow())
        sm.add_widget(triggerWindow())
        sm.add_widget(complexWindow())
        sm.add_widget(mirBaseWindow())
        sm.add_widget(strucShowScreen())
        sm.add_widget(fileManager())
        sm.add_widget(loadScreen())

        return sm


if __name__ == '__main__':
    ToeholdSwitchGenerator().run()