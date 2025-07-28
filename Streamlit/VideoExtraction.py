import streamlit as st

USER_CREDENTIALS = st.secrets["USER_CREDENTIALS"]

def main():
    st.set_page_config(page_title="動画切り取りアプリ",page_icon="🎬", layout="wide")
    st.title("動画切り取りアプリ✂️")
    
    try:
        with st.sidebar:
            st.header("ログイン")
            username = st.text_input("ユーザー名")
            password = st.text_input("パスワード", type="password")
            login_button = st.button("ログイン")
            
            # 認証処理
            if login_button:
                user_info = USER_CREDENTIALS.get(username)
                if user_info and user_info["password"] == password:
                    st.success(f"ログインに成功しました")
                else:
                    st.error("ユーザー名またはパスワードが間違っています")
        
        st.markdown("test")

    except Exception as e:
        st.error(f"予期せぬエラーが発生しました: {str(e)}")

if __name__ == '__main__':
    main()
