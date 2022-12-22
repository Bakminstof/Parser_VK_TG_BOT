from aiogram.dispatcher.filters.state import StatesGroup, State


class States(StatesGroup):
    EditRlsState = State()

    AddMainGroupState = State()
    AddSendToGroupState = State()
    AcceptChangeState = State()

    AddSlotState = State()
    DelSlotState = State()
    DelEmptySlotState = State()
    DelOccupiedSlotState = State()

    CollectSlotState = State()
    SendSlotState = State()

    SubsPaymentState = State()
