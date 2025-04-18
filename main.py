import os
import json
import datetime
import logging as logger
import tempfile
import functions_framework
import requests

from linebot.v3 import WebhookHandler
from linebot.v3.models import UnknownEvent
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    LocationMessageContent,
    StickerMessageContent,
    ImageMessageContent,
    VideoMessageContent,
    AudioMessageContent,
    FileMessageContent,
    UserSource,
    RoomSource,
    GroupSource,
    FollowEvent,
    UnfollowEvent,
    JoinEvent,
    LeaveEvent,
    PostbackEvent,
    BeaconEvent,
    MemberJoinedEvent,
    MemberLeftEvent,
)


from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    PushMessageRequest,
    MulticastRequest,
    BroadcastRequest,
    TextMessage,
    ApiException,
    LocationMessage,
    StickerMessage,
    ImageMessage,
    TemplateMessage,
    FlexMessage,
    Emoji,
    QuickReply,
    QuickReplyItem,
    ConfirmTemplate,
    ButtonsTemplate,
    CarouselTemplate,
    CarouselColumn,
    ImageCarouselTemplate,
    ImageCarouselColumn,
    FlexBubble,
    FlexImage,
    FlexBox,
    FlexText,
    FlexIcon,
    FlexButton,
    FlexSeparator,
    FlexContainer,
    FlexCarousel,
    MessageAction,
    URIAction,
    PostbackAction,
    DatetimePickerAction,
    CameraAction,
    CameraRollAction,
    LocationAction,
    ErrorResponse,
    ShowLoadingAnimationRequest,
    Message,
)

from linebot.v3.insight import ApiClient as InsightClient, Insight
from commons.yaml_env import load_yaml_to_env

load_yaml_to_env("scripts/line_secret.yml")

CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]


configuration = Configuration(
    access_token=CHANNEL_ACCESS_TOKEN,
)
handler = WebhookHandler(CHANNEL_SECRET)

# Initialize the Messaging API client once
with ApiClient(configuration) as api_client:
    line_bot_api = MessagingApi(api_client)
    line_bot_blob_api = MessagingApiBlob(api_client)


@functions_framework.http
def callback(request):
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    print("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print(
            "Invalid signature. Please check your channel access token/channel secret."
        )

    return "OK"

user_sessions = {}  # สำหรับเก็บสถานะของแต่ละผู้ใช้

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    line_bot_api.show_loading_animation(
        ShowLoadingAnimationRequest(chat_id=event.source.user_id)
    )
    
    text = event.message.text
    user_id = event.source.user_id
    
    if text == "beat":
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text="Hello, My name is Beat, Hope you enjoy :)"),
                ],
            )
        )
    elif text == "my id":
        line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text=f"Hello, My name is Beat, your id:{user_id}"),
                    ],
                )
            )
    elif text == "my status":
        line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text=f"Status: {user_sessions[user_id]["status"]}"),
                    ],
                )
            )
    elif text == "คำนวณภาษีให้หน่อย":
        user_sessions[user_id] = {"status":"wait_income","income":0,"reduce":0}
        line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text=f"กรุณาระบุรายได้ต่อเดือนของคุณ (ตัวเลข):"),
                    ],
                )
            ) 
    elif user_sessions[user_id]["status"] == 'wait_income' and text == "ไม่มี":
        user_sessions[user_id]["status"] = 'ask_deductions'
        income = user_sessions[user_id]["income"]
        deduction = user_sessions[user_id]["reduce"]
        
        total = income - deduction
        line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text=f"ภาษีที่ต้องจ่ายคือ {total}"),
                    ],
                )
            )
    elif "X" in user_sessions[user_id]["status"]:
        user_sessions[user_id]["reduce"] += float(text.replace(",",''))
        user_sessions[user_id]["status"] = 'wait_income'
        line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text=f'หากไม่มีการลดหย่อนแล้ว พิม "ไม่มี"'),
                    ],
                )
            )
    elif user_sessions[user_id]["status"] == 'wait_income':
        income = float(text.replace(",",''))
        user_sessions[user_id]["income"] = income*12
        
        carousel_template = CarouselTemplate(
            columns=[
                CarouselColumn(
                    text="เลือกกองทุน",
                    title="กองทุน",
                    thumbnail_image_url="https://raw.githubusercontent.com/VarinPond/gcf-echo-line-bot/refs/heads/main/assets/fund.png",
                    actions=[
                        PostbackAction(label="กองทุน SSF", data=f"กองทุน SSFXxX{user_id}"),
                        PostbackAction(label="กองทุน RMF", data=f"กองทุน RMFXxX{user_id}"),
                    ],
                ),
                CarouselColumn(
                    text=" ",
                    title="ประกันสังคม",
                    thumbnail_image_url="https://raw.githubusercontent.com/VarinPond/gcf-echo-line-bot/refs/heads/main/assets/work.png",
                    actions=[
                        PostbackAction(label="ใช่ ฉันมี", data=f"ประกันสังคมXxX{user_id}"),
                        PostbackAction(label="ศึกษาเพิ่มเติม", data="ศึกษาเพิ่มเติม ประกันสังคม"),
                    ],
                ),
                CarouselColumn(
                    text=" ",
                    title="ประกันชีวิต",
                    thumbnail_image_url="https://raw.githubusercontent.com/VarinPond/gcf-echo-line-bot/refs/heads/main/assets/life.png",
                    actions=[
                        PostbackAction(label="ใช่ ฉันมี", data=f"ประกันชีวิตXxX{user_id}"),
                        PostbackAction(label="ศึกษาเพิ่มเติม", data="ศึกษาเพิ่มเติม ประกันชีวิต"),
                    ],
                ),
                CarouselColumn(
                    text=" ",
                    title="บริจาคทั่วไป",
                    thumbnail_image_url="https://raw.githubusercontent.com/VarinPond/gcf-echo-line-bot/refs/heads/main/assets/donate.png",
                    actions=[
                        PostbackAction(label="ใช่ ฉันมี", data=f"บริจาคทั่วไปXxX{user_id}"),
                        PostbackAction(label="ศึกษาเพิ่มเติม", data="ศึกษาเพิ่มเติม บริจาคทั่วไป"),
                    ],
                ),
            ]
        )
        
        
        template_message = TemplateMessage(
            alt_text="Carousel alt text", template=carousel_template
        )
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[
                    TextMessage(text=f"รายได้ต่อปีของคุณ :{income*12}"),
                    template_message]
            )
        )  
    else:
        # # Your FastAPI server URL (update if not running locally or using a different port)
        # url = "https://c926-184-22-104-248.ngrok-free.app/chat"

        # # The message you want to send to the chatbot
        # params = {
        #     "message": event.message.text
        # }

        # # Make the GET request
        # response = requests.get(url, params=params)

        # answer = response.json()["message"]
            
        # line_bot_api.reply_message(
        #     ReplyMessageRequest(
        #         reply_token=event.reply_token,
        #         messages=[TextMessage(text=answer)],
        #     )
        # )
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="ไม่มีคำตอบ")],
            )
        )


@handler.add(MessageEvent, message=StickerMessageContent)
def handle_sticker_message(event):
    line_bot_api.show_loading_animation_with_http_info(
        ShowLoadingAnimationRequest(chat_id=event.source.user_id)
    )
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                StickerMessage(
                    package_id=event.message.package_id,
                    sticker_id=event.message.sticker_id,
                )
            ],
        )
    )


@handler.add(MessageEvent, message=LocationMessageContent)
def handle_location_message(event):
    line_bot_api.show_loading_animation_with_http_info(
        ShowLoadingAnimationRequest(chat_id=event.source.user_id)
    )
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                LocationMessage(
                    title="Location",
                    address=event.message.address,
                    latitude=event.message.latitude,
                    longitude=event.message.longitude,
                )
            ],
        )
    )


@handler.add(
    MessageEvent,
    message=(ImageMessageContent, VideoMessageContent, AudioMessageContent),
)
def handle_content_message(event):
    line_bot_api.show_loading_animation_with_http_info(
        ShowLoadingAnimationRequest(chat_id=event.source.user_id)
    )
    if isinstance(event.message, ImageMessageContent):
        ext = "jpg"
        ftype = "image"
    elif isinstance(event.message, VideoMessageContent):
        ext = "mp4"
        ftype = "viedio"
    elif isinstance(event.message, AudioMessageContent):
        ext = "m4a"
        ftype = "audio"
    else:
        return

    message_content = line_bot_blob_api.get_message_content(message_id=event.message.id)
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                TextMessage(text=f"Thank for sending {ftype} file"),
            ],
        )
    )


@handler.add(MessageEvent, message=FileMessageContent)
def handle_file_message(event):
    message_content = line_bot_blob_api.get_message_content(message_id=event.message.id)
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                TextMessage(text="Thank for sending the file."),
            ],
        )
    )


@handler.add(FollowEvent)
def handle_follow(event):
    logger.info("Got Follow event:" + event.source.user_id)
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text="Got follow event")],
        )
    )


@handler.add(UnfollowEvent)
def handle_unfollow(event):
    logger.info("Got Unfollow event:" + event.source.user_id)


@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text="Joined this " + event.source.type)],
        )
    )


@handler.add(LeaveEvent)
def handle_leave():
    logger.info("Got leave event")


@handler.add(PostbackEvent)
def handle_postback(event: PostbackEvent):
    raw_data = event.postback.data
    data, user_id = raw_data.split("XxX")
    if data == "ping":
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text="pong")]
            )
        )
    elif data == "ประกันชีวิต":
        user_sessions[user_id]["status"] = "Xประกันชีวิต"
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text=f'เบี้ยประกันชีวิตที่จ่ายตลอดทั้งปีเป็นเท่าไหร่ (สูงสุด 100,000 บาท)')]
            )
        )
    elif data == "กองทุน RMF":
        user_sessions[user_id]["status"] = "Xกองทุน RMF"
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text=f'กองทุน RMF สามารถลงทุนได้สูงสุด 30% ของรายได้ทั้งปี (สูงสุด {str(int(user_sessions[user_id]["income"]*0.3))} บาท) กรอกมูลค่าการลงทุนตลอดทั้งปี:')]
            )
        )
    elif data == "กองทุน SSF":
        user_sessions[user_id]["status"] = "Xกองทุน SSF"
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text=f'กองทุน SSF สามารถลงทุนได้สูงสุด 30% ของรายได้ทั้งปี (สูงสุด {str(int(user_sessions[user_id]["income"]*0.3))} บาท) กรอกมูลค่าการลงทุนตลอดทั้งปี:')]
            )
        )
    elif data == "ประกันสังคม":
        user_sessions[user_id]["status"] = "Xประกันสังคม"
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text=f'จำนวนเงินที่ถูกหักทั้งปี (ไม่รวมหน้าจ้างสมทบ):')]
            )
        )
    elif data == "บริจาคทั่วไป":
        user_sessions[user_id]["reduce"] += 10000
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text='ลดหย่อนได้ 10,000 บาท\nหากไม่มีการลดหย่อนเพิ่มเติมแล้วพิม "ไม่มี"')]
            )
        )
    elif data == "datetime_postback":
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=event.postback.params["datetime"])],
            )
        )
    elif data == "date_postback":
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=event.postback.params["date"])],
            )
        )
    else:
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text="ข้อความ\nuser:{user_id}\ndata:{data}")]
            )
        )
        


@handler.add(BeaconEvent)
def handle_beacon(event: BeaconEvent):
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                TextMessage(
                    text="Got beacon event. hwid={}, device_message(hex string)={}".format(
                        event.beacon.hwid, event.beacon.dm
                    )
                )
            ],
        )
    )


@handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                TextMessage(text="Got memberJoined event. event={}".format(event))
            ],
        )
    )


@handler.add(MemberLeftEvent)
def handle_member_left(event):
    logger.info("Got memberLeft event")


@handler.add(UnknownEvent)
def handle_unknown_left(event):
    logger.info(f"unknown event {event}")
