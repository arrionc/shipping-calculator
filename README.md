# Vingo Calculator App

This simple web app helps to breakdown wine shipping costs using the shipping service called Vingo.
The app will give an error if the wrong state is entered and it requires a value is always entered - 0 if none. 

The project ip: [http://44.200.13.8/](http://44.200.13.8//)

# Requirements 

The web app was created using:

- [Python](https://www.python.org/)
- [Flask](http://flask.pocoo.org/)
- [SqlAlchemy](https://www.sqlalchemy.org/)
- [Amazon Lightsail](https://aws.amazon.com/lightsail)
- [PostgreSQL](https://www.postgresql.org/)
- [Bootstrap4](https://getbootstrap.com/)

## Setting up an Instance in Amazon Lightsail

- Login to Amazon Lightsail
- Click `Create Instance`
- Select Platform `Linux/Unix` 
- Select a blueprint `OS Only`
- Select `Ubuntu 16.04 LTS`
- Choose your instance plan - choose the cheapest one
- Give a name to your instance 
- Create Instance

## Set up the SSH Key
- Download the default private key from your Lightsail Account Page.
- Move this private key file named `LightsailDefaultPrivateKey-*.pem` into the local folder `~/.ssh` and rename it `vingo1_key.rsa`
- In your local terminal run the following command `chmod 600 ~/.ssh/vingo1_key.rsa`
- Connect to the instance via the terminal `ssh -i ~/.ssh/vingo_key.rsa ubuntu@44.200.13.8`
- CHANGING THE KEY TO .rsa DID NOT WORK -->> Leaving the key with the .pem worked
- `~/.ssh` and rename it `vingo_key.pem`
- In your local terminal run the following command `chmod 600 ~/.ssh/vingo_key.pem`
- Connect to the instance via the terminal `ssh -i ~/.ssh/vingo_key.pem ubuntu@44.200.13.8`

## Change SSH port from 22 to 2200
- Edit the sshd_config file by running `sudo nano /etc/ssh/sshd_config`
- Change port from 22 to 2200
- Save the change by Control+X and confirm with Y
- Restart SSH with `sudo service ssh restart` 

## Configure Uncomplicated Firewall (UFW)
- The firewall for Ubuntu needs to only allow incoming connections for SSH(port 2200), HTTP(port 80) and NTP (port 123).
- Run the following commands: 
```
sudo ufw status         # the status should be inactive.
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 2200/tcp # Allow incoming tcp packets on port 2200.
sudo ufw allow www      # Allow HTTP traffic in.
sudo ufw allow 123/udp  # Allow incoming udp packets on port 123.
sudo ufw deny 22        # Deny incoming requests on port 22 sudo ufw enable         #Turn on UFW
sudo ufw enable         # Enables all the changes made
sudo ufw status         #UFW is now active and should list all the allowed ports  
```
- Exit the SSH connection, type `exit`
- Go to the AWS Lightsail instance and in the Networking tab edit the Firewall rules:
```
Application        Protocol      Port range
HTTP                TCP           80
Custom              UDP           123
Custom              TCP           2200
```

- After enabling ufw and opening ports 80, 2200 and 123 run:
`ssh -i ~/.ssh/vingo_key.pem -p 2200 ubuntu@44.200.13.8`


## Create user grader and give sudo access 
- Create user run `sudo adduser grader`
- Create a new directory in sudoer directory run `sudo nano /etc/sudoers.d/grader`
- Add `grader ALL=(ALL:ALL) ALL` in nano editor
- Save and exit using CTRL+X and confirm with Y 
- Verify the grader has sudo permissions. Run `su -grader` and then `sudo -l` 
- The grader should have ALL permissions.

## Create SSH key pair for grader (NOT NEEDED UNLESS ANOTHER PERSON NEEDS ACCESS)
 - In your local terminal run `ssh-keygen`
 - Copy the generated ssh file with extension .pub
 - Login to the virtual machine as the grader `su - grader `
 - Create directory `mkdir .ssh`
 - Create file `touch .ssh/authorized_keys`
 - Run `sudo nano ~/.ssh/authorized_keys` and paste the contents from the .pub file into this file.
 - Save and exit 
 - Give permissions `chmod 700 .ssh` and `chmod 644 .ssh/authorized_keys`
 - Check `/etc/ssh/sshd_config` file make sure `PasswordAuthentication`is set to no
 - Restart `sudo service ssh restart`
 - Check `sudo nano /etc/ssh/sshd_config` find `PermitRootLogin` and change it to `no`
- On the local machine run `ssh grader@3.93.39.142 -p 2200 -i ~/.ssh/linuxProject`

## Update Ubuntu
- Run `sudo apt update` and `sudo apt upgrade`

## Update all packages

- Run `sudo apt-get update` and `sudo apt-get upgrade`

## Ubuntu restart
- Run `sudo reboot` — this takes a couple of minutes until it reboots there will be no access

## Set up Local Time Zone 
- While logged in as grader, configure the time zone: `sudo dpkg-reconfigure tzdata`

## Install Apache and wsgi module to create the server
- Run `sudo apt-get install apache2` to install apache
- Run `sudo apt-get install python-setuptools libapache2-mod-wsgi-py3` to install mod-wsgi module
- Start the server `sudo service apache2 start`
- Enable `mod-wsgi` run `sudo a2enmod wsgi`

## Install Git and clone the vingo project
- Run `sudo apt-get install git`
- Configure your username and email run `git config --global user.name yourusername` and `git config --global user.email youremail`
- Clone the project run `cd /var/www and sudo mkdir vingo`
- Change the owner to grader `sudo chown -R grader:grader vingo`
- Run `set sudo chmod +x vingo` to give a permission to clone the project.
- Switch to the vingo directory and clone the Vingo project.
- `cd vingo` and `git clone https://github.com/arrionc/vingoApp.git`
- Create vingo.wsgi file.
- Run `sudo nano vingo.wsgi` and add the following code:
```
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/vingo/vingoApp/")
sys.path.insert(1, "/var/www/vingo/")

from vingoApp import app as application
application.secret_key = '...'
```

## Install and configure PostgreSQL
- While logged in as grader, install PostgreSQL: `sudo apt-get install postgresql`

- Check PostgreSQL does not allow remote connections. In the `/etc/postgresql/9.5/main/pg_hba.conf` file
- Switch to the postgres user: `sudo su - postgres`
- Open PostgreSQL interactive terminal with psql.
- Create the catalog user with a password and give them the ability to create databases run the following commands:
```
postgres=# CREATE ROLE vingo WITH LOGIN PASSWORD 'yourpassword';
postgres=# ALTER ROLE vingo CREATEDB;
```
- You can check the created role by running `\du` and the catalog role should be listed with an attribute to `Create DB`
- Exit psql: `\q`

- Switch back to the grader user type `exit` in the terminal
- Create a new Linux user called catalog: `sudo adduser vingo`
- Enter password and fill out information.
- Give to vingo user the permission to sudo. Run: `sudo visudo`
- Search for the lines that looks like this:
```
root    ALL=(ALL:ALL) ALL
grader  ALL=(ALL:ALL) ALL
```
- Give catalog sudo permission by adding it to the file
```
vingo  ALL=(ALL:ALL) ALL
```
- Save and exit using CTRL+X and confirm with Y.
- Change user to vingo `su - vingo`
- While logged in as vingo, create a database: `createdb vingo`
- Run `psql` and then run `\l` to see that the new database has been created. 
- Exit psql: `\q`
- Switch back to the grader user type `exit` on your terminal

## Install virtual environment and Flask framework
- Select grader user `su - grader`
- Inside the folder /var/www/vingo/vingoApp
- Install pip, `sudo apt-get install python3-pip`
- Run `sudo apt-get install python-virtualenv` to install virtual environment
- Create a new virtual environment with `sudo virtualenv -p python3 venv3`
- Change the ownership to grader with: `sudo chown -R grader:grader venv3/`
- Activate the environment `. venv3/bin/activate`
- Install all needed dependencies:
```
pip3 install flask
pip3 instal sqlalchemy
pip3 install --upgrade oauth2client
pip3 install httplib2
pip3 install requests
sudo apt-get install libpq-dev
pip3 install psycopg2
``` 
- Deactivate virtual environment type `deactivate` in the terminal.

## Configure Apache
- Create a config file `sudo nano /etc/apache2/sites-available/vingo.conf`
- Add the following lines:
```
WSGIPythonHome "/var/www/vingo/vingoApp/venv3/bin/python3"
WSGIPythonPath "/var/www/vingo/vingoApp/venv3/lib/python3.5/site-packages"

<VirtualHost *:80>
    ServerName Ubuntu-1
    ServerAlias 44.200.13.8
    WSGIScriptAlias / /var/www/vingo/vingo.wsgi
    <Directory /var/www/vingo/vingoApp/>
        Order allow,deny
        Allow from all
    </Directory>
    Alias /static /var/www/vingo/vingoApp/static
    <Directory /var/www/vingo/vingoApp/static/>
        Order allow,deny
        Allow from all
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/error.log
    LogLevel warn
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```
- Disable Apache site `sudo a2dissite 000-default.conf`
- Reload Apache `sudo service apache2 reload`
- Enable virtual host `sudo a2ensite vingo`
- Reload Apache `sudo service apache2 reload`

## Modify filenames to deploy on AWS.

- Rename `application.py` file to `__init__.py` by running `mv application.py __init__.py`
- In `__init__.py`, replace:
```
# app.run(host="0.0.0.0", port=8000, debug=True)
app.run()
```
- In the `database_setup.py` file, the `__init__.py` file, the `prices_database.py`, the `states_database.py` and `update_database.py` file replace:
```
# engine = create_engine("sqlite:///vingo.db")
engine = create_engine('postgresql://vingo:yourpassword@localhost/vingo')
```
- In the `/var/vingo/vingoApp directory`, activate the virtual environment `. venv3/bin/activate`
- Create the database `python3 database_setup.py`
- Populate the database `python3 prices_database.py`, `python3 states_database.py` and `python3 update_database.py`
- Deactivate the virtual environment `deactivate`
- Restart Apache `sudo service apache2 reload`
- Open browser to `44.200.13.8`
- Application should be app and running 
- A useful command to catch errors in apache `sudo tail /var/log/apache2/error.log`
- Run `sudo service apache2 restart`


## References 
- [Stack Overflow](https://stackoverflow.com/)
- [How to Create a Server on Amazon Lightsail](https://serverpilot.io/docs/how-to-create-a-server-on-amazon-lightsail
)
- [xip.io](http://xip.io/)
- GitHub Repositories
    - https://github.com/boisalai/udacity-linux-server-configuration
    - https://github.com/adityamehra/udacity-linux-server-configuration
    - https://github.com/aaayumi/linux-server-configuration-udacity
