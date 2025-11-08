import logging
# import httpx  # موقتاً نیاز نداریم
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- تنظیمات اولیه ---

# ! توکن ربات خود را اینجا قرار دهید
BOT_TOKEN = "8426082406:AAHljMmL6uvDrIbMHmT3Gv2d107C8IFS0hs" 

# ! آدرس پایه API (موقتاً نیاز نداریم)
# API_BASE_URL = "https://yoursite.com/api/"

# فعال‌سازی لاگ (برای خطایابی)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- داده‌های تستی (Mock Data) ---
# جایگزین API جنگو برای تست

MOCK_CATEGORIES = [
    {"id": 1, "name": " دسته تستی الف (محصولات بهداشتی)"},
    {"id": 2, "name": "دسته تستی ب (لوازم جانبی)"},
]

MOCK_PRODUCTS = {
    "1": [ # محصولات دسته ۱
        {"id": 101, "name": "محصول تستی ۱ (از دسته الف)"},
        {"id": 102, "name": "محصول تستی ۲ (از دسته الف)"},
    ],
    "2": [ # محصولات دسته ۲
        {"id": 201, "name": "محصول تستی ۳ (از دسته ب)"},
    ],
}

MOCK_PRODUCT_DETAILS = {
    "101": {"id": 101, "name": "محصول تستی ۱", "description": "این توضیحات تستی برای محصول ۱۰۱ است.", "price": 50000, "category_id": 1},
    "102": {"id": 102, "name": "محصول تستی ۲", "description": "توضیحات کامل برای محصول ۱۰۲.", "price": 75000, "category_id": 1},
    "201": {"id": 201, "name": "محصول تستی ۳", "description": "این محصول در دسته ب قرار دارد.", "price": 120000, "category_id": 2},
}

# --- توابع کمکی ---

# async def fetch_from_api(endpoint: str):
#     """ (موقتاً غیرفعال شد) تابع کمکی برای دریافت اطلاعات از API جنگو"""
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(f"{API_BASE_URL}{endpoint}")
#             response.raise_for_status()
#             return response.json()
#         except httpx.HTTPStatusError as e:
#             logger.error(f"HTTP error fetching {endpoint}: {e}")
#             return None
#         except Exception as e:
#             logger.error(f"Error fetching {endpoint}: {e}")
#             return None

# --- توابع اصلی ربات (Handlers) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پاسخ به دستور /start و نمایش منوی اصلی"""
    keyboard = [
        [InlineKeyboardButton("🛍️ نمایش محصولات", callback_data="show_categories")],
        [InlineKeyboardButton("🛒 سبد خرید من (به زودی)", callback_data="view_cart")],
        [InlineKeyboardButton("📞 پشتیبانی", callback_data="support")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "سلام! به فروشگاه ما خوش آمدید. (نسخه تست آفلاین)\nلطفاً یک گزینه را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت تمام دکمه‌های شیشه‌ای (Inline Buttons)"""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "show_categories":
        await list_categories(query)
    
    elif data.startswith("category_"):
        category_id = data.split("_")[1]
        await list_products(query, category_id)
        
    elif data.startswith("product_"):
        product_id = data.split("_")[1]
        await show_product_detail(query, product_id)
    
    elif data == "support":
        await query.edit_message_text(text="برای پشتیبانی با @YourSupportAdmin تماس بگیرید.")


async def list_categories(query):
    """لیست دسته‌بندی‌ها را از داده‌های تستی نمایش می‌دهد"""
    
    # --- تغییر یافته: به جای API از داده تستی می‌خواند ---
    categories = MOCK_CATEGORIES 
    
    if not categories:
        await query.edit_message_text(text="خطا: هیچ دسته‌بندی تستی تعریف نشده است.")
        return

    keyboard = []
    for cat in categories:
        button = InlineKeyboardButton(cat['name'], callback_data=f"category_{cat['id']}")
        keyboard.append([button])
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="لطفاً یک دسته‌بندی را انتخاب کنید:", reply_markup=reply_markup)


async def list_products(query, category_id):
    """لیست محصولات یک دسته را از داده‌های تستی نمایش می‌دهد"""
    
    # --- تغییر یافته: به جای API از داده تستی می‌خواند ---
    products = MOCK_PRODUCTS.get(category_id)
    
    if not products:
        await query.edit_message_text(text="محصولی در این دسته تستی یافت نشد.")
        return

    keyboard = []
    for prod in products:
        button = InlineKeyboardButton(prod['name'], callback_data=f"product_{prod['id']}")
        keyboard.append([button])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به دسته‌بندی‌ها", callback_data="show_categories")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=f"محصولات این دسته:", reply_markup=reply_markup)


async def show_product_detail(query, product_id):
    """جزئیات کامل یک محصول را از داده‌های تستی نمایش می‌دهد"""
    
    # --- تغییر یافته: به جای API از داده تستی می‌خواند ---
    product = MOCK_PRODUCT_DETAILS.get(product_id)
    
    if not product:
        await query.edit_message_text(text="خطا در دریافت اطلاعات محصول تستی.")
        return

    message_text = f"**{product['name']}**\n\n"
    message_text += f"{product['description']}\n\n"
    message_text += f"قیمت: **{product['price']:,} تومان**"

    keyboard = [
        [InlineKeyboardButton("➕ افزودن به سبد خرید (به زودی)", callback_data=f"add_cart_{product_id}")],
        [InlineKeyboardButton(f"🔙 بازگشت به محصولات", callback_data=f"category_{product['category_id']}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text=message_text, reply_markup=reply_markup, parse_mode="Markdown")


# --- تابع اصلی اجرای ربات ---

def main():
    """اجرا کننده اصلی ربات"""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bot is running in MOCK (Test) mode...")
    application.run_polling()


if __name__ == "__main__":
    main()