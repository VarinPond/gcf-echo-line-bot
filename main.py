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
    elif text == "คำนวณภาษีให้หน่อย":
        user_sessions[user_id] = {"status":"wait_income","income":0}
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
        # if "reduce" in user_sessions[user_id].key():
        #     deduction = user_sessions[user_id]["reduce"]
        # else:
        deduction = 0
        total = income - deduction
        line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text=f"ภาษีที่ต้องจ่ายคือ {total}"),
                    ],
                )
            )
    elif user_sessions[user_id]["status"] == 'wait_income':
        income = float(text.replace(",",''))
        user_sessions[user_id]["income"] = income*12
        
        carousel_template = ImageCarouselTemplate(
            columns=[
                ImageCarouselColumn(
                    title="ประกันชีวิต",
                    image_url="https://raw.githubusercontent.com/VarinPond/gcf-echo-line-bot/refs/heads/main/assets/life_insurance.jpeg",
                    action=PostbackAction(label="ใช่ ฉันมี", data="ประกันชีวิต")
                ),
                ImageCarouselColumn(
                    title="กองทุน SSF",
                    image_url="https://raw.githubusercontent.com/VarinPond/gcf-echo-line-bot/refs/heads/main/assets/image_co2.jpeg",
                    action=PostbackAction(label="ใช่ ฉันมี", data="กองทุน SSF")
                ),
                ImageCarouselColumn(
                    title="กองทุน RMF",
                    image_url="https://raw.githubusercontent.com/VarinPond/gcf-echo-line-bot/refs/heads/main/assets/image_co3.jpeg",
                    action=PostbackAction(label="ใช่ ฉันมี", data="กองทุน RMF")
                )
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

    elif text == "profile":
        if isinstance(event.source, UserSource):
            profile = line_bot_api.get_profile(user_id=event.source.user_id)

            with open("flex_msgs/profile_bubble.json") as profile_bubble_json:
                profile_bubble = profile_bubble_json.read()
                profile_bubble = (
                    profile_bubble.replace("USER_PROFILE_URL", profile.picture_url)
                    .replace("LINE_USER_NAME", profile.display_name)
                    .replace("LINE_USER_STATUS", profile.status_message)
                )
                flex_profile_message = FlexMessage(
                    alt_text="my_profile_bubble",
                    contents=FlexContainer.from_json(profile_bubble),
                )
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[
                            TextMessage(text="Profile JSON: " + profile.to_str()),
                            flex_profile_message,
                        ],
                    )
                )

        else:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text="Bot can't use profile API without user ID")
                    ],
                )
            )
    elif text == "sticker":
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[StickerMessage(package_id="446", sticker_id="1988")],
            )
        )

    elif text == "emojis":
        emojis = [
            Emoji(index=0, product_id="5ac1bfd5040ab15980c9b435", emoji_id="001"),
            Emoji(index=13, product_id="5ac1bfd5040ab15980c9b435", emoji_id="002"),
        ]
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="$ LINE emoji $", emojis=emojis)],
            )
        )
    elif text == "quota":
        quota = line_bot_api.get_message_quota()
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text="type: " + quota.type),
                    TextMessage(text="value: " + str(quota.value)),
                ],
            )
        )
    elif text == "quota_consumption":
        quota_consumption = line_bot_api.get_message_quota_consumption()
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text="total usage: " + str(quota_consumption.total_usage)
                    )
                ],
            )
        )
    elif text == "push":
        line_bot_api.push_message(
            PushMessageRequest(
                to=event.source.user_id, messages=[TextMessage(text="PUSH!")]
            )
        )
    elif text == "multicast":
        line_bot_api.multicast(
            MulticastRequest(
                to=[event.source.user_id],
                messages=[
                    TextMessage(
                        text="THIS IS A MULTICAST MESSAGE, but it's slower than PUSH."
                    )
                ],
            )
        )
    elif text == "broadcast":
        line_bot_api.broadcast(
            BroadcastRequest(messages=[TextMessage(text="THIS IS A BROADCAST MESSAGE")])
        )
    elif text.startswith("broadcast "):  # broadcast 20190505
        date = text.split(" ")[1]
        logger.info("Getting broadcast result: " + date)
        result = line_bot_api.get_number_of_sent_broadcast_messages(var_date=date)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text="Number of sent broadcast messages: " + date),
                    TextMessage(text="status: " + str(result.status)),
                    TextMessage(text="success: " + str(result.success)),
                ],
            )
        )
    elif text == "bye":
        if isinstance(event.source, GroupSource):
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="Leaving group")],
                )
            )
            line_bot_api.leave_group(event.source.group_id)
        elif isinstance(event.source, RoomSource):
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="Leaving room")],
                )
            )
            line_bot_api.leave_room(room_id=event.source.room_id)
        else:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="Bot can't leave from 1:1 chat")],
                )
            )
    elif text == "confirm":
        confirm_template = ConfirmTemplate(
            text="Do it?",
            actions=[
                MessageAction(label="Yes", text="Yes!"),
                MessageAction(label="No", text="No!"),
            ],
        )
        template_message = TemplateMessage(
            alt_text="Confirm alt text", template=confirm_template
        )
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[template_message]
            )
        )
    elif text == "buttons":
        buttons_template = ButtonsTemplate(
            title="My buttons sample",
            text="Hello, my buttons",
            actions=[
                URIAction(label="Go to line.me", uri="https://line.me"),
                PostbackAction(label="ping", data="ping"),
                PostbackAction(label="ping with text", data="ping", text="ping"),
                MessageAction(label="Translate Rice", text="米"),
            ],
        )
        template_message = TemplateMessage(
            alt_text="Buttons alt text", template=buttons_template
        )
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[template_message]
            )
        )
    elif text == "carousel":
        carousel_template = CarouselTemplate(
            columns=[
                CarouselColumn(
                    text="hoge1",
                    title="fuga1",
                    actions=[
                        URIAction(label="Go to line.me", uri="https://line.me"),
                        PostbackAction(label="ping", data="ping"),
                    ],
                ),
                CarouselColumn(
                    text="hoge2",
                    title="fuga2",
                    actions=[
                        PostbackAction(
                            label="ping with text", data="ping", text="ping"
                        ),
                        MessageAction(label="Translate Rice", text="米"),
                    ],
                ),
            ]
        )
        template_message = TemplateMessage(
            alt_text="Carousel alt text", template=carousel_template
        )
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[template_message]
            )
        )
    elif text == "image_carousel":
        image_carousel_template = ImageCarouselTemplate(
            columns=[
                ImageCarouselColumn(
                    image_url="https://developers-resource.landpress.line.me/fx/clip/clip1.jpg",
                    action=DatetimePickerAction(
                        label="datetime", data="datetime_postback", mode="datetime"
                    ),
                ),
                ImageCarouselColumn(
                    image_url="https://developers-resource.landpress.line.me/fx/clip/clip2.jpg",
                    action=DatetimePickerAction(
                        label="date", data="date_postback", mode="date"
                    ),
                ),
            ]
        )
        template_message = TemplateMessage(
            alt_text="ImageCarousel alt text", template=image_carousel_template
        )
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[template_message]
            )
        )
    elif text == "flex":
        start_icon_url = "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
        bubble = FlexBubble(
            direction="ltr",
            hero=FlexImage(
                url="https://developers-resource.landpress.line.me/fx/img/01_1_cafe.png",
                size="full",
                aspect_ratio="20:13",
                aspect_mode="cover",
                action=URIAction(uri="http://example.com", label="label"),
            ),
            body=FlexBox(
                layout="vertical",
                contents=[
                    # title
                    FlexText(text="Brown Cafe", weight="bold", size="xl"),
                    # review
                    FlexBox(
                        layout="baseline",
                        margin="md",
                        contents=[
                            FlexIcon(size="sm", url=start_icon_url),
                            FlexIcon(size="sm", url=start_icon_url),
                            FlexIcon(size="sm", url=start_icon_url),
                            FlexIcon(size="sm", url=start_icon_url),
                            FlexIcon(size="sm", url=start_icon_url),
                            FlexText(
                                text="4.0",
                                size="sm",
                                color="#999999",
                                margin="md",
                                flex=0,
                            ),
                        ],
                    ),
                    # info
                    FlexBox(
                        layout="vertical",
                        margin="lg",
                        spacing="sm",
                        contents=[
                            FlexBox(
                                layout="baseline",
                                spacing="sm",
                                contents=[
                                    FlexText(
                                        text="Place", color="#aaaaaa", size="sm", flex=1
                                    ),
                                    FlexText(
                                        text="Shinjuku, Tokyo",
                                        wrap=True,
                                        color="#666666",
                                        size="sm",
                                        flex=5,
                                    ),
                                ],
                            ),
                            FlexBox(
                                layout="baseline",
                                spacing="sm",
                                contents=[
                                    FlexText(
                                        text="Time", color="#aaaaaa", size="sm", flex=1
                                    ),
                                    FlexText(
                                        text="10:00 - 23:00",
                                        wrap=True,
                                        color="#666666",
                                        size="sm",
                                        flex=5,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            footer=FlexBox(
                layout="vertical",
                spacing="sm",
                contents=[
                    # callAction
                    FlexButton(
                        style="link",
                        height="sm",
                        action=URIAction(label="CALL", uri="tel:000000"),
                    ),
                    # separator
                    FlexSeparator(),
                    # websiteAction
                    FlexButton(
                        style="link",
                        height="sm",
                        action=URIAction(label="WEBSITE", uri="https://example.com"),
                    ),
                ],
            ),
        )
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[FlexMessage(alt_text="hello", contents=bubble)],
            )
        )
    elif text == "flex_update_1":
        with open("flex_msgs/flex_update_1.json") as bubble_json:
            bubble_string = bubble_json.read()

        message = FlexMessage(
            alt_text="hello", contents=FlexContainer.from_json(bubble_string)
        )
        line_bot_api.reply_message(
            ReplyMessageRequest(reply_token=event.reply_token, messages=[message])
        )
    elif text == "flex_carousel":
        with open("flex_msgs/flex_carousel_template.json") as file_json:
            flex_carousel_template = file_json.read()

        line_bot_api.push_message(
            PushMessageRequest.from_json(flex_carousel_template),
        )
    elif text == "flex_carousel_2":
        my_flex_message = FlexMessage(
            alt_text="hello",
            contents=FlexCarousel(
                type="carousel",
                contents=[
                    FlexContainer.from_json(bubble_string),
                    FlexContainer.from_json(bubble_string),
                ],
            ),
        )
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[my_flex_message]
            )
        )
    elif text == "quick_reply":
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text="Quick reply",
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyItem(
                                    action=PostbackAction(label="label1", data="data1")
                                ),
                                QuickReplyItem(
                                    action=MessageAction(label="label2", text="text2")
                                ),
                                QuickReplyItem(
                                    action=DatetimePickerAction(
                                        label="label3", data="data3", mode="date"
                                    )
                                ),
                                QuickReplyItem(action=CameraAction(label="label4")),
                                QuickReplyItem(action=CameraRollAction(label="label5")),
                                QuickReplyItem(action=LocationAction(label="label6")),
                            ]
                        ),
                    )
                ],
            )
        )
    elif text == "link_token" and isinstance(event.source, UserSource):
        link_token_response = line_bot_api.issue_link_token(
            user_id=event.source.user_id
        )
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text="link_token: " + link_token_response.link_token)
                ],
            )
        )
    elif text == "insight_message_delivery":
        with InsightClient(configuration) as api_client:
            line_bot_insight_api = Insight(api_client)
            today = datetime.date.today().strftime("%Y%m%d")
            response = line_bot_insight_api.get_number_of_message_deliveries(
                var_date=today
            )
            if response.status == "ready":
                messages = [
                    TextMessage(text="broadcast: " + str(response.broadcast)),
                    TextMessage(text="targeting: " + str(response.targeting)),
                ]
            else:
                messages = [TextMessage(text="status: " + response.status)]
        line_bot_api.reply_message(
            ReplyMessageRequest(reply_token=event.reply_token, messages=messages)
        )
    elif text == "insight_followers":
        with InsightClient(configuration) as api_client:
            line_bot_insight_api = Insight(api_client)
            today = datetime.date.today().strftime("%Y%m%d")
            response = line_bot_insight_api.get_number_of_followers(var_date=today)
        if response.status == "ready":
            messages = [
                TextMessage(text="followers: " + str(response.followers)),
                TextMessage(text="targetedReaches: " + str(response.targeted_reaches)),
                TextMessage(text="blocks: " + str(response.blocks)),
            ]
        else:
            messages = [TextMessage(text="status: " + response.status)]
        line_bot_api.reply_message(
            ReplyMessageRequest(reply_token=event.reply_token, messages=messages)
        )
    elif text == "insight_demographic":
        with InsightClient(configuration) as api_client:
            line_bot_insight_api = Insight(api_client)
            response = line_bot_insight_api.get_friends_demographics()
        if response.available:
            messages = [
                "{gender}: {percentage}".format(
                    gender=it.gender, percentage=it.percentage
                )
                for it in response.genders
            ]
        else:
            messages = [TextMessage(text="available: false")]
        line_bot_api.reply_message(
            ReplyMessageRequest(reply_token=event.reply_token, messages=messages)
        )
    elif text == "with http info":
        response = line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="see application log")],
            )
        )
        logger.info("Got response with http status code: " + str(response.status_code))
        logger.info("Got x-line-request-id: " + response.headers["x-line-request-id"])
        logger.info("Got response with http body: " + str(response.data))
    elif text == "with http info error":
        try:
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token="invalid-reply-token",
                    messages=[TextMessage(text="see application log")],
                )
            )
        except ApiException as e:
            logger.info("Got response with http status code: " + str(e.status))
            logger.info("Got x-line-request-id: " + e.headers["x-line-request-id"])
            logger.info(
                "Got response with http body: " + str(ErrorResponse.from_json(e.body))
            )
    else:
        # Your FastAPI server URL (update if not running locally or using a different port)
        url = "https://c926-184-22-104-248.ngrok-free.app/chat"

        # The message you want to send to the chatbot
        params = {
            "message": event.message.text
        }

        # Make the GET request
        response = requests.get(url, params=params)

        answer = response.json()["message"]
            
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=answer)],
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
    data = event.postback.data
    if data == "ping":
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text="pong")]
            )
        )
    elif data == "ประกันชีวิต":
        # if "reduce" not in user_sessions[user_id].key():
        #     user_sessions[user_id]["reduce"] = 100000
        # else:
        #     user_sessions[user_id]["reduce"] += 100000
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text='ลดหย่อนได้ 100,000 บาท\nหากไม่มีการลดหย่อนเพิ่มเติมแล้วพิม "ไม่มี"')]
            )
        )
    elif data == "กองทุน RMF":
        # if "reduce" not in user_sessions[user_id].key():
        #     user_sessions[user_id]["reduce"] = 200000
        # else:
        #     user_sessions[user_id]["reduce"] += 200000
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text='ลดหย่อนได้ 200,000 บาท\nหากไม่มีการลดหย่อนเพิ่มเติมแล้วพิม "ไม่มี"')]
            )
        )
    elif data == "กองทุน SSF":
        # if "reduce" not in user_sessions[user_id].key():
        #     user_sessions[user_id]["reduce"] = 150000
        # else:
        #     user_sessions[user_id]["reduce"] += 150000
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text='ลดหย่อนได้ 150,000 บาท\nหากไม่มีการลดหย่อนเพิ่มเติมแล้วพิม "ไม่มี"')]
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
