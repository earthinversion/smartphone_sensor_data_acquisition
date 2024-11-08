```bash
sudo yum install git
python3 -m venv venv
source venv/bin/activate
pip install pandas
pip install Flask Flask-SocketIO eventlet
git clone https://github.com/earthinversion/smartphone_sensor_data_acquisition.git
cd smartphone_sensor_data_acquisition

```


## Update Security Group
1. Log in to the AWS Console and go to the EC2 Dashboard.
1. Select Security Groups:
    - In the left sidebar under Network & Security, click on Security Groups.
1. Find the Security Group:
    - Locate the Security Group associated with your EC2 instance. If you're unsure, go to the Instances section, select your instance, and check the Security Group listed in its details.
1. Edit Inbound Rules:
    - Click on the Security Group to open its details.
    - Select the Inbound rules tab, then click Edit inbound rules.
1. Add a New Rule for TCP Port 56204:
    - Click Add rule and configure it as follows:
    ```bash
    Type: Custom TCP
    Protocol: TCP
    Port Range: 56204
    Source: 0.0.0.0/0 (for all IP addresses) or specify a range that includes your phone’s IP address if you want to restrict access.
    ```
1. Save the rule.


## Access the app
- http://54.245.66.246:5000/
