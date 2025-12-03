import flet as ft
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import glob

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

#Google Drive APIのスコープ
def get_drive(token_file = None):
    creds = None

    #既存トークンファイルを読み込む
    if token_file and os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        except:
            creds = None

    #トークンの新規作成
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        if not creds:
            if not os.path.exists("credentials.json"):
                print("エラー：credentials.jsonが見つかりません。")
                return None, None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",SCOPES
            )
            creds = flow.run_local_server(port=0)

    return build('drive', 'v3', credentials=creds),creds



def Get_searching(page: ft.Page):
    accounts_map = {} #メールアドレス:ファイル名

    def load_account():
        accounts_map.clear()
        token_files = glob.glob("token*.json")

        for t_file in token_files:
            try:
                srv, _ = get_drive(t_file)
                if srv:
                    email = srv.about().get(fields="user").execute()['user']['emailAddress']
                    accounts_map[email] = t_file
            except:
                pass
    
    load_account()

    #アカウント選択用ドロップダウン
    accounts_dropdown = ft.Dropdown(
        label = "アカウント選択",
        width = 400,
        options = [ft.dropdown.Option(email) for email in accounts_map.keys()]+ [ft.dropdown.Option("CREATE NEW")],
        value = list(accounts_map.keys())[0] if accounts_map else "CREATE NEW",
        label_style = ft.TextStyle(font_family="MyFont", color="white"),
        color = "white",
        border_color = "white",
    )


    search_field = ft.TextField(
        label = "Google Drive内を検索",
        hint_text = "ファイル名、キーワードなど",
        width = 400,
        prefix_icon = ft.Icons.SEARCH,
        label_style = ft.TextStyle(font_family="MyFont", color="white"),
        color = "white",
    )

    results_list = ft.ListView(
        expand = True,
        spacing = 10,
        padding = 10,
    )

    def run_search(e):
        keyword = search_field.value.strip()
        selected_email = accounts_dropdown.value
        if not keyword or not selected_email:
            return
        
        #検索中UI
        results_list.controls.clear()
        results_list.controls.append(ft.Text("ファイルを検索中・・・"))
        results_list.update()

        service = None

        #分岐処理
        if selected_email == "CREATE NEW":
            service, new_creds = get_drive(token_file=None)
            if service:
                email = service.about().get(fields="user").execute()['user']['emailAddress']
                new_filename = f"token_{email}.json"
                with open(new_filename, "w") as f:
                    f.write(new_creds.to_json())

                accounts_map[email] = new_filename
                accounts_dropdown.options = [ft.dropdown.Option(e) for e in accounts_map.keys()] + [ft.dropdown.Option("CREATE NEW")]
                accounts_dropdown.value = email
                accounts_dropdown.update()
        else:
            target_file = accounts_map.get(selected_email)
            service, _ = get_drive(token_file=target_file)


        if not service:
            results_list.controls.clear()
            results_list.controls.append(ft.Text("エラーが発生しました", color="red", selectable=True))
            results_list.update()
            return
        
        try:
            query = (
                f"(name contains '{keyword}' or fullText contains '{keyword}')"
                " and trashed = false"
            )

            results = service.files().list(
                q = query,
                pageSize = 20,
                fields = "nextPageToken, files(id, name, mimeType, webViewLink, iconLink)"
            ).execute()

            items = results.get("files", [])

            results_list.controls.clear()
            
            if not items:
                results_list.controls.append(ft.Text("該当するファイルは見つかりませんでした。", color="white"))
            else:
                for item in items:
                    # アイコンの出し分け
                    icon_data = ft.Icons.INSERT_DRIVE_FILE
                    if "pdf" in item['mimeType']:
                        icon_data = ft.Icons.PICTURE_AS_PDF
                    elif "word" in item['mimeType']:
                        icon_data = ft.Icons.DESCRIPTION
                    elif "sheet" in item['mimeType'] or "excel" in item['mimeType']:
                        icon_data = ft.Icons.TABLE_CHART

                    # リストに追加
                    results_list.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(icon_data, color="white"),
                            title=ft.Text(item['name'], color="white", weight="bold"),
                            subtitle=ft.Text(f"ID: {item['id']}", color="grey", size=12),
                            # クリックしたらブラウザで開く機能
                            on_click=lambda e, link=item['webViewLink']: page.launch_url(link)
                        )
                    )

        except Exception as error:
            print(f"An error occurred: {error}")
            results_list.controls.clear()
            results_list.controls.append(ft.Text(f"検索エラーが発生しました: {error}", color="red"))

        results_list.update()


    search_button = ft.ElevatedButton(
        "検索",
        icon = ft.Icons.SEARCH,
        on_click = run_search,
        style = ft.ButtonStyle(
            bgcolor = "blue",
            color = "white",
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=20
        )
    )

    return ft.Container(
        padding = 20,
        content = ft.Column(
            controls = [
                ft.Text("Drive検索", size=24, font_family="MyFont"),
                ft.Divider(),
                accounts_dropdown,
                ft.Row(
                    controls = [search_field, search_button],
                    alignment = ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                
                ft.Divider(color="grey"),
                ft.Text("検索結果", size=16, font_family="MyFont"),
                ft.Container(
                    content = results_list,
                    expand = True, # Column内で広げる
                    border = ft.border.all(1, "grey"),
                    border_radius = 10,
                    padding = 10
                )
            ],
        ),
        expand = True,
        alignment = ft.alignment.top_left
    )