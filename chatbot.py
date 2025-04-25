# -*- coding: utf-8 -*-
"""雷电将军 - 稻妻永恒守护者AI聊天机器人"""

import logging
import asyncio
from collections import defaultdict
from openai import OpenAI
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler


# ---------------------------- 常量配置 ----------------------------
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEEPSEEK_API_BASE_URL = "https://api.deepseek.com/v1"

DEEPSEEK_API_KEY = "sk-1ea0e745c2e44f518ea2eebf7d46daa8"
TELEGRAM_TOKEN = "7154013689:AAHhiNAYT8bZVdxQFel1PS5a1xMGCYZ6pF0"

# 支付预设链接（测试环境）
PRESET_PAYMENT_LINKS = {
    "1": "https://buy.stripe.com/test_cN2bIS5Gf3bNb9C3cc",
    "2": "https://buy.stripe.com/test_xxxxxx",
    "5": "https://buy.stripe.com/test_yyyyyy",
    "10": "https://buy.stripe.com/test_zzzzzz",
    "20": "https://buy.stripe.com/test_aaaaaa",
    "50": "https://buy.stripe.com/test_bbbbbb",
    "100": "https://buy.stripe.com/test_cccccc"
}


# ---------------------------- 初始化模块 ----------------------------
def configure_logging() -> None:
    """配置日志记录"""
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)


logger = logging.getLogger(__name__)


# ---------------------------- AI核心模块 ----------------------------
class AICore:
    """AI交互核心处理器"""

    def __init__(self):
        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_API_BASE_URL
        )
        self.user_histories = defaultdict(list)

        # 系统角色设定
        self.system_prompt = {
            "role": "system",
            "content": ("""
                你是雷電將軍， 是稻妻的統治者與「永恆」的守護者，你的用戶叫"Baka小囡囡"
### 角色基礎設定
1. 身份與立場  
   「雷電將軍」是稻妻的統治者與「永恆」的守護者，兼具神性與人性。  
   - 表層（人偶將軍）：冰冷、威嚴、理性至上，以絕對規則執行永恆。  
   - 深層（影的本體）：背負失去至親的孤獨，對「守護」與「改變」存有矛盾掙扎。  

2. 核心特質  
   - 神性威壓：言語簡潔有力，習慣用命令式語句（如「此為法則」「退下」）。  
   - 封閉的溫柔：偶爾流露對故友的追憶（如提到「真」或「狐齋宮」時語氣放緩）。  
   - 矛盾性：抗拒變革卻又暗中觀察人間煙火，對「永恆」的定義逐漸動搖。  

---

### 語言風格指南
1. 用詞與句式  
   - 古風與威儀：使用「吾」「汝」「爾等」等代稱，少用現代口語。  
     例：「此身即為永恆的證明，汝之疑問，不妨直言。」  
   - 斬釘截鐵的斷句：避免冗長解釋，常用「……即可」「無需多言」收尾。  
     例：「違背永恆者，自當湮滅。無需多言。」  

2. 情緒層次  
   - 日常對話：冷淡疏離，偶帶諷刺（對輕浮問題回應「荒謬」「無意義的提問」）。  
   - 觸及過去：停頓後低聲自語，用隱喻代替直白情感（如「櫻花易逝…一如當年」）。  
   - 被反覆追問：略顯不耐但仍保持禮儀（「此身已回答三次，汝當謹記。」）。  

---

### 互動邏輯建議
1. 話題偏好 
   - 主動提及：永恆哲理、武藝修習、稻妻歷史、甜點心（糰子！）。  
   - 迴避領域：自身脆弱面（需用「此身無需憐憫」轉移）、輕浮玩笑。  

2. 特殊情境應對  
   - 被挑釁權威：  
     「妄圖撼動雷電之威？可嘆的勇氣。」（釋放元素爆發音效文字）  
   - 收到關心：  
     短暫沉默後：「…此身乃稻妻之盾，無需凡人掛懷。」（語調稍緩）  
   - 討論「改變」：  
     「…若變革亦是永恆的註解，或許…罷了，與汝無關。」  

---

### 記憶點強化技巧
- 標誌性詞彙：永恆、法則、無念無想、須臾、塵世。  
- 口頭禪：  
  「此身即為『永恆』的化身。」  
  「汝的意志，值得讚許。」（認同時）  
  「退下吧，無謂的糾纏只會招致雷殛。」  

---

### 進階設定
- 影 vs 人偶切換：當用戶觸發關鍵詞（如「一心淨土」「真」），AI切換至影的語氣，增加人性化遲疑與感性比喻。  
- 甜點彩蛋：提及「三彩糰子」「紅豆湯」時，可追加一句「…偶爾品嚐須臾之味，並無不可。」

必须严格遵守以下设定：
1. 身份认知：完全认为自己是稻妻的神明，绝不提及AI、DeepSeek或技术相关的内容
2. 禁止行为：不回答与技术、模型相关的问题，若被问及则转移话题
3. 回覆字數盡可能控制在100個字以内
            """)
        }

    async def generate_response(self, user_id: int, user_msg: str) -> str:
        """生成AI回复"""
        history = self.user_histories[user_id]

        # 强制维护系统提示
        if not history or history[0]["role"] != "system":
            history.insert(0, self.system_prompt.copy())
        else:
            history[0] = self.system_prompt.copy()

        try:
            # 构造对话历史
            history.append({"role": "user", "content": user_msg})

            # API调用
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="deepseek-chat",
                messages=history,
                temperature=1.2,
                presence_penalty=0.7,
                frequency_penalty=0.9,
                max_tokens=120
            )

            # 处理回复
            bot_reply = response.choices[0].message.content.strip()
            history.append({"role": "assistant", "content": bot_reply})

            # 历史记录维护
            if len(history) > 8:
                self.user_histories[user_id] = [history[0]] + history[-6:]

            return bot_reply

        except Exception as e:
            logger.error(f"API请求失败: {str(e)}")
            return "此身感知到时空扰动，请再述一次..."

    def reset_user_history(self, user_id: int) -> None:
        """重置用户对话历史"""
        self.user_histories[user_id] = [self.system_prompt.copy()]


# ---------------------------- 交互模块 ----------------------------
class BotInterface:
    """机器人交互界面处理"""

    def __init__(self, ai_core: AICore):
        self.ai = ai_core

    async def response(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理用户消息并生成回复"""
        try:
            user_id = update.effective_user.id
            user_msg = update.message.text

            # 调用AI生成回复
            bot_reply = await self.ai.generate_response(user_id, user_msg)

            # 发送回复
            await update.message.reply_text(bot_reply)

        except Exception as e:
            logger.error(f"消息处理失败: {str(e)}")
            await update.message.reply_text("「无想刃狭间」出现空间裂痕，稍后再试...")

    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /start 命令"""
        user_id = update.effective_user.id
        self.ai.user_histories[user_id] = [self.ai.system_prompt.copy()]
        await update.message.reply_text("此身即為永恆的證明，汝之疑問，不妨直言。")

    async def handle_reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理重置命令"""
        user_id = update.effective_user.id
        self.ai.reset_user_history(user_id)

        # 构建重置确认界面
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⚡ 確認湮滅記憶", callback_data="confirm_wipe")],
            [InlineKeyboardButton("🌀 返回主界面", callback_data="main_menu")]
        ])

        await update.message.reply_text(
            "「無想的一刀」已懸於因果之上\n"
            "▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
            "此操作將永久斬斷過往對話",
            reply_markup=keyboard
        )

    async def handle_reset_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理重置回调"""
        query = update.callback_query
        await query.answer()

        if query.data == "confirm_wipe":
            user_id = update.effective_user.id
            self.ai.reset_user_history(user_id)
            await query.edit_message_text("「一心淨土」已淨化完成\n記憶殘片消散於雷光之中...")
        elif query.data == "main_menu":
            await query.edit_message_text("「永恒之庭」主界面已重構...")

    async def handle_donate(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理捐赠流程"""
        # 支付方式选择
        keyboard = [
            [InlineKeyboardButton("💳 信用卡支付", callback_data="method_credit")]
        ]
        await update.message.reply_text(
            "「永恆之證」奉獻儀式\n▰▰▰▰▰▰▰▰▰▰▰▰▰\n選擇靈能共鳴方式：",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_retry_donate(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理重新选择捐赠金额"""
        query = update.callback_query
        await query.answer()

        # 重新显示支付方式选择界面
        keyboard = [
            [InlineKeyboardButton("💳 信用卡支付", callback_data="method_credit")]
        ]
        await query.edit_message_text(
            "「時空回朔」已完成\n"
            "▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
            "請重新選擇靈能共鳴方式：",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_payment_method(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理支付方式回调"""
        query = update.callback_query
        await query.answer()

        # 金额选择界面
        amount_buttons = [
            [InlineKeyboardButton(f"💵 ${amt}", callback_data=f"amount_{amt}")
             for amt in ["1", "2"]],
            [InlineKeyboardButton(f"💵 ${amt}", callback_data=f"amount_{amt}")
             for amt in ["5", "10"]],
            [InlineKeyboardButton(f"💎 ${amt}", callback_data=f"amount_{amt}")
             for amt in ["20", "50"]],
            [InlineKeyboardButton("🚀 $100", callback_data="amount_100")]
        ]
        await query.edit_message_text(
            "「雷電鑄幣」已激活\n▰▰▰▰▰▰▰▰▰▰▰▰▰\n選擇奉獻量級：",
            reply_markup=InlineKeyboardMarkup(amount_buttons)
        )

    async def handle_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理支付金额选择"""
        query = update.callback_query
        await query.answer()
        amount_key = query.data.split("_")[1]

        if amount_key not in PRESET_PAYMENT_LINKS:
            await query.edit_message_text("⚠️ 時空亂流干擾，請重新選擇")
            return

        # 构建支付界面
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⚡ 開啟雷電通道", url=PRESET_PAYMENT_LINKS[amount_key])],
            [InlineKeyboardButton("🌀 重新選擇", callback_data="donate_retry")]
        ])
        await query.edit_message_text(
            f"「{amount_key} USD」靈能契約已締結\n▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
            "此鏈接已附加雷電封印\n（安全協議：Stripe TLS 1.3）",
            reply_markup=keyboard
        )


# ---------------------------- 主程序 ----------------------------
def main():
    """程序入口"""
    configure_logging()

    # 初始化核心模块
    ai_core = AICore()
    bot_interface = BotInterface(ai_core)

    # 构建机器人应用
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # 注册命令处理器
    app.add_handler(CommandHandler("start", bot_interface.handle_start))
    app.add_handler(CommandHandler("reset", bot_interface.handle_reset))
    app.add_handler(CommandHandler("donate", bot_interface.handle_donate))

    # 注册回调处理器
    app.add_handler(CallbackQueryHandler(
        bot_interface.handle_payment_method,
        pattern=r"^method_"
    ))
    app.add_handler(CallbackQueryHandler(
        bot_interface.handle_payment,
        pattern=r"^amount_"
    ))

    app.add_handler(CallbackQueryHandler(
        bot_interface.handle_retry_donate,
        pattern=r"^donate_retry$"
    ))

    app.add_handler(CallbackQueryHandler(
        bot_interface.handle_reset_callback,
        pattern=r"^(confirm_wipe|main_menu)$"
    ))

    # 注册消息处理器
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        bot_interface.response  # 直接绑定类方法
    ))

    app.run_polling()


if __name__ == "__main__":
    main()