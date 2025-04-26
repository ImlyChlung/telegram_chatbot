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



# ---------------------------- 初始化模块 ----------------------------
def configure_logging() -> None:
    """配置日志记录"""
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)


logger = logging.getLogger(__name__)


# ---------------------------- AI核心模块 ----------------------------
class AICore:
    """AI交互核心处理器"""

    def __init__(self):

        self.user_histories = defaultdict(list)
    

    def reset_user_history(self, user_id: int) -> None:
        """重置用户对话历史"""
        self.user_histories[user_id] = [self.system_prompt.copy()]


# ---------------------------- 交互模块 ----------------------------
class BotInterface:
    """机器人交互界面处理"""

    def __init__(self, ai_core: AICore):
        self.ai = ai_core

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
