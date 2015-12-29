#!/usr/bin/python
# -*- coding: latin-1 -*-
 
#################################### PRACTICA 7 ######################################
######################### Autores: Raquel Noblejas Sampedro  #########################
#########################          Daniel Revilla Twose      #########################
######################################################################################

# Importamos las bibliotecas que vamos a usar.
from subprocess import call
from lxml import etree
import shutil
import sys
import os

print("-----------------------------------------------------------------------")
print("------------------------- Empieza el script ---------------------------")

# Comprobamos si esta creado el directorio de trabajo "p3" y sino lo creamos.
if (not os.path.isdir("cdps")):

	# Creamos el directorio de trabajo.
	os.system("mkdir cdps")
	os.system("cd cdps")
	os.system("wget http://idefix.dit.upm.es/download/cdps/p7/p7.tgz")
	os.system("tar xfvz p7.tgz")
	os.system("cd p7")


		


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
		os.system(comando)
	else:
		comando1 = "lxc-attach -n s"+str(n)+" -- mount -t glusterfs 10.1.3."+str(n+20)+":/nas /mnt/nas"
		os.system(comando)


print("-----------------------------------------------------------------------")
print("------------------------ Configurando Nagios --------------------------")

# Por si acaso hago un update e instalo sshpass por si tengo que luego conectarme a esa terminal.
os.system("apt-get update")
os.system("apt-get install sshpass")
os.system("apt-get install nano")

# Configuro la terminal nagios para la monitorizacion.
os.system("lxc-attach -n nagios -- apt-get update")
os.system("lxc-attach -n nagios -- apt-get install nano")
os.system("lxc-attach -n nagios -- apt-get install apache2 -y")



# os.system("sshpass -p 'xxxx' ssh -o StrictHostKeyChecking=no root@nagios")



print("-----------------------------------------------------------------------")
print("------------------- Configurando y Arrancando LB ----------------------")
# Esto dejará la terminal inutilizada, no detener el proceso o se saldrá del escenario



