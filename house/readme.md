# 共有产权房自动化消息通知

file tree

```bash
.
├── house_info.py
└── house.json
```

config file: `house.json`

```json
{
    "Cookie": "xxxxxx",
    "CHATBOT_URL": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YourKeys"
}
```

run python script in Linux by crontab

```bash
# 12:11:00 run program
crontab -e
11 12 * * *  /home/xxx/envs-py/jupy/bin/python /home/xxx/python-examples/house/house_info.py
crontab -l
```
