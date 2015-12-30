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
os.system("sudo su -c './bin/prepare-p7-vm'")

# Destruimos el escenario anterior si lo hubiese y creamos el nuevo
os.system("sudo su -c 'vnx -f p7.xml -v --destroy'")
os.system("sudo su -c 'vnx -f p7.xml -v --create'")


print("-----------------------------------------------------------------------")
print("------------------------- Configurando NAS ----------------------------")

os.system("sudo su -c 'lxc-attach -n nas1 -- gluster peer probe 10.1.3.22'")
os.system("sudo su -c 'lxc-attach -n nas1 -- gluster peer probe 10.1.3.23'")
os.system("sudo su -c 'lxc-attach -n nas1 -- gluster volume create nas replica 3 10.1.3.21:/nas 10.1.3.22:/nas 10.1.3.23:/nas force'")
os.system("sudo su -c 'lxc-attach -n nas1 -- gluster volume start nas'")


print("-----------------------------------------------------------------------")
print("---------------------- Configurando Servidores ------------------------")

for n in range(1, 5):
        comando = "sudo su -c 'lxc-attach -n s"+str(n)+" -- mkdir /mnt/nas'"
        os.system(comando)

        if(n == 4):
                comando1 = "sudo su -c 'lxc-attach -n s"+str(n)+" -- mount -t glusterfs 10.1.3."+str(n+19)+":/nas /mnt/nas'"
                os.system(comando)
        else:
                comando1 = "sudo su -c 'lxc-attach -n s"+str(n)+" -- mount -t glusterfs 10.1.3."+str(n+20)+":/nas /mnt/nas'"
                os.system(comando)


print("-----------------------------------------------------------------------")
print("------------------------ Configurando Nagios --------------------------")

# Por si acaso hago un update e instalo sshpass por si tengo que luego conectarme a esa terminal.
os.system("sudo apt-get update")
os.system("sudo apt-get install sshpass")
os.system("sudo apt-get install nano")

# Configuro la terminal nagios para la monitorizacion.
os.system("sudo su -c 'lxc-attach -n nagios -- apt-get update'")
os.system("sudo su -c 'lxc-attach -n nagios -- apt-get install nano'")
os.system("sudo su -c 'lxc-attach -n nagios -- apt-get install apache2 -y'")
os.system("sudo su -c 'lxc-attach -n nagios -- apt-get install nagios3 -y'")
os.system("sudo su -c 'lxc-attach -n nagios -- service apache2 restart'")

# Ahora cargamos los ficheros de configuracion para los servidores.
for n in range (1, 5):
	os.system("sudo su -c 'lxc-attach -n nagios -- wget https://raw.githubusercontent.com/revilla-92/CDPSfy_MV/master/s"+str(n)+"_nagios2.cfg -P /etc/nagios3/conf.d'")

# Remplazamos el fichero de hostgroups
# os.system("sudo su -c 'lxc-attach -n nagios -- wget https://raw.githubusercontent.com/revilla-92/CDPSfy_MV/master/hostgroups_nagios2.cfg -P /etc/nagios3/conf.d'")
# Si hacemos manualmente cambiando el fichero hostgroups y luego reiniciando nagios (service nagsios3 restart) funciona...

# Reiniciamos nagios3 y apache2
os.system("sudo su -c 'lxc-attach -n nagios -- service nagios3 restart'")
os.system("sudo su -c 'lxc-attach -n nagios -- service apache2 restart'")


print("-----------------------------------------------------------------------")
print("------------------- Configurando y Arrancando LB ----------------------")

# Esto dejará la terminal inutilizada, no detener el proceso o se saldrá del escenario


