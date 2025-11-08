import logging
import httpx  # کتابخانه مدرن و غیرهمزمان به جای requests
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- تنظیمات اولیه ---

# ! توکن ربات خود را اینجا قرار دهید
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE" 

# ! آدرس پایه API سایت جنگو شما
API_BASE_URL = "https://yoursite.com/api/"

# فعال‌سازی لاگ (برای خطایابی)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- توابع کمکی ---

async def fetch_from_api(endpoint: str):
    """یک تابع کمکی برای دریافت اطلاعات از API جنگو"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}{endpoint}")
            response.raise_for_status()  # بررسی خطاهای HTTP
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching {endpoint}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {endpoint}: {e}")
            return None

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
        "سلام! به فروشگاه ما خوش آمدید. لطفاً یک گزینه را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت تمام دکمه‌های شیشه‌ای (Inline Buttons)"""
    query = update.callback_query
    await query.answer()  # به تلگرام می‌گوید که دکمه دریافت شد

    data = query.data

    if data == "show_categories":
        await list_categories(query)
    
    elif data.startswith("category_"):
        # جدا کردن آیدی دسته از "category_1"
        category_id = data.split("_")[1]
        await list_products(query, category_id)
        
    elif data.startswith("product_"):
        # جدا کردن آیدی محصول از "product_12"
        product_id = data.split("_")[1]
        await show_product_detail(query, product_id)
    
    elif data == "support":
        await query.edit_message_text(text="برای پشتیبانی با @YourSupportAdmin تماس بگیرید.")
        
    # اینجا می‌توانید دکمه‌های دیگر مثل "view_cart" را مدیریت کنید


async def list_categories(query):
    """لیست دسته‌بندی‌ها را از API دریافت و به صورت دکمه نمایش می‌دهد"""
    categories = await fetch_from_api("categories/")
    
    if not categories:
        await query.edit_message_text(text="خطایی در دریافت دسته‌بندی‌ها رخ داد. لطفاً بعداً تلاش کنید.")
        return

    keyboard = []
    # فرض می‌کنیم API یک لیست از دیکشنری‌ها برمی‌گرداند: [{"id": 1, "name": "دسته الف"}]
    for cat in categories:
        button = InlineKeyboardButton(cat['name'], callback_data=f"category_{cat['id']}")
        keyboard.append([button])
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="لطفاً یک دسته‌بندی را انتخاب کنید:", reply_markup=reply_markup)


async def list_products(query, category_id):
    """لیست محصولات یک دسته را از API دریافت و نمایش می‌دهد"""
    # فرض می‌کنیم API شما از فیلتر پشتیبانی می‌کند
    products = await fetch_from_api(f"products/?category={category_id}")
    
    if not products:
        await query.edit_message_text(text="محصولی در این دسته یافت نشد.")
        return

    keyboard = []
    # فرض می‌کنیم API: [{"id": 12, "name": "محصول الف"}]
    for prod in products:
        button = InlineKeyboardButton(prod['name'], callback_data=f"product_{prod['id']}")
        keyboard.append([button])
    
    # اضافه کردن دکمه بازگشت
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به دسته‌بندی‌ها", callback_data="show_categories")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=f"محصولات این دسته:", reply_markup=reply_markup)


async def show_product_detail(query, product_id):
    """جزئیات کامل یک محصول را از API دریافت و نمایش می‌دهد"""
    product = await fetch_from_api(f"products/{product_id}/")
    
    if not product:
        await query.edit_message_text(text="خطا در دریافت اطلاعات محصول.")
        return

    # فرض می‌کنیم API: {"id": 12, "name": "محصول الف", "description": "توضیحات...", "price": 50000, "category_id": 1}
    # ارسال عکس محصول (اگر API آدرس عکس را می‌دهد)
    # if product.get('image_url'):
    #     await query.message.reply_photo(photo=product['image_url'])

    message_text = f"**{product['name']}**\n\n"
    message_text += f"{product['description']}\n\n"
    message_text += f"قیمت: **{product['price']:,} تومان**" # فرمت‌دهی قیمت

    keyboard = [
        [InlineKeyboardButton("➕ افزودن به سبد خرید (به زودی)", callback_data=f"add_cart_{product_id}")],
        # دکمه بازگشت به لیست محصولات همان دسته
        [InlineKeyboardButton(f"🔙 بازگشت به محصولات", callback_data=f"category_{product['category_id']}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # parse_mode="Markdown" را برای bold کردن متن تنظیم می‌کنیم
    await query.edit_message_text(text=message_text, reply_markup=reply_markup, parse_mode="Markdown")


# --- تابع اصلی اجرای ربات ---

def main():
    """اجرا کننده اصلی ربات"""
    # ساخت Application
    application = Application.builder().token(BOT_TOKEN).build()

    # افزودن Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    # اجرای ربات (در حالت polling)
    logger.info("Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()