import flet as ft
from openai import OpenAI
from dotenv import load_dotenv
import os

import setting
import searching

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


def main(page: ft.Page):
    page.title = "Rephraseアプリ"
    page.window_width = 600
    page.window_height = 400
    page.window_left = 100
    page.window_top = 100
    page.bgcolor = "#525252"

    page.fonts = {
        "MyFont": "/fonts/NotoSansJP-Regular.ttf"
    }
    page.theme = ft.Theme(font_family="MyFont")

    API_config = {
        "model":"gpt-4o"
    }

    #会話の保持
    chat_history = ft.ListView(
        expand = True,
        spacing = 10,
        padding = 10,
        auto_scroll = True
    )

    input_field = ft.TextField(
        label = "Sentence to rephrase", 
        autofocus = True, 
        multiline = True, 
        width = 500,
        text_style = ft.TextStyle(font_family="MyFont", color="white", size=16)
    )
    
    #プロンプトの入力欄
    prompt_field = ft.TextField(label="Orders", 
        width = 500, 
        text_style = ft.TextStyle(font_family="MyFont", color="white", size=16)
    )

    def handle_click(e):
        user_input =input_field.value.strip()
        user_prompt = prompt_field.value.strip()

        if user_input and user_prompt:
            #入力履歴への追加
            chat_history.controls.append(ft.Text(f"元の文章：{user_input}",color="white",font_family="MyFont"))
            chat_history.controls.append(ft.Text(f"AIへの指示：{user_prompt}",color="white",font_family="MyFont"))

            #最終的なプロンプト
            full_prompt = f"{user_prompt}\n\n[元の文章]:\n{user_input}"

            #APIの呼び出し
            response =client.chat.completions.create(
                model=API_config["model"],
                messages=[
                    {"role": "system","content": f"あなたはユーザーの指示に従って文章作成支援を行うAIです。"},
                    {"role":"user","content":full_prompt}
                ]
            )

            output_content = response.choices[0].message.content
   
            chat_history.controls.append(ft.Text(f"AI：{output_content}",color="white",font_family="MyFont",selectable=True))  
            chat_history.controls.append(ft.Divider(color="#CECECE"))         
            
            input_field.value = ""
            prompt_field.value = ""
            page.update()

    button = ft.ElevatedButton(
        "Rephrase", 
        on_click=handle_click,
        style=ft.ButtonStyle(
            bgcolor="blue",
            color="white",
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=15
        )
    )

    chat_view = ft.Container(
        padding = 20,
        content = ft.Column(
            controls = [
                ft.Text("AI添削/翻訳", size=24, font_family="MyFont"),
                ft.Divider(),
                input_field,
                prompt_field,
                button,
                ft.Divider(),
                chat_history
            ]
        ),
        expand = True,
    )

    def handle_config_change(key, value):
        API_config[key] = value
        print(f"Config changed:{key}={value}")

        # チャット履歴にモデル変更を記録
        chat_history.controls.append(
            ft.Text(
                f"AIモデルを {value} に変更しました", 
                color="yellow", 
                size=12,
                italic=True
            )
        )
        chat_history.controls.append(ft.Divider(color="#CECECE", height=1))
        page.update()


    setting_view = setting.Get_setting(API_config, handle_config_change)
    searching_view = searching.Get_searching(page)
    
    
    content_area = ft.Container(
        content = chat_view, 
        expand = True, 
    )

    #ナビゲーションレール
    def nav_change(e):
        selected_index = e.control.selected_index
        if selected_index == 0:
            content_area.content = chat_view
        if selected_index == 1:
            content_area.content = searching_view
        if selected_index == 2:
            content_area.content = setting_view
        page.update()

    def nav_toggle(e):
        rail.visible = not rail.visible
        ft.VerticalDivider.visible = not ft.VerticalDivider.visible
        page.update()

    page.appbar = ft.AppBar(
        # メニューアイコン
        leading=ft.IconButton(
            icon=ft.Icons.MENU, 
            on_click=nav_toggle, 
            tooltip="メニューを開閉"
        ),
        leading_width=40,
        
        # タイトル
        title=ft.Row(
            controls=[
                ft.Image(src="/images/app_logo.png", width=28, height=28),
                ft.Text("Rephraseアプリ", size=16),
            ],
        ),
        bgcolor="blue",
        color="white"
    )

    rail = ft.NavigationRail(
        selected_index = 0,
        label_type = ft.NavigationRailLabelType.ALL,
        min_width = 100,
        group_alignment = -0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.CHAT_BUBBLE_OUTLINE, 
                selected_icon=ft.Icons.CHAT_BUBBLE, 
                label="AI添削/翻訳",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SEARCH_OUTLINED, 
                selected_icon=ft.Icons.SEARCH, 
                label="検索",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS_OUTLINED, 
                selected_icon=ft.Icons.SETTINGS, 
                label="設定",
            ),
        ],
        on_change=nav_change,
        bgcolor="#444444"
    )

    #画面レイアウト
    layout = ft.Row(
        controls = [
            rail,
            ft.VerticalDivider(width=1, color="white"),
            content_area
        ],
        expand=True
    )

    page.add(layout)

ft.app(target=main, view=ft.WEB_BROWSER, port=8551, assets_dir="assets")