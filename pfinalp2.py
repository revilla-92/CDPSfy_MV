#!/usr/bin/python
# -*- coding: latin-1 -*-

#################################### PRACTICA 7 ######################################
######################### Autores: Raquel Noblejas Sampedro  #########################
#########################          Daniel Revilla Twose      #########################
######################################################################################

# Importamos las bibliotecas que vamos a usar.
import time
import sys
import os


print("-----------------------------------------------------------------------")
print("------------------------- Empieza el script ---------------------------")

# Guardamos el instante inicial de ejecucion del script para saber el tiempo de ejecucion al final:
start_time = time.time()

# Por defecto no arrancamos la monitorizacion de Nagios.
nagios = False

# Si añadimos en la ejecucion del comando "python pfinalp2.py -nagios" se activara nagios.
# Damos la opcion de seleccionar o no Nagios ya que la instalacion de Nagios detendra la ejecucion del script.
if (len(sys.argv) == 2):
        opcion = sys.argv[1]
        print "La opcion seleccionada ha sido: " + opcion
        if (opcion == "-nagios"):
                nagios = True
        else:
                sys.exit("Si desea arrancar Nagios debe utilizar -nagios")
else:
        print "No ha seleccionado ninguna opcion. Si desea activar nagios ponga -nagios. Por defecto no se arrancara Nagios."

# Paramos la ejecucion del Script 5 segundos para que de tiempo a leer los mensajes de ayuda.
time.sleep(5)

# Actualizamos el anfitrion e instalamos nano para poder editar ficheros.
os.system("sudo apt-get update")
os.system("sudo apt-get install nano")


print("-----------------------------------------------------------------------")
print("-------------------- Creando escenario de trabajo ---------------------")

# Eliminamos si existe el directorio de trabajo para volver a importar los ficheros.
if (os.path.isdir("CDPS")):
        os.system("rm -rf CDPS")


# Creamos el directorio de trabajo.
os.system("mkdir CDPS")
os.chdir("CDPS")
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

# Solo si se ha activado la opcion de Nagios configuramos nagios.
if (nagios):
        
        # Configuro la terminal nagios para la monitorizacion.
        os.system("lxc-attach -n nagios -- apt-get update")
        os.system("lxc-attach -n nagios -- apt-get install nano")
        os.system("lxc-attach -n nagios -- apt-get install apache2 -y")
        os.system("lxc-attach -n nagios -- apt-get install nagios3 -y")
        os.system("lxc-attach -n nagios -- service apache2 restart")

        # Ahora cargamos los ficheros de configuracion para los servidores.
        for n in range (1, 5):
        	os.system("lxc-attach -n nagios -- wget https://raw.githubusercontent.com/revilla-92/CDPSfy_MV/master/Nagios/s"+str(n)+"_nagios2.cfg -P /etc/nagios3/conf.d")

        # Remplazamos el fichero de hostgroups
        os.system("lxc-attach -n nagios -- rm -rf /etc/nagios3/conf.d/hostgroups_nagios2.cfg")
        os.system("lxc-attach -n nagios -- wget https://raw.githubusercontent.com/revilla-92/CDPSfy_MV/master/Nagios/hostgroups_nagios2.cfg -P /etc/nagios3/conf.d")

        # Reiniciamos nagios3 y apache2
        os.system("lxc-attach -n nagios -- service nagios3 restart")
        os.system("lxc-attach -n nagios -- service apache2 restart")


print("-----------------------------------------------------------------------")
print("----------------- Configuracion de Server Y Tracks --------------------")

# Configuramos el fichero hosts para que redirija las direccionas web.
os.system("rm -rf /etc/hosts")
os.system("wget https://raw.githubusercontent.com/revilla-92/CDPSfy_MV/master/Hosts_MV/Anfitrion/hosts -P /etc")

# Configuramos el fichero hosts de s4 para que redirija correctamente las direcciones web.
os.system("lxc-attach -n s4 -- rm -rf /etc/hosts")
os.system("lxc-attach -n s4 -- wget https://raw.githubusercontent.com/revilla-92/CDPSfy_MV/master/Hosts_MV/s4/hosts -P /etc")

# Instalamos node en todos los servidores descargando y ejecutando un script aparte desde cada servidor.
for n in range (1, 5):
        os.system("lxc-attach -n s"+str(n)+" -- wget https://raw.githubusercontent.com/revilla-92/CDPSfy_MV/master/pfinalp2_node.py")
        os.system("lxc-attach -n s"+str(n)+" -- python pfinalp2_node.py")
        os.system("lxc-attach -n s"+str(n)+" -- apt-get install nano")

# Clonamos y arrancamos la aplicacion Tracks en los servidores.
for i in range (1, 4):
        os.system("lxc-attach -n s"+str(i)+" -- git clone https://github.com/revilla-92/CDPSfy_Tracks")
        comando2 = "'cd /CDPSfy_Tracks/ && node app.js'"
        os.system('xterm -hold -e "lxc-attach -n s'+str(i)+' -- sh -c '+comando2+'" &')

# Clonamos y arrancamos la aplicacion Server en el servidor. Asi mismo creamos /data/db para la mejora de MongoDB.
os.system("lxc-attach -n s4 -- git clone https://github.com/revilla-92/CDPSfy_Server")
os.system("lxc-attach -n s4 -- mkdir -p /data/db")
os.system("lxc-attach -n s4 -- chmod +rwx /data/db")

# Deberemos meter en s4 este comando para arrancar la BBDD.
# os.system("lxc-attach -n s4 -- mongod > /dev/null 2>&1 &")

# Este comando lo hacemos para ejecutar el comando npm start en una nueva terminal:
# El comando completo seria: xterm -hold -e "lxc-attach -n s4 -- sh -c 'cd /CDPSfy_Server/ && npm start'" &
# comando3 = "'cd /CDPSfy_Server/ && npm start'"
# os.system('xterm -hold -e "lxc-attach -n s4 -- sh -c '+comando3+'" &')

# Redirecciona cuando llamamos a tracks al contenido del directorio.
os.system("lxc-attach -n s1 -- sh -c 'cd /var/www/html && ln -s /mnt/nas'")       


print("-----------------------------------------------------------------------")
print("------------------- Configurando y Arrancando LB ----------------------")

# Arrancamos el baleanceador de carga en una terminal aparte balanceado a s1, s2 y s3 por el puerto 3030 que es donde hemos puesto a escuchar tracks.cdpsfy.es.
os.system("xterm -hold -e 'lxc-attach -n lb -- xr --verbose --server tcp:0:80 --backend 10.1.2.11:3030 --backend 10.1.2.12:3030 --backend 10.1.2.13:3030 --web-interface 0:8001' &")


# Imprimimos el tiempo que ha tardado en ejecutarse el script total:
print("------------------------ %s seconds ------------------------" % (time.time() - start_time))

print("-----------------------------------------------------------------------")
print("------------------------- Script Finalizado ---------------------------")

