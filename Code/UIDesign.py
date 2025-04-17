class UIDesign:

    # =============================================================
    # 全局通用样式设定
    # =============================================================
    # 全局背景样式
    BG_BLACK = "background-color: black;"

    # 默认按钮样式（适用于大部分 QPushButton 控件）
    BUTTON_STYLE = """
    QPushButton {
        background-color: white; 
        color: black; 
        border-radius: 10px;
        font-size: 20px;
    }
    QPushButton:hover {
        background-color: #dddddd;
    }
    """

    # 动态生成按钮样式，可通过参数定制
    def get_button_style(bg_color="white", text_color="black", border_radius=10, font_size=20, hover_bg="#dddddd"):
        return f"""
        QPushButton {{
            background-color: {bg_color}; 
            color: {text_color}; 
            border-radius: {border_radius}px;
            font-size: {font_size}px;
        }}
        QPushButton:hover {{
            background-color: {hover_bg};
        }}
        """

    # 标签统一样式（适用于 QLabel）
    LABEL_STYLE = """
    QLabel {
        color: white;
        font-size: 20px;
    }
    """

    # 输入框统一样式（适用于 QLineEdit）
    LINE_EDIT_STYLE = """
    QLineEdit {
        background-color: #222;
        color: white;
        font-size: 16px;
        border-radius: 5px;
        padding: 5px;
    }
    """

    # 文本编辑控件统一样式（适用于 QTextEdit）
    TEXT_EDIT_STYLE = """
    QTextEdit {
        background-color: #222;
        color: white;
        font-size: 16px;
        border-radius: 5px;
        padding: 5px;
    }
    """

    # 下拉框统一样式（适用于 QComboBox）
    COMBO_BOX_STYLE = """
    QComboBox {
        background-color: #222;
        color: white;
        font-size: 16px;
        border-radius: 5px;
        padding: 5px;
    }
    QComboBox:hover {
        background-color: #333;
    }
    """

    # 工具按钮统一样式（适用于 QToolButton）
    TOOL_BUTTON_STYLE = """
    QToolButton {
        background-color: transparent;
        color: white;
        font-size: 16px;
    }
    QToolButton:hover {
        color: #dddddd;
    }
    """

    # 统一框架样式（适用于 QFrame）
    FRAME_STYLE = """
    QFrame {
        background-color: #141414;
        border-radius: 10px;
    }
    """

    # =============================================================
    # CalendarPage 专用样式设定
    # =============================================================
    CALENDAR_STYLE = """
    QCalendarWidget {
        background-color: #1C1C1E;
        color: #FFFFFF;
        border: none;
        font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif;
        font-size: 18px;
        font-weight: bold;
    }
    QCalendarWidget QAbstractItemView {
        background-color: #1C1C1E;
        font-size: 18px;
        border-radius: 5px;
        border: none;
    }
    QCalendarWidget QToolButton {
        color: #FFFFFF;
        background: transparent;
        border: none;
    }
    QCalendarWidget QMenu {
        background-color: #2C2C2E;
        color: white;
        font-size: 16px;
        border: 1px solid #3A3A3C;
    }
    QCalendarWidget QMenu::item {
        padding: 6px 20px;
        background-color: transparent;
    }
    QCalendarWidget QMenu::item:selected {
        color: white;
    }
    QCalendarWidget QSpinBox {
        background-color: #1C1C1E;
        color: #FFFFFF;
        border: 1px solid #3A3A3C;
        border-radius: 5px;
        font-size: 16px;
        padding: 2px 6px;
    }
    QSpinBox::up-button, QSpinBox::down-button {
        image: none;
        width: 0px;
        height: 0px;
    }
    QToolButton::menu-indicator {
        image: none;
        width: 0px;
        height: 0px;
    }
    QCalendarWidget QWidget#qt_calendar_navigationbar {
        background-color: #1C1C1E;
        border-radius: 5px;
    }
    QCalendarWidget QToolButton#qt_calendar_prevmonth {
        qproperty-icon: none;
        text-align: center;
        font-size: 20px;
        color: white;
        background-color: transparent;
        border: none;
        min-width: 30px;
        padding-left: 10px;
    }
    QCalendarWidget QToolButton#qt_calendar_nextmonth {
        qproperty-icon: none;
        text-align: center;
        font-size: 20px;
        color: white;
        background-color: transparent;
        border: none;
        min-width: 30px;
        padding-right: 10px;
    }
    QCalendarWidget QAbstractItemView {
        background-color: #1C1C1E;
        color: white;
        font-size: 18px;
        font-weight: bold;
        border-radius: 5px;
        border: none;
        gridline-color: #3A3A3C;
    }
    """

    CALENDAR_DETAIL_STYLE = "background-color: #2a2a2a;"
    CALENDAR_SCROLL_STYLE = "background-color: #3a3a3a;"

    # =============================================================
    # TimeWindow 专用样式设定
    # =============================================================
    TIMEWINDOW_MAIN_FRAME_STYLE = """
    QFrame {
        background-color: black;
        border: 3px groove #93DEF9;
    }
    """
    TIMEWINDOW_CLOSE_BUTTON_STYLE = """
    QPushButton {
        background-color: white;
        color: black;
        border-radius: 20px;
        font-size: 15px;
    }
    QPushButton:hover {
        background-color: #dddddd;
    }
    """
    TIMEWINDOW_BUTTON_STYLE = """
    QPushButton {
        background-color: white;
        color: black;
        border-radius: 5px;
        font-size: 16px;
    }
    QPushButton:hover {
        background-color: #dddddd;
    }
    """

    # =============================================================
    # WheelPicker 专用样式设定
    # =============================================================
    WHEELPICKER_STYLE = "background-color: black; border: none;"
    WHEELPICKER_LABEL_BASE = "background-color: black;"

    # =============================================================
    # TimerPage 专用样式设定
    # =============================================================
    TIMERPOPUP_STYLE = "background-color: white; color: black;"
    TIMERPAGE_BG_STYLE = "background-color: black;"
    TIMERPAGE_LINEEDIT_STYLE = """
    QLineEdit {
        background-color: #222;
        color: white;
        font-size: 16px;
        border-radius: 5px;
        padding: 5px;
    }
    """
    TIMERPAGE_TIMELABEL_STYLE = "color: white;"
    TIMERPAGE_ENDTIMELABEL_STYLE = "color: #aaaaaa; font-size: 16px;"
    TIMERPAGE_STARTBUTTON_STYLE = """
    QPushButton {
        background-color: #007A00;
        color: white;
        font-size: 16px;
        border-radius: 8px;
    }
    QPushButton:hover {
        background-color: #009900;
    }
    """
    TIMERPAGE_STOPBUTTON_STYLE = """
    QPushButton {
        background-color: #990000;
        color: white;
        font-size: 16px;
        border-radius: 8px;
    }
    QPushButton:hover {
        background-color: #cc0000;
    }
    """
    TIMERPAGE_CANCELBUTTON_STYLE = """
    QPushButton {
        background-color: #333;
        color: white;
        font-size: 16px;
        border-radius: 8px;
    }
    QPushButton:hover {
        background-color: #555;
    }
    """

    # =============================================================
    # StopWatchPage 专用样式设定
    # =============================================================
    STOPWATCH_BG_STYLE = "background-color: black;"
    STOPWATCH_TIME_LABEL_STYLE = "color: white;"
    STOPWATCH_LAP_LABEL_STYLE = "color: white; font-size: 20px;"
    STOPWATCH_LAP_LIST_STYLE = """
    background-color: black;
    color: white;
    font-size: 20px;
    border: none;
    """
    STOPWATCH_LEFT_BUTTON_STYLE = """
    QPushButton {
        background-color: #333;
        color: white;
        font-size: 18px;
        border-radius: 10px;
    }
    QPushButton:hover {
        background-color: #555;
    }
    """
    STOPWATCH_RIGHT_BUTTON_START_STYLE = """
    QPushButton {
        background-color: #007A00;
        color: white;
        font-size: 18px;
        border-radius: 10px;
    }
    QPushButton:hover {
        background-color: #009900;
    }
    """
    STOPWATCH_RIGHT_BUTTON_STOP_STYLE = """
    QPushButton {
        background-color: #990000;
        color: white;
        font-size: 18px;
        border-radius: 10px;
    }
    QPushButton:hover {
        background-color: #cc0000;
    }
    """

    # =============================================================
    # Alarm 模块专用样式设定（包括 AlarmPopup、AlarmItem、AlarmEditDialog、AlarmClockWidget）
    # =============================================================
    ALARMPOPUP_STYLE = "background-color: white; color: black;"
    ALARMITEM_FRAME_STYLE = """
    QFrame {
        border-radius: 10px;
        background-color: #141414;
    }
    """
    ALARMITEM_TIME_LABEL_STYLE = "font-size: 24px; color: #bbb; background-color: #141414;"
    ALARMITEM_LABEL_LABEL_STYLE = "font-size: 14px; color: #bbb; background-color: #141414;"
    ALARMITEM_CHECKBOX_STYLE = """
    QCheckBox {
        background-color: #141414;
        color: #bbb;
        font-size: 14px;
    }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
    }
    """
    ALARMITEM_DELETEBUTTON_STYLE = """
    QPushButton {
        background-color: #141414;
        color: white;
        border-radius: 4px;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: #777;
    }
    """
    ALARMEDITDIALOG_STYLE = "background-color: black; color: white;"
    ALARMEDITDIALOG_LINEEDIT_STYLE = "background-color: #222; color: white; font-size: 14px;"
    ALARMEDITDIALOG_BUTTON_STYLE = """
    QPushButton {
        background-color: #333;
        color: white;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #555;
    }
    """
    ALARMCLOCK_BG_STYLE = "background-color: black;"
    ALARMCLOCK_EDIT_BUTTON_STYLE = """
    QPushButton {
        background-color: #444;
        color: white;
        border-radius: 5px;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: #666;
    }
    """
    ALARMCLOCK_ADD_BUTTON_STYLE = """
    QPushButton {
        background-color: #333;
        color: white;
        font-size: 16px;
        border-radius: 8px;
    }
    QPushButton:hover:enabled {
        background-color: #555;
    }
    QPushButton:disabled {
        background-color: #555;
        color: #aaa;
    }
    """

    # =============================================================
    # ToDoPage 专用样式设定
    # =============================================================
    LEFT_PANEL_BG = "background-color: #2f2f2f;"  # 待办页面左侧面板背景
    PAGE_BG = "background-color: #4f4f4f;"  # 待办页面整体背景（Recent、Collection、All、Future、Category 等）
    TOP_BUTTON_STYLE = """
    QPushButton {
        background-color: #444444;
        color: white;
        border-radius: 5px;
        font-size: 16px;
    }
    QPushButton:checked {
        background-color: #3399FF;
    }
    QPushButton:hover {
        background-color: #666666;
    }
    """

    TODO_ADD_STYLE = """
    QPushButton {
        background-color: #ccc;
        color: black;
        border-radius: 5px;
        }
    QPushButton:hover {
     background-color: #eee;
    }
    
    """

    TODO_CARD_FRAME_STYLE = """
    QFrame {
        background-color: #141414;
        border-radius: 10px;
    }
    """
    CARD_COLLECTION_BUTTON_STYLE = """
    QPushButton {
        background-color: #333;
        color: #fff;
        border-radius: 3px;
        font-size: 10px;
    }
    QPushButton:hover {
        background-color: #666;
    }
    """
    CARD_DELETE_BUTTON_STYLE = """
    QPushButton {
        background-color: transparent;
        color: #fff;
        font-size: 12px;
    }
    QPushButton:hover {
        color: red;
    }
    """
    EDIT_DIALOG_BUTTON_STYLE = """
    QPushButton {
        background-color: #666;
        color: white;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #888;
    }
    """

    def get_category_button_style(color: str) -> str:
        return f"""
        QPushButton {{
            background-color: {color};
            color: white;
            border-radius: 5px;
            font-size: 12px;
            padding: 4px 8px;
        }}
        QPushButton:hover {{
            font-size: 20px;
            font-weight: bold;
        }}
        QPushButton:checked {{
            font-size: 20px;
            font-weight: bold;
        }}
        """

    # =============================================================
    # Exp_Dialog 专用样式设定
    # =============================================================
    DIALOG_BACK = "background-color: #333333;"
    DIALOG_STYLE = "background-color: #4c4c4c; color: #ffffff;"
    DIALOG_INPUT_STYLE = "background-color: #333333; color: #ffffff; border-radius: 3px;"
    DIALOG_BUTTON_STYLE = """
    QPushButton {
        background-color: #666666;
        color: white;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #888888;
    }
    """

    # =============================================================
    # Exp_Pages 专用样式设定
    # =============================================================
    # TodayPage 样式配置
    TODAY_PAGE_BG = "background-color: #555555;"
    TODAY_DAILY_BOX_STYLE = "background-color: #444444; border-radius: 5px;"
    TODAY_LABEL_STYLE_SMALL = "color: white; font-size: 14px;"
    TODAY_BTN_EDIT_BUDGET_STYLE = """
    QPushButton {
        background-color: #555555;
        color: white;
        border-radius: 5px;
        font-size: 12px;
    }
    QPushButton:hover {
        background-color: #777777;
    }
    """
    TODAY_BOTTOM_FRAME_STYLE = "background-color: #666666; border-radius: 5px;"
    TODAY_TITLE_LABEL_STYLE = "color: white; font-size: 20px;"

    TODAY_CONTENT_BACK_STYLE = "background-color: #575757;"
    TODAY_HEADER_LABEL_STYLE = "color: white; font-size: 15px;"
    TODAY_SCROLL_AREA_STYLE = "background-color: transparent; border: none;"

    # AllPage 样式配置
    ALL_PAGE_BG = "background-color: #555555;"
    ALL_TITLE_LABEL_STYLE = "color: white; font-size: 24px;"
    ALL_SCROLL_AREA_STYLE = "background-color: transparent; border: none;"

    # SummaryPage 样式配置
    SUMMARY_PAGE_BG = "background-color: #555555;"
    SUMMARY_COMBO_STYLE = """
    QComboBox {
        background-color: transparent;
        color: white;
        font-size: 25px;
        border-radius: 5px;
    }
    QComboBox:hover {
        background-color: #444444;
    }
    """
    SUMMARY_INFOR_FRAME_STYLE = "background-color: #444444; border-radius: 5px;"
    SUMMARY_PERIOD_COMBO_STYLE = """
    QComboBox {
        background-color: transparent;
        color: white;
        font-size: 20px;
        border-radius: 5px;
    }
    QComboBox:hover {
        background-color: #444444;
    }
    """
    SUMMARY_LABEL_INFO_STYLE = "color: white; font-size: 14px;"
    SUMMARY_PIE_FRAME_STYLE = "background-color: transparent;"
    SUMMARY_BAR_FRAME_STYLE = "background-color: transparent;"

    PIE_LABELS_STYLE = """
    QScrollArea{
        background-color: transparent;
        border: white;
        border-radius: 5px;
        border-width: 10px;
    """

    # CategoryFilterPage 样式配置
    CATEGORY_PAGE_BG = "background-color: #555555;"
    CATEGORY_TITLE_LABEL_STYLE = "color: white; font-size: 24px;"
    CATEGORY_BTN_ADD_STYLE = """
    QPushButton {
        background-color: #333333;
        color: white;
        border-radius: 5px;
        font-size: 14px;
        padding: 4px 10px;
    }
    QPushButton:hover {
        background-color: #555555;
    }
    """
    CATEGORY_BTN_DELETE_STYLE = """
    QPushButton {
        background-color: #aa0000;
        color: white;
        border-radius: 5px;
        font-size: 14px;
        padding: 4px 10px;
    }
    QPushButton:hover {
        background-color: #cc0000;
    }
    """
    CATEGORY_SCROLL_AREA_STYLE = "background-color: transparent; border: none;"

    # =============================================================
    # Exp_Widgets 专用样式设定
    # =============================================================
    # CategoryButton 样式
    CATEGORYBUTTON_DEFAULT_STYLE = """
    QWidget {
        background-color: #444444;
        color: white;
        border-radius: 5px;
        font-size: 14px;
    }
    """
    CATEGORYBUTTON_HOVER_STYLE = """
    QWidget {
        background-color: #666666;
        color: white;
        border-radius: 5px;
        font-size: 14px;
    }
    """
    CATEGORYBUTTON_DELETE_BUTTON_STYLE = """
    QPushButton {
        background-color: transparent;
        color: #fff;
        font-size: 12px;
        border: none;
    }
    QPushButton:hover {
        color: #ffdddd;
        background-color: transparent;
    }
    """

    # ExpenseCard 样式
    EXPENSECARD_DEFAULT_STYLE = "background-color: #4a4a4a; border-radius: 5px;"
    EXPENSECARD_HOVER_STYLE = "background-color: #4f4f4f; border-radius: 5px;"
    EXPENSECARD_LABEL_STYLE = "background-color: transparent; color: #fff; font-size: 12px;"
    EXPENSECARD_DELETE_BUTTON_STYLE = """
    QPushButton {
        background-color: transparent;
        color: #fff;
        font-size: 12px;
        border-radius: 3px;
    }
    QPushButton:hover {
        background-color: transparent;
        color: #fff;
        font-size: 15px;
        border-radius: 3px;
    }
    """

    # MonthSummaryWidget 样式
    MONTHSUMMARY_FRAME_STYLE = "background-color: #444444; border-radius: 5px;"
    MONTHSUMMARY_LABEL_STYLE = "color: white; font-size: 14px;"
    MONTHSUMMARY_DETAIL_FRAME_STYLE = "background-color: #575757; border-radius: 5px;"
    MONTHSUMMARY_BTN_DETAIL_STYLE = """
    QPushButton {
        background-color: #666666;
        color: white;
        border-radius: 5px;
        font-size: 12px;
    }
    QPushButton:hover {
        background-color: #888888;
    }
    """

    # =============================================================
    # ExpenditurePage 专用样式设定
    # =============================================================
    EXP_LEFT_PANEL_BG = "background-color: #2f2f2f;"
    EXP_CATEGORY_LABEL_STYLE = "color: white; font-size: 18px;"
    EXP_ADD_BUTTON_STYLE = """
    QPushButton {
        background-color: #555555; 
        color: white; 
        border-radius: 5px; 
        font-size: 12px;
    }
    QPushButton:hover {
        background-color: #5e5e5e;
    }
    QPushButton:disabled {
        color: #555555;
        background-color: #444444;}
    """

    EXP_DELETE_BUTTON_STYLE = """
    QPushButton {
        background-color: #aa0000; 
        color: white; 
        border-radius: 5px; 
        font-size: 12px;
    }
    QPushButton:hover {
        background-color: #cc0000;
    }
    """

    EXP_ALL_ADD_BUTTON_STYLE = """
        QPushButton {
            background-color: #444444; 
            color: white; 
            border-radius: 5px; 
            font-size: 16px;
        }
        QPushButton:hover {
            background-color: #555555;
        }
        QPushButton:disabled {
            color: #555555;
            background-color: #444444;}
        """

    EXP_ALL_DELETE_BUTTON_STYLE = """
        QPushButton {
            background-color: #aa0000; 
            color: white; 
            border-radius: 5px; 
            font-size: 16px;
        }
        QPushButton:hover {
            background-color: #cc0000;
        }
        """
    EXP_CATEGORY_SCROLL_STYLE = "background: transparent; border: none;"
    EXP_PAGES_WIDGET_STYLE = "background-color: #4c4c4c;"

