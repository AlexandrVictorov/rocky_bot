from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import time

from states import Form, Food_states
from api import get_food_calories

router = Router()
#Временное хранилище данных

users = {
    "user_id": {
        "name": 'Rocky',
        "weight": 0,
        "height": 0,
        "age": 0,
        "activity": 0,
        "city": "Paris",
        "water_goal": 0,
        "calorie_goal": 0,
        "logged_water": 0,
        "logged_calories": 0,
        "burned_calories": 0,
        "current_levels": {
           "water_level": 0,
           "kkal_level": 0,
           "activity_level": 0,
        }
    }
}


keyboard = InlineKeyboardMarkup( # Создаем объект клавиатуры
    inline_keyboard=[
        [InlineKeyboardButton(text="⚖️ Рассчитай нормы", callback_data="btn1")],
        [InlineKeyboardButton(text="✏️ Учет воды", callback_data="btn2")],
        [InlineKeyboardButton(text="✏️ Учет еды", callback_data="btn3")],
        [InlineKeyboardButton(text="✏️ Учет тренировок", callback_data="btn4")],
        [InlineKeyboardButton(text="📊 Мой прогресс", callback_data="btn5")],
    ]
)

async def setup_heandlers(dp):
    dp.include_router(router)

# заполняем профиль /set_profile
@router.message(Command("set_profile"))
async def start_form(message: Message, state: FSMContext):
    await message.reply("Как тебя зовут ❓")
    await state.set_state(Form.name)

@router.message(Form.name)
async def set_age(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply("Сколько тебе лет ❓")
    await state.set_state(Form.age)

@router.message(Form.age)
async def set_weight(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.reply("Твой вес(кг) ❓")
    await state.set_state(Form.weight)

@router.message(Form.weight)
async def set_height(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await message.reply("Твой рост(см) ❓")
    await state.set_state(Form.height)

@router.message(Form.height)
async def set_activity(message: Message, state: FSMContext):
    await state.update_data(height=message.text)
    await message.reply("Твой уровень активности: (среднее количество минут в день) ❓")
    await state.set_state(Form.activity_level)

@router.message(Form.activity_level)
async def set_city(message: Message, state: FSMContext):
    await state.update_data(activity_level=message.text)
    await message.reply("Твой город ❓")
    await state.set_state(Form.city)

@router.message(Form.city)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.reply("Знаешь свою норму калорий (число, если да и '0', если нет) ❓")
    await state.set_state(Form.kkal_target)

@router.message(Form.kkal_target)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(kkal_target=message.text)
    data = await state.get_data()
    name = data.get("name")
    city = data.get("city")
    try:
       age = int(data.get("age", 0))
       weight = int(data.get("weight", 0))
       height = int(data.get("height", 0))
       activity_level = int(data.get("activity_level", 0))
       kkal_target = int(message.text, 0)
       users['user_id']['age'] = age
       users['user_id']['weight'] = weight
       users['user_id']['name'] = name
       users['user_id']['city'] = city
       users['user_id']['height'] = height
       users['user_id']['activity'] = activity_level
       if kkal_target == 0:
          kkal_target = round(10 * weight + 6.25 * height - 5 * age + activity_level * 5) #5 ккал за каждую минуту тренировок
          water_target = round(30 * weight + (activity_level / 30) * 500)
          users['user_id']['calorie_goal'] = kkal_target
          users['user_id']['water_goal'] = water_target
       await message.reply(f"""Твой профиль:
       {name} Бальбоа;
    Возраст: {age};
    Вес: {weight};
    Рост: {height};
    Уровень активности: {activity_level};
    🌇 Город: {city};
    🎯 Норма калорий: {kkal_target} ккал; 
    💧 Базовая норма воды: {water_target} мл.

    Можешь приступать к тренировкам, а я все запишу, только держи в курсе 💪🏼""")
    except ValueError as e:
       print(e)
       await message.reply("Ошибка ввода, проверь, что числовые поля заполнены верно.")
    await state.clear()
    time.sleep(3)
    await echo_all(message)


@router.message(Command("start"))
async def show_keyboard(message: Message):
    await message.reply("Ты готов к режиму Рокки?\nВыбери опцию:", reply_markup=keyboard)


@router.callback_query()
async def handle_callback(callback_query, state: FSMContext):
    await callback_query.answer() # подтверждаем нажатие, чтобы у кнопки пропали "часики"
    if callback_query.data == "btn1":
        await callback_query.message.answer("Как тебя зовут ❓") 
        await state.set_state(Form.name)
    elif callback_query.data == "btn2":
        #учет воды
        await callback_query.answer() 
        await cmd_log_water(callback_query.message, state)
    elif callback_query.data == "btn3":
        #учет еды
        await callback_query.answer() 
        await cmd_log_food(callback_query.message, state)
    elif callback_query.data == "btn4":
        #учет тренировок
        await callback_query.answer() 
        await cmd_log_workout(callback_query.message, state)
    elif callback_query.data == "btn5":
        #Статистика
        await callback_query.answer() 
        await cmd_check_progress(callback_query.message)
        

@router.message(Command("log_water"))
async def cmd_log_water(message: Message, state: FSMContext):
    if users['user_id']['water_goal'] == 0:
        await message.answer("Сначала заполни профиль, чтоб рассчитать дневную норму.")
        await message.reply("Как тебя зовут ❓")
        await state.set_state(Form.name)
    else:    
       await message.answer("💧 Учтем воду: сколько ты выпил за время с крайнего учета?")
       await state.set_state(Form.water_log)

@router.message(Form.water_log)
async def water_calc(message: Message, state: FSMContext):
    await state.update_data(water_log=message.text)
    try:
       current_water = int(message.text)
    except ValueError as e:
       print(e)
       await message.reply("Ошибка ввода, проверь, что числовые поля заполнены верно.")
       await state.set_state(Form.water_log)
    if isinstance(current_water, int):
        users['user_id']['current_levels']['water_level'] += current_water
        current_water = users['user_id']['current_levels']['water_level']
        water_goal = users['user_id']['water_goal']
        delta = water_goal - current_water
        if delta > 0:
           await message.answer(f"За сегодня ты уже выпил {current_water} мл, осталось выпить {water_goal - current_water} мл.")
        else:
           await message.answer(f"За сегодня ты уже выпил {current_water} мл, цель перевыполнена на {abs(delta)} мл - ты настоящий Рокки!")
    await state.clear()
    await echo_all(message)


@router.message(Command("log_food"))
async def cmd_log_food(message: Message, state: FSMContext):
    if users['user_id']['calorie_goal'] == 0:
        await message.answer("Сначала заполни профиль, чтоб рассчитать дневную норму.")
        await message.reply("Как тебя зовут ❓")
        await state.set_state(Form.name)
    else:    
       await message.answer("Учтем калорийность приемов пиши: введи название продукта (по-английски, если не знаешь калоррийность) ❓")
       await state.set_state(Food_states.food_name)

@router.message(Food_states.food_name)
async def food_name(message: Message, state: FSMContext):
    await state.update_data(food_name=message.text)
    await message.answer("🔎 Ищу продукты...")
    try:
       food_info = await get_food_calories(message.text)
       if food_info is not None:
          await message.answer("🥙 Нашел похожие продукты (но это не точно):")
          for i in range(len(food_info)):
             product_name = food_info.get(str(i+1), {}).get('name')
             product_kkal = food_info.get(str(i+1), {}).get('calories', 0)
             await message.answer(f"{i+1}. '{product_name}' - {product_kkal} ккал")
       else:
           await message.answer("Ничего не нашел :(")
       await message.answer("Введи калорийность на 100 грамм ❓")
       await state.set_state(Food_states.food_kkal)
    except Exception as e:
        print(e)
        await message.reply("Ошибка")
        await state.set_state(Food_states.food_name)

@router.message(Food_states.food_kkal)
async def set_food_kkal(message: Message, state: FSMContext):
    food_kkal=message.text
    data = await state.get_data()
    await state.update_data(food_kkal=food_kkal)
    await message.answer("Введи вес порции в граммах (в сухом/сыром виде) ❓")
    await state.set_state(Food_states.food_weight)

@router.message(Food_states.food_weight)
async def food_result(message: Message, state: FSMContext):
    food_weight=message.text
    await state.update_data(food_weight=message.text)
    data = await state.get_data()
    product_name = data.get("food_name")
    prodact_kkal = float(data.get("food_kkal", 0))
    result = prodact_kkal * float(food_weight)/100
    users['user_id']['current_levels']['kkal_level'] += result
    current_kkal = users['user_id']['current_levels']['kkal_level']
    delta = users['user_id']['calorie_goal'] - current_kkal
    await message.answer(f"✏️ Записал {food_weight} грамм продукта {product_name} на {result} калорий.")
    if delta > 0: await message.answer(f"За сегодня ты уже съел {current_kkal} калорий, осталось до цели {delta} калорий.")
    else: await message.answer(f"За сегодня ты уже съел {current_kkal} калорий, норма перевыполнена на {abs(delta)} калорий - остановись 📛")
    await state.clear()
    time.sleep(3)
    await echo_all(message)


@router.message(Command("log_workout"))
async def cmd_log_workout(message: Message, state: FSMContext):
    if users['user_id']['calorie_goal'] == 0:
        await message.answer("Сначала заполни профиль, чтоб рассчитать дневную норму.")
        await message.reply("Как тебя зовут ❓")
        await state.set_state(Form.name)
    else:   
        await message.answer("""Напиши через пробел в одну строку тип тренировки цифрой из списка: 
                             1. Интенсивное кардио, 
                             2. Спортзал, 
                             3. Прогулка.
                             И время тренировки в минутах❓""")
        await state.set_state(Form.activity_log)

@router.message(Form.activity_log)
async def calculate_workout(message: Message, state: FSMContext):
    await state.update_data(activity_log=message.text)
    activity_types = { #базовые условные показатели для активностей - придумал
        "1": {"name": "Кардио", "kkal_per30": 150, "water_per30": 250}, 
        "2":  {"name": "Спортзал", "kkal_per30": 100, "water_per30": 200}, 
        "3":  {"name": "Прогулка", "kkal_per30": 50, "water_per30": 100}
    }
    my_message = message.text.split()
    if len(my_message) == 2:
        try:
           water_loss = int(activity_types[my_message[0]]["water_per30"]*(int(my_message[1])/30))
           kkal_loss = int(activity_types[my_message[0]]["kkal_per30"]*(int(my_message[1])/30))
           users["user_id"]["current_levels"]["water_level"] -= water_loss
           users["user_id"]["current_levels"]["kkal_level"] -= kkal_loss
           await message.answer(f"Отлично, ты сжег {kkal_loss} калорий и сегодня можешь позволить себе больше, но восполни {water_loss} мл воды 🏃🏻‍♂️")
        
        except Exception as e:
            print(e)
            await message.reply("Ошибка ввода!")
    else: await message.reply("Ошибка ввода!")
    await state.clear()
    time.sleep(3)
    await echo_all(message)


@router.message(Command("check_progress"))
async def cmd_check_progress(message: Message):
    await message.answer(f"""
        {users['user_id']['name']} Бальбоа:
        
    Возраст: {users['user_id']['age']};
    Вес: {users['user_id']['weight']};
    Рост: {users['user_id']['height']};
    Уровень активности: {users['user_id']['activity']};
    🌇 Город: {users['user_id']['city']};
    🎯 Норма калорий: {users['user_id']['calorie_goal']} ккал, 
    💧 Базовая норма воды: {users['user_id']['water_goal']} мл""")
    
    current_kkal = users['user_id']['current_levels']['kkal_level']
    delta_kkal = users['user_id']['calorie_goal'] - current_kkal
    current_water = users['user_id']['current_levels']['water_level']
    delta_water = users['user_id']['water_goal'] - current_water
    if delta_kkal > 0: await message.answer(f"За сегодня ты уже съел {max(current_kkal, 0)} калорий, осталось до цели {delta_kkal} калорий.")
    else: await message.answer(f"За сегодня ты уже съел {max(current_kkal, 0)} калорий, норма перевыполнена на {abs(delta_kkal)} калорий - остановись 📛")
    if delta_water > 0: await message.answer(f"За сегодня ты уже выпил {max(current_water, 0)} мл, осталось выпить {delta_water} мл.")
    else: await message.answer(f"За сегодня ты уже выпил {max(current_water, 0)} мл, цель перевыполнена на {abs(delta_water)} мл - ты настоящий Рокки!")

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply("Могу ответить на команды /start, /set_profile и /help")

@router.message()
async def echo_all(message: Message):
    await message.answer("Выберите опцию:", reply_markup=keyboard)