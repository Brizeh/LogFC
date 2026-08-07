# LogFC-Testing

## Setup

These two files hold your own data and are not tracked by git. Create them
from the provided templates:

```
copy src\input_logs.example.txt   src\input_logs.txt
copy src\custom_names.example.json src\custom_names.json
```

## How to ? :
###  - Put all links in "src/input_logs.txt"
###  - Run.bat

## You can add custom names :
### - associate anet_accounts with some nicknames in src/custom_names.json

Two formats are supported, see src/custom_names.example.json :

```json
{
    "anetaccount.4444": "custom_name_on_output",
    "bladeswornIsNotDead.1234": {
        "nickname": "ImNotOnCopium",
        "discord": "<@123456789012345678>"
    }
}
```
