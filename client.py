import dpkt
import socket, random, time
from scapy.all import *
from multiprocessing import *

health = 100 #Sets the health of the player
mana = 100   #Sets the mana of the player
potions = 3  #Sets the starting amount for the potions
elixer = 3

def move(action): #This functions uses the action variable to define what 
    global health #Calls upon the global variable health 
    global mana #Calls upon the global variable mana
    global potions #Calls upon the global variable potions
    global elixer
    #Creates the ICMP Packet to send
    echo = dpkt.icmp.ICMP.Echo() 
    echo.id = random.randint(0, 0xffff)
    echo.seq = random.randint(0, 0xffff)
    icmp = dpkt.icmp.ICMP()
    icmp.type = dpkt.icmp.ICMP_ECHO
    icmp.data = echo 
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, dpkt.ip.IP_PROTO_ICMP)
    s.connect(('172.16.12.128', 1)) #Specifies the IP Address to which the ICMP packet is sent
    i = random.randint(0,10) #randomized number is generated to determine whether the attack/fireball will do extra damage (critical) 
    action = action.lower() #Forces all incomming characters to be lower case

    if (action == 'attack'):
        if (i <= 7):
            echo.data = 'Attack' #Player does a regular attack
            sent = s.send(str(icmp))
        else:
            echo.data = 'Attack-Crit' #Player gets a crit with te regular attack
            sent = s.send(str(icmp))
    elif (action == 'defend'):
        echo.data = 'Defend' #Player is defending
        sent = s.send(str(icmp))
    elif (action == 'f-ball' or action == 'fireball'):
        if (i <= 7):
            if mana <= 0:
                print "Your out of mana"
            else:
                echo.data = 'F-Ball' #Player users the fireball
                sent = s.send(str(icmp))
                mana = mana - 25
        else:
            if mana <= 0:
                print "Your out of mana"
            else:
                echo.data = 'F-Ball-Crit' #Player gets a critical with the fireball
                sent = s.send(str(icmp))
                mana = mana - 25
    elif (action == 'potion'): #Adds 50% of health to the player
        health = health + 50
        potions = potions - 1
    elif (action == 'elixer'): #Add 50% back to the players mana reserve
        health = mana + 50
        elixer = elixer - 1
    else:
        print 'That is not a correct value. Try again.' #Is displayed when the user inputs an incorrect move

def captureICMP(pkt): #Capture packets sent from the server
    global health #imports the global health variable
    raw = pkt.sprintf('%Raw.load%')# grabs the data portion of the ICMP packet
    if raw == "'G-Attack'": #Goblin attack incoming
        move = re.findall('G-Attack', raw) 
        health = health - 5
        print move[0]
    elif raw == "'G-Attack-Crit'": #Goblin attack incoming thats critical
        move = re.findall('G-Attack-Crit', raw)
        health = health - 10
        print move[0]
    elif raw == "'G-Defend'": #Goblin is defending
        move = re.findall('G-Defend', raw)
        print move[0]
    elif raw == "'G-F-Ball'": #Goblin fireball incomming
        move = re.findall('G-F-Ball', raw)
        health = health - 10
        print move[0]
    elif raw == "'G-F-Ball-Crit'": #Goblin fireball incomming
        move = re.findall('F-Ball-Crit', raw)
        health = health - 20
        print move[0]

def main():
    print 'Welcome to the Goblin Killing Simulator'
    print '---------------------------------------'
    conf.iface = 'vmnet8' #Tells scapy what interface to monitor
    while (health >= 100):
	print 'Your health is at %d%%, you have %d potions left, you have %d%% mana left, and %d elixers ' % (health,potions,mana,elixer)
	print 'Your moves are: Attack, Defend, Fireball, Potion, Elixer'
        move(str(raw_input('Your move:')))
        sniff(filter='icmp', prn=captureICMP, count = 1) #Used to capture the icmp packets.  The data captured to the packets goes to the captureICMP function.  Also suppose to wait to capture 1 icmp packet after move
    print 'You are dead!'

if __name__ == '__main__':
    main()
