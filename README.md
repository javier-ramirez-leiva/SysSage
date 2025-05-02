# SysSage
A lightweight Slack bot that monitors system resources and disk usage, sending alerts with detailed system health reports.

The bot is designed to be easy to set up and use, retrieving only the necessary information from the system.

## Installation
In order to install the bot, you will need to have Python 3.6 or higher installed on your system.
1. Clone the repository:
```
git clone https://github.com/javier-ramirez-leiva/SysSage.git
```
2. Install the required dependencies:
```
pip install -r requirements.txt
```
## Create slack app
1. Create a New Slack App
 - Go to: https://api.slack.com/apps
 - Click “Create New App”
 - Choose:
 - From scratch
 - Give it a name (e.g., SysSage)
 - Pick your Slack workspace
 - Click Create App

2. Enable Socket Mode
 - Go to “Socket Mode” in the left menu
 - Enable it
 - Create an App Token (needed for SLACK_APP_TOKEN)
 - Give it a name (e.g., SysSage App Token)
 - Select the connections:write scope
 - Save and copy the token (starts with xapp-...): **slack_app_token**

3. Set Up Bot Token Scopes
 - Go to “OAuth & Permissions”
 - Under Bot Token Scopes, add:
 - app_mentions:read (to react to !status)
 - chat:write (to send messages)
 - channels:join (optional) if you want the bot to auto-join
 - Save changes

4. Install the App to Your Workspace
 - Click the Install App button in the sidebar
 - Authorize it
 - You’ll receive the Bot User OAuth Token (starts with xoxb-...): **slack_bot_token**


## Configuration
In order to configure the bot, you will need to create a `configuration.json` file in the root directory of the project.
### Mandatory fields
- `slack_bot_token`: The Slack bot token.
- `slack_app_token`: The Slack app token.
- `status_keyword`: The keyword that the bot will listen for to trigger the status check.
- `system_name`: The name of the system that the bot will monitor.

If any of the fields are missing, the bot will not be able to run.
### Disk filter [optional]
If you want to monitor only a specific disk, you can add the following fields to the configuration file. If no disk is specified, the bot will monitor all disks.
- `disks`: A list of disks to monitor.
### Alerts [optional]
If you want to receive alerts when the system is not healthy, you can add the following fields to the configuration file.
- `channel_id`: The ID of the channel where the bot will send the alerts.
- `timeout`: The time in minutes that the bot will wait for the system to be healthy before sending an alert.
- `return_status_on_alert`: If true, the bot will return the status of the system when an alert is triggered. If false, the bot will not return the status of the system when an alert is triggered.
- `disk_thresholds`: A dictionary of disk names and their corresponding thresholds. If the disk usage exceeds the threshold, the bot will send an alert.

### Example
```json
{
    "slack_bot_token": " xoxb-...",
    "slack_app_token": "xapp-...",
    "status_keyword": "!status",
    "system_name": "My system",
    "disk": [
        "/",
        "/media/disk1"
    ],
    "alerts": {
        "timeout": 60,
        "channel_id": "C...",
        "return_status_on_alert": true,
        "disk_thresholds": {
            "/": 85,
             "/media/disk1": 60
        }
    }
}
```

## Usage
In order to launch the bot, you will need to run the following command:
```
python3 slackbot.py
```
To use the bot, simply send a message to the Slack channel where the bot is invited with the keyword specified in the configuration file. The bot will then check the system health and send a message with the status of the system.
