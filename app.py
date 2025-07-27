from flask import Flask, request, abort
import requests
import json
import os

app = Flask(__name__)

# LINE APIの設定
LINE_CHANNEL_ACCESS_TOKEN = 'HebQLBzo3AsxAhlXnCNQPOMGs6f29b4dg/wDooDO1wPLrFAOaFwhEccvv/f1oE+5IhW0G+Lt3bYAu4DUjUKP8HPKubZzw1IkAPHhZI8UneNTUaBasRpWN1L/kYVp6xwS9TzfMoN3/PxO9e+yWxk/2AdB04t89/1O/w1cDnyilFU='

# Webhookを受け取るエンドポイント
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    print(f"受信したデータ: {body}")
    
    try:
        events = json.loads(body)['events']
        
        for event in events:
            if event['type'] == 'message':
                user_id = event['source']['userId']
                
                # テキストメッセージの処理
                if event['message']['type'] == 'text':
                    message_text = event['message']['text']
                    print(f"受信メッセージ: {message_text}")
                    
                    if message_text == '【処方箋送信】':
                        print("処方箋送信コマンドを受信")
                        send_camera_action(user_id)
                    elif message_text == '【服薬指導】':
                        print("服薬指導コマンドを受信")
                        send_flex_message(user_id)
                    elif message_text == '【アクセス】':
                        print("アクセス情報コマンドを受信")
                        send_access_info(user_id)
                
                # 🔹【追加】画像メッセージの処理
                elif event['message']['type'] == 'image':
                    print("処方箋画像を受信")
                    send_prescription_received_message(user_id)
                    
        return 'OK'
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        abort(400)

# 🔹【新規追加】処方箋画像受信時の自動返信メッセージ
def send_prescription_received_message(user_id):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
    }

    data = {
        'to': user_id,
        'messages': [{
            'type': 'text',
            'text': '📮処方箋画像の送信ありがとうございます！\n\n画像メッセージが既読になりましたら受付完了となっておりますので、お気をつけてお越しください😊\n\n受け取りが後日や時間をずらす場合は、ひと言ご連絡いただけると助かります✨'
        }]
    }

    try:
        response = requests.post(
            'https://api.line.me/v2/bot/message/push',
            headers=headers,
            data=json.dumps(data)
        )
        print(f"処方箋受信メッセージ送信レスポンス: {response.status_code}")
        
        if response.status_code != 200:
            print(f"送信エラー: {response.status_code}")
            print(f"エラー詳細: {response.text}")
            
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

def send_camera_action(user_id):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
    }

    data = {
        'to': user_id,
        'messages': [{
            'type': 'text',
            'text': '処方箋を撮影してください',
            'quickReply': {
                'items': [{
                    'type': 'action',
                    'action': {
                        'type': 'camera',
                        'label': 'カメラを起動'
                    }
                }]
            }
        }]
    }

    try:
        response = requests.post(
            'https://api.line.me/v2/bot/message/push',
            headers=headers,
            data=json.dumps(data)
        )
        print(f"カメラアクション送信レスポンス: {response.status_code}")
        
        if response.status_code != 200:
            print(f"送信エラー: {response.status_code}")
            print(f"エラー詳細: {response.text}")
            
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

def send_flex_message(user_id):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
    }

    flex_message = {
        "type": "flex",
        "altText": "ご相談方法の選択",
        "contents": {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": "https://tokyo-online-clinic.info/wp-content/themes/toclp/img/linehifuka/asahi01.png",
                "size": "full",
                "aspectRatio": "20:20",
                "aspectMode": "cover",
                "action": {
                    "type": "uri",
                    "uri": "https://line.me/"
                }
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "ご相談方法をお選びください",
                        "weight": "bold",
                        "size": "lg"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "message",
                            "label": "電話での相談",
                            "text": "電話での相談"
                        }
                    },
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "message",
                            "label": "LINEでの相談",
                            "text": "LINEでの相談"
                        }
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [],
                        "margin": "sm"
                    }
                ],
                "flex": 0
            }
        }
    }

    data = {
        'to': user_id,
        'messages': [flex_message]
    }

    try:
        response = requests.post(
            'https://api.line.me/v2/bot/message/push',
            headers=headers,
            data=json.dumps(data)
        )
        print(f"Flexメッセージ送信レスポンス: {response.status_code}")
        
        if response.status_code != 200:
            print(f"送信エラー: {response.status_code}")
            print(f"エラー詳細: {response.text}")
            
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

# 🔹【修正】アクセス情報を準備中に変更
def send_access_info(user_id):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
    }

    flex_message = {
        "type": "flex",
        "altText": "アクセス情報",
        "contents": {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "アクセス情報",
                        "weight": "bold",
                        "size": "lg",
                        "align": "center"
                    },
                    {
                        "type": "spacer",
                        "size": "md"
                    },
                    {
                        "type": "text",
                        "text": "準備中",
                        "size": "xl",
                        "align": "center",
                        "color": "#b8a999"
                    },
                    {
                        "type": "spacer",
                        "size": "sm"
                    },
                    {
                        "type": "text",
                        "text": "しばらくお待ちください",
                        "size": "sm",
                        "align": "center",
                        "color": "#666666"
                    }
                ]
            }
        }
    }

    data = {
        'to': user_id,
        'messages': [flex_message]
    }

    try:
        response = requests.post(
            'https://api.line.me/v2/bot/message/push',
            headers=headers,
            data=json.dumps(data)
        )
        print(f"アクセス情報送信レスポンス: {response.status_code}")
        
        if response.status_code != 200:
            print(f"送信エラー: {response.status_code}")
            print(f"エラー詳細: {response.text}")
            
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

@app.route('/', methods=['GET'])
def hello():
    return 'Hello, World!'

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
