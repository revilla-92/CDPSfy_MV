#!/usr/bin/python
# -*- coding: latin-1 -*-

#################################### PRACTICA 7 ######################################
######################### Autores: Raquel Noblejas Sampedro  #########################
#########################          Daniel Revilla Twose      #########################
######################################################################################

# Importamos las bibliotecas que vamos a usar.
import sys
import os

print("-----------------------------------------------------------------------")
print("------------------------- Empieza el script ---------------------------")

# Eliminamos si existe el directorio de trabajo para volver a importar los ficheros.
if (os.path.isdir("cdps")):
        os.system("rm -rf cdps")


# Creamos el directorio de trabajo.
os.system("mkdir cdps")
os.chdir("cdps")
os.system("wget http://idefix.dit.upm.es/download/cdps/p7/p7.tgz")
os.system("tar xfvz p7.tgz")
os.chdir("p7")
os.system("rm -rf p7.xml")
os.system("wget https://raw.githubusercontent.com/revilla-92/CDPSfy_MV/master/p7.xml")


print("-----------------------------------------------------------------------")
print("---------------------- Empieza la configuracion -----------------------")

# Como trabajamos en maquina virtual
os.system("./bin/prepare-p7-vm")

# Destruimos el escenario anterior si lo hubiese y creamos el nuevo
os.system("vnx -f p7.xml -v --destroy")
os.system("vnx -f p7.xml -v --create")


print("-----------------------------------------------------------------------")
print("------------------------- Configurando NAS ----------------------------")

os.system("lxc-attach -n nas1 -- gluster peer probe 10.1.3.22")
os.system("lxc-attach -n nas1 -- gluster peer probe 10.1.3.23")
os.system("lxc-attach -n nas1 -- gluster volume create nas replica 3 10.1.3.21:/nas 10.1.3.22:/nas 10.1.3.23:/nas force")
os.system("lxc-attach -n nas1 -- gluster volume start nas")


print("-----------------------------------------------------------------------")
print("---------------------- Configurando Servidores ------------------------")

for n in range(1, 5):
        comando = "lxc-attach -n s"+str(n)+" -- mkdir /mnt/nas"
        os.system(comando)

        if(n == 4):
                comando1 = "lxc-attach -n s"+str(n)+" -- mount -t glusterfs 10.1.3."+str(n+19)+":/nas /mnt/nas"
                os.system(comando1)
        else:
                comando1 = "lxc-attach -n s"+str(n)+" -- mount -t glusterfs 10.1.3."+str(n+20)+":/nas /mnt/nas"
                os.system(comando1)


print("-----------------------------------------------------------------------")
print("------------------------ Configurando Nagios --------------------------")

# Por si acaso hago un update e instalo sshpass por si tengo que luego conectarme a esa terminal.
os.system("sudo apt-get update")
os.system("sudo apt-get install sshpass")
os.system("sudo apt-get install nano")

# Configuro la terminal nagios para la monitorizacion.
os.system("lxc-attach -n nagios -- apt-get update")
os.system("lxc-attach -n nagios -- apt-get install nano")
os.system("lxc-attach -n nagios -- apt-get install apache2 -y")
os.system("lxc-attach -n nagios -- apt-get install nagios3 -y")
os.system("lxc-attach -n nagios -- service apache2 restart")

# Ahora cargamos los ficheros de configuracion para los servidores.
for n in range (1, 5):
	os.system("lxc-attach -n nagios -- wget https://raw.githubusercontent.com/revilla-92/CDPSfy_MV/master/s"+str(n)+"_nagios2.cfg -P /etc/nagios3/conf.d")

# Remplazamos el fichero de hostgroups
os.system("lxc-attach -n nagios -- rm -rf /etc/nagios3/conf.d/hostgroups_nagios2.cfg")
os.system("lxc-attach -n nagios -- wget https://raw.githubusercontent.com/revilla-92/CDPSfy_MV/master/hostgroups_nagios2.cfg -P /etc/nagios3/conf.d")

# Reiniciamos nagios3 y apache2
os.system("lxc-attach -n nagios -- service nagios3 restart")
os.system("lxc-attach -n nagios -- service apache2 restart")


print("-----------------------------------------------------------------------")
print("----------------- Configuracion de Server Y Tracks --------------------")

# Configuramos el fichero hosts para que redirija las direccionas web.
os.system("rm -rf /etc/hosts")
os.system("wget https://raw.githubusercontent.com/revilla-92/CDPSfy_MV/master/hosts -P /etc")

for n in range (1, 5):
        os.system("lxc-attach -n s"+str(n)+" apt-get update")
        os.system("lxc-attach -n s"+str(n)+" apt-get install software-properties-common")
        os.system("lxc-attach -n s"+str(n)+" apt-get install git")
        os.system("lxc-attach -n s"+str(n)+" apt-get install make g++")
        os.system("lxc-attach -n s"+str(n)+" apt-get install python-software-properties")
        os.system("lxc-attach -n s"+str(n)+" add-apt-repository ppa:chris-lea/node.js")
        os.system("lxc-attach -n s"+str(n)+" apt-get update")
        os.system("lxc-attach -n s"+str(n)+" apt-get install nodejs")

for i in range (1, 4):
        os.system("lxc-attach -n s"+str(i)+" git clone https://github.com/revilla-92/CDPSfy_Tracks")
        os.system("lxc-attach -n s"+str(i)+" -- sh -c 'cd /CDPSfy_Tracks/ && npm install'")

os.system("lxc-attach -n s4 git clone https://github.com/revilla-92/CDPSfy_Server")
os.system("lxc-attach -n s4 -- sh -c 'cd /CDPSfy_Server/ && npm install'")

# Redirecciona cuando llamamos a tracks al contenido del directorio.
os.system("lxc-attach -n s1 -- sh -c 'cd /var/www/html && ln -s /mnt/nas'")       

# Arrancamos el servidor en s4.
# os.system("lxc-attach -n s4 -- sh -c 'cd /CDPSfy/ && npm start'")

print("-----------------------------------------------------------------------")
print("------------------- Configurando y Arrancando LB ----------------------")

# Esto dejará la terminal inutilizada, no detener el proceso o se saldrá del escenario --> Hacerlo en un xterm
# os.system("lxc-attach -n lb 'xr --verbose --server tcp:0:80 --backend 10.1.2.11:3030 --backend 10.1.2.12:3030 --backend 10.1.2.13:3030 --web-interface 0:8001'")



