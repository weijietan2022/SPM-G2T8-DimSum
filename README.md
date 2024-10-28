# SPM-G2T8-DimSum
# npm run dev  -  local development
# npm run build - build front end project to static files ,check the "dist" folder

# React Port - 5173
# login.py - 5001
# schedule.py - 5000
# application-form.py - 5002
# notification - 5003


# Link  (http only)

http://139.59.225.156


# cloud server installation
# Project Deployment Guide
System Information
Operating System: Ubuntu 20.04.4 LTS (Focal Fossa)
System Type: Debian-based

Install and Configure Nginx (Nginx is the web server for host web static files)

Step 1: Update and Install Nginx
Update the package index and install Nginx to serve the front-end and proxy requests to the back-end.

sudo apt update
sudo apt install nginx -y

configure the nginx 
/etc/nginx/nginx.conf

Step 2: Start and Configure Nginx
Start Nginx to ensure the web server is running and ready for front-end deployment.

sudo systemctl start nginx

to reload the nginx
sudo systemctl reload nginx

Step 3: Set Up Gunicorn for Back-End Deployment
Gunicorn will be used as the WSGI server to run Python back-end services.

Install Gunicorn
In the server’s Python environment, install Gunicorn:

pip install gunicorn

Step 4. Back-End Deployment
Transfer Back-End Files: Copy all necessary back-end project directories (ViewRequest, schedules, notification, login, autorejection, application-form) to the server directory at /home/project/spm-g2t8-dimsum-backend.

Run Back-End Services: Navigate to the project directory and start the back-end services using the provided run.sh script.

ps aux | grep -E "ViewRequest|schedules|notification|login|autorejection|application-form"

Stop Back-End Services: To terminate the back-end processes, run the kill.sh script.

bash kill.sh


# how to deploy into cloud

server ip address: 139.59.225.156
access: root/spmg2t8Dimsum


Front-End Deployment:
Build the Front-End: Compile the front-end code from the local project, and generate the dist folder containing the optimized production files.
Upload to Cloud Server: Transfer the contents of the dist folder to the cloud server directory at /var/www/html.
Restart Web Server: Reload the Nginx web server to apply the latest front-end changes using the command:systemctl reload nginx

Back-End Deployment:
Copy Project Directories: Transfer the necessary backend project directories (ViewRequest, schedules, notification, login, autorejection, application-form) to the cloud server at /home/project/spm-g2t8-dimsum-backend.
Start the Back-End Services: Execute the backend startup script to initialize the services: 

bash run.sh

Stop the Back-End Services: When needed, execute the backend shutdown script to terminate the services:

kill.sh
