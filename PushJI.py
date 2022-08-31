import json, os, yaml, requests, tempfile, wget
from flask import Flask, request

app = Flask(__name__)

# 读取配置文件
with open('./config.yaml', 'r', encoding='utf-8') as cfgFile:
    cfg = yaml.load(cfgFile.read(), Loader=yaml.Loader)

# 配置环境变量
SEND_KEY = cfg.get('SEND_KEY')
SEND_TO_ID = cfg.get('SEND_TO_ID')
AGENT_ID = cfg.get('AGENT_ID')
CORP_ID = cfg.get('CORP_ID')
CORP_SECRET = cfg.get('CORP_SECRET')

# 企业微信API
qyapi_url = "https://qyapi.weixin.qq.com/cgi-bin/"


# 获取 Access Token
def get_access_token():
    get_access_token_url = f'{qyapi_url}gettoken?corpid={CORP_ID}&corpsecret={CORP_SECRET}'
    return json.loads(requests.get(get_access_token_url).content)['access_token']


# 存储 access_token
access_token = get_access_token()

# 信息推送API
message_push_url = f"{qyapi_url}message/send?access_token={access_token}"


# 图片/语音/文件 等仅需 media_id 的信息推送
def message_push(pushType, media_id):
    data = {
        "touser": SEND_TO_ID,
        "agentid": AGENT_ID,
        "msgtype": pushType,
        pushType: {
            "media_id": media_id
        },
        "duplicate_check_interval": 600
    }
    response = requests.post(url=message_push_url, data=json.dumps(data)).content
    return response


# 获取 media_id
def get_media_id(url, fileType):
    tmpDir = str(tempfile.mkdtemp())
    fileName = wget.filename_from_url(url)
    wget.download(url, out=tmpDir)
    # 媒体上传API
    media_upload_url = f"{qyapi_url}media/upload?access_token={access_token}&type={fileType}"
    media = {"media": open(tmpDir + "\\" + fileName, "rb")}
    response = requests.post(url=media_upload_url, files=media).content
    media_id = json.loads(response)['media_id']
    return media_id


# TODO 文档
@app.route('/')
def index():
    return open("./index.html", 'r', encoding='utf-8')


# 文本消息
@app.route('/text', methods=['POST', 'GET'])
def text_push():
    if request.args.get('sendkey') == SEND_KEY:
        text = request.args.get('text')
        data = {
            "touser": SEND_TO_ID,
            "agentid": AGENT_ID,
            "msgtype": "text",
            "text": {
                "content": text
            },
            "duplicate_check_interval": 600
        }
        response = requests.post(url=message_push_url, data=json.dumps(data)).content
        return response
    else:
        return Falsea


# 图片消息
@app.route('/image', methods=['POST', 'GET'])
def image_push():
    if request.args.get('sendkey') == SEND_KEY:
        picurl = request.args.get('picurl')
        media_id = get_media_id(url=picurl, fileType="image")
        response = message_push(pushType="image", media_id=media_id)
        return response
    else:
        return False


# 语音消息
@app.route('/voice', methods=['POST', 'GET'])
def voice_push():
    if request.args.get('sendkey') == SEND_KEY:
        voiceurl = request.args.get('voiceurl')
        media_id = get_media_id(url=voiceurl, fileType="voice")
        response = message_push(pushType="voice", media_id=media_id)
        return response
    else:
        return False


# 文件消息
@app.route('/file', methods=['POST', 'GET'])
def file_push():
    if request.args.get('sendkey') == SEND_KEY:
        fileurl = request.args.get('fileurl')
        media_id = get_media_id(url=fileurl, fileType="file")
        response = message_push(pushType="file", media_id=media_id)
        return response
    else:
        return False


# 图文消息
@app.route('/news', methods=['POST', 'GET'])
def news_push():
    if request.args.get('sendkey') == SEND_KEY:
        desp, url, picurl = "", "", ""
        title = request.args.get('title')
        try:
            desp = request.args.get('desp')
            url = request.args.get('url')
            picurl = request.args.get('picurl')
        except:
            pass
        data = {
            "touser": SEND_TO_ID,
            "agentid": AGENT_ID,
            "msgtype": "news",
            "news": {
                "articles": [
                    {
                        "title": title,
                        "description": desp,
                        "url": url,
                        "picurl": picurl
                    }
                ]
            },
            "duplicate_check_interval": 600
        }
        response = requests.post(url=message_push_url, data=json.dumps(data)).content
        return response
    else:
        return Falsea


if __name__ == '__main__':
    app.run()
