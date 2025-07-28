import streamlit as st
import time

USER_CREDENTIALS = st.secrets["USER_CREDENTIALS"]
api_key = ""

def main():
    st.set_page_config(page_title="動画切り取りアプリ",page_icon="🎬", layout="wide")
    st.title("動画切り取りアプリ✂️")

    # セッションにログイン状態を保持
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    
    try:
        if not st.session_state.logged_in:
            login_area = st.sidebar.empty()
            with login_area.container():
                st.header("ログイン")
                username = st.text_input("ユーザー名")
                password = st.text_input("パスワード", type="password")
                login_button = st.button("ログイン")
                
                # 認証処理
                if login_button:
                    user_info = USER_CREDENTIALS.get(username)
                    if user_info and user_info["password"] == password:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.api_key = user_info["api_key"]
                        login_area.empty() # ログインフォームを消す
                        msg = st.sidebar.empty()
                        msg.success("ログインに成功しました")
                        time.sleep(2)
                        msg.empty()
                        st.rerun() # ログイン状態を反映するために再実行
                    else:
                        st.error("ユーザー名またはパスワードが間違っています")

        else:
            # ログイン後に表示
            user_info = USER_CREDENTIALS[st.session_state.username]
            st.sidebar.markdown(f"👤 **{st.session_state.username}**としてログイン中")
            api_key = st.session_state.api_key
            if st.sidebar.button("ログアウト"):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.api_key = ""
                st.rerun()  # ログアウト後に画面を更新

            # ログイン後のメイン画面
            st.success("ログイン済みです！ここに機能を追加してください。")
        
        st.markdown("test")

    except Exception as e:
        st.error(f"予期せぬエラーが発生しました: {str(e)}")

if __name__ == '__main__':
    main()
