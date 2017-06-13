import sys
import threading
import time
from Tkinter import * 
from collections import deque

queue = deque()		# list recipient qui peut utiliser append et pop plus rapide aux extremites

class Semaphore(object):

    def __init__(self, initial):	#l initialisation de la classe
        self.lock = threading.Condition(threading.Lock())
        self.value = initial

    def up(self): 	#cette function notifie le threads de patienter
        with self.lock:
            self.value += 1
            self.lock.notify()

    def down(self):	#cette function notifie les threads qu ils peuvent s executer
        with self.lock:
            while self.value == 0:
                self.lock.wait()
            self.value -= 1

class ChopStick(object):

    def __init__(self, number):        # le constructeur
        self.number = number           # chop stick ID
        self.user = -1                 # suivre les philosophes s il utilize le chopstick
        self.lock = threading.Condition(threading.Lock())
        self.taken = False

    def take(self, user):         # used for synchronization / pour etre sur que le chopstick n est pas utilise par plusieurs personnes en meme temps
        with self.lock:
            while self.taken == True:
                self.lock.wait()
            self.user = user
            self.taken = True
            queue.appendleft("p[%s] a pris c[%s]\n" % (user, self.number))
            self.lock.notifyAll()
#les messages qui correspondent aux actions sont stockes dans une queue qui est affiche a la fin sur l interface graphique


    def drop(self, user):         # used for synchronization
        with self.lock:
            while self.taken == False:
                self.lock.wait()
            self.user = -1
            self.taken = False
            queue.appendleft("p[%s] a laisse c[%s]\n" % (user, self.number))
            self.lock.notifyAll()
# ces fonctions decident quand on prend ou on laisse les chopsticks, en le bloquant pour les autres personnes


class Philosopher (threading.Thread):

    def __init__(self, number, left, right, butler):  	# le constructeur
        threading.Thread.__init__(self)
        self.number = number            		# philosopher number
        self.left = left
        self.right = right
        self.butler = butler

    def run(self):
        for i in range(20):
            self.butler.down()              # start service by butler
            time.sleep(0.1)                 # think pour eviter le deadlock
            self.left.take(self.number)     # pickup left chopstick
            time.sleep(0.1)                 # (yield makes deadlock more likely)
            self.right.take(self.number)    # pickup right chopstick
            time.sleep(0.1)                 # eat
            self.right.drop(self.number)    # drop right chopstick
            self.left.drop(self.number)     # drop left chopstick
            self.butler.up()                # end service by butler
        print("p[%s] a fini refflechir et manger\n" % self.number)
        p = "p[%s] a fini refflechir et manger\n" % self.number
        queue.appendleft(p)



class Window(Frame):


    def __init__(self, master=None):

        Frame.__init__(self, master)
        master.title("Bianca & Lavinia")
        master.geometry("300x400")
        master.resizable(width=FALSE, height=FALSE)

        self.pack(fill=BOTH, expand=1)

        self.labela = Label(self, text="Actions:")
        self.labela.place(x=25, y=5)

        self.listbox = Listbox(self, width=40,height=10)
        self.listbox.place(x=25, y=25)

        self.labelb = Label(self, text="Numero de philosophes:")
        self.labelb.place(x=25, y=230)

        self.nr = IntVar()
        self.entry1 = Entry(self,textvariable=self.nr)
        self.entry1.place(x=25, y=250)


        self.button = Button(self, text="Ajoutez" ,command=self.main)
        self.button.place(x=25, y=275)

        self.labelc = Label(self, text="Attendre pour la console!")
        self.labelc.place(x=25, y=330)

        self.button1 = Button(self, text="Affichez", command=self.afiseaza)
        self.button1.place(x=25, y=350)



    def main(self):
        # nombre de philosophes / chop sticks

        n = int(self.entry1.get())

        # butler pour eviter le deadlock (n-1 valable)
        butler = Semaphore(n - 1)

        # list de chopsticks
        c = [ChopStick(i) for i in range(n)]

        # list de philsophes
        p = [Philosopher(i, c[i], c[(i + 1) % n], butler) for i in range(n)]

        for i in range(n):
            p[i].start()

    def afiseaza(self):
        for i in range(0, len(queue)):
            z = queue.pop()
            self.listbox.insert(END, z)





if __name__ == "__main__":
    window = Tk()
    frame = Window(window)
    window.mainloop()


