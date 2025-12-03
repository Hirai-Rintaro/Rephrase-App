import flet as ft

def Get_setting(config, on_change):
    def handle_model_change(e):
        config["model"] = e.control.value
        on_change("model", e.control.value)

    return ft.Container(
        padding = 20,
        content = ft.Column(
            controls = [
                ft.Text("設定", size=24, font_family="MyFont"),
                ft.Divider(),

                ft.Text("使用するAIモデル", size=16),
                ft.Dropdown(
                    value = config["model"],
                    options = [
                        ft.dropdown.Option("gpt-5-mini"),
                        ft.dropdown.Option("gpt-4o"),
                        ft.dropdown.Option("gpt-4-turbo"),
                        ft.dropdown.Option("gpt-3.5-turbo")
                    ],
                    on_change = handle_model_change,
                    width = 400
                )
            ],
            alignment = ft.MainAxisAlignment.START,
        ),
        expand = True,
    )