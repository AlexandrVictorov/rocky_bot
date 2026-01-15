from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    name = State()
    age = State()
    weight = State()
    height = State() 
    activity_level = State()
    city = State()
    kkal_target = State()
    water_log = State() #Ожидание количества выпитой воды
    activity_log = State()

class Food_states(StatesGroup):
    food_name = State()
    food_kkal = State()
    food_weight = State()

