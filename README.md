## VK to TG
Instantly forwards new posts from the VK group to the Telegram channel.
Uses a Long Poll request, if there is a new post in the group, then it is processed and immediately sent to the telegram channel
## Requirements:
- Python 3.8+
- Telegram bot token
- VK access token
## What can it forward
|VK| Telegram |Notes|
|--|--|--|
|Text|✅|Will be splitted into multpile messages if VK text is too big (> 4096).|
|Photo|✅|Will be posted with the largest size available.|
|File|✅|Will be posted in separate message.|
|Link|✅|Will be shown just as VK link.|
|Article|✅|Will be in the form of link.|
|Poster|✅|Works the same way as with the photo.|
|Graffiti|✅|Works the same way as with the photo.|
|Map|✅|Will be posted in separate message.|

## Example

![demo](src/demo.gif)