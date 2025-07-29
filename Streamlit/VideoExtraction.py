import streamlit as st
import tempfile
import os
import subprocess
import json
import re
import openai
from moviepy.editor import VideoFileClip
import time
# os.system("apt-get update && apt-get install -y ffmpeg")

# ==関数==
# 通知を出す
def notification(text):
    md = f"""
    <script>
    if ("Notification" in window) {{
      if (Notification.permission === "granted") {{
        new Notification('{text}');
      }} else if (Notification.permission !== "denied") {{
        Notification.requestPermission().then(function (permission) {{
          if (permission === "granted") {{
            new Notification('{text}');
          }}
        }});
      }}
    }}
    </script>
    """
    st.markdown(md, unsafe_allow_html=True)
    
# 動画の長さ取得
def get_video_duration(video_path):
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "json", video_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])

# クリップ結合
def concat_clips_ffmpeg(clip_filenames, output_path):
    input_args = []
    for clip in clip_filenames:
        input_args.extend(["-i", clip])

    filter_parts = []
    for i in range(len(clip_filenames)):
        filter_parts.append(f"[{i}:v:0][{i}:a:0]")
    filter_concat = "".join(filter_parts)
    filter_complex = f"{filter_concat}concat=n={len(clip_filenames)}:v=1:a=1[outv][outa]"

    cmd = [
        "ffmpeg",
        "-y",
        *input_args,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "28",
        "-c:a", "aac",
        "-b:a", "192k",
        output_path
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    # st.write(result.stdout)  # ffmpegのログをStreamlitに表示

# 音声有無
def has_audio_stream(video_path):
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "a",
            "-show_entries", "stream=index", "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    return result.stdout.strip() != ""

# セグメント合体
def merge_overlapping_segments(segments, tolerance=0.01):
    sorted_segments = sorted(segments, key=lambda x: x["start"])
    merged = []
    for seg in sorted_segments:
        if not merged:
            merged.append(seg)
        else:
            last = merged[-1]
            if last["end"] + tolerance >= seg["start"]:
                last["end"] = max(last["end"], seg["end"])
            else:
                merged.append(seg)
    return merged

# 動画生成
def process_segment(segments, video_path, file_name):
    duration = get_video_duration(video_path)
    for seg in segments:
        if seg["start"] < 0 or seg["end"] > duration:
            st.error(f"セグメント{seg}が動画尺({duration:.2f}s)を超えています")
            return
        if seg["start"] >= seg["end"]:
            st.error(f"セグメント不正: start({seg['start']}) >= end({seg['end']})")
            return
    segments = merge_overlapping_segments(segments)
    sorted_segments = sorted(segments, key=lambda x: x["start"])
    for i in range(len(sorted_segments) - 1):
        cur = sorted_segments[i]
        next_ = sorted_segments[i + 1]
        if cur["end"] >= next_["start"]:
            st.error(f"セグメント重複: [{cur['start']}〜{cur['end']}] と [{next_['start']}〜{next_['end']}]")
            return
    if not os.path.exists(video_path):
        st.error(f"動画ファイルが見つかりません: {video_path}")
        return

    clip_filenames = []
    for i, seg in enumerate(segments):
        output = f"clip_{i}.mp4"
        clip_filenames.append(output)
        has_audio = has_audio_stream(video_path)
        if has_audio:
            audio_filter = (
                f"[0:a]atrim=start={seg['start']}:end={seg['end']},asetpts=PTS-STARTPTS[a];"
            )
            audio_map = ["-map", "[a]"]
        else:
            audio_filter = ""
            audio_map = []
        filter_complex = (
            f"[0:v]trim=start={seg['start']}:end={seg['end']},setpts=PTS-STARTPTS[v];"
            f"{audio_filter}"
            f"[v]scale=1280:720:force_original_aspect_ratio=decrease,"
            f"pad=1280:720:(ow-iw)/2:(oh-ih)/2[outv]"
        )
        cmd = [
            "ffmpeg", "-y", "-i", video_path,
            "-filter_complex", filter_complex,
            "-map", "[outv]", *audio_map,
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
            "-c:a", "aac", "-b:a", "192k", output
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        # st.write(result.stdout)
    clip_files = [f"clip_{i}.mp4" for i in range(len(segments))]
    output_path = f"{file_name}.mp4"
    concat_clips_ffmpeg(clip_files, output_path)
    for clip in clip_filenames:
        if os.path.exists(clip):
            os.remove(clip)
    return output_path

# 複数動画
def process_multiple_videos(video_configs, video_path, output_file_name):
    output_files = []
    for i, config in enumerate(video_configs):
        st.markdown(f"### 動画{i+1}")
        file_name = f"{output_file_name}{i+1}"
        msg = st.empty()
        msg.info(f"動画{i+1}を生成中…")
        output_file = process_segment(config["segments"], video_path, file_name)
        if output_file and os.path.exists(output_file):
            msg.empty()
            with open(output_file, "rb") as f:
                video_bytes = f.read()

            st.video(video_bytes)

            c1, c2 = st.columns(2)
            # 見出し1
            with c1:
                h1 = config['headline'][0]
                st.write(f"動画{i+1} 見出し1行目:{h1}")
                st.components.v1.html(
                    f"""
                    <div style="display: flex; align-items: center;">
                        <textarea id="text-areaA-{i}" style="width:0;height:0;opacity:0;position:absolute;">{h1}</textarea>
                        <button onclick="copyTextA_{i}()" style="height:28px;font-size:0.9em;">コピー</button>
                        <span id="copy-messageA-{i}" style="color:green; display:none; font-size:0.9em; margin-left:6px;">☑コピー</span>
                    </div>
                    <script>
                    function copyTextA_{i}() {{
                        var text = document.getElementById('text-areaA-{i}').value;
                        navigator.clipboard.writeText(text).then(function() {{
                            document.getElementById('copy-messageA-{i}').style.display = 'inline';
                            setTimeout(function() {{
                                document.getElementById('copy-messageA-{i}').style.display = 'none';
                            }}, 1500);
                        }});
                    }}
                    </script>
                    """,
                    height=38,
                )
            
            # 見出し2
            with c2:
                h2 = config['headline'][1]
                st.write(f"動画{i+1} 見出し2行目:{h2}")
                st.components.v1.html(
                    f"""
                    <div style="display: flex; align-items: center;">
                        <textarea id="text-areaB-{i}" style="width:0;height:0;opacity:0;position:absolute;">{h2}</textarea>
                        <button onclick="copyTextB_{i}()" style="height:28px;font-size:0.9em;">コピー</button>
                        <span id="copy-messageB-{i}" style="color:green; display:none; font-size:0.9em; margin-left:6px;">☑コピー</span>
                    </div>
                    <script>
                    function copyTextB_{i}() {{
                        var text = document.getElementById('text-areaB-{i}').value;
                        navigator.clipboard.writeText(text).then(function() {{
                            document.getElementById('copy-messageB-{i}').style.display = 'inline';
                            setTimeout(function() {{
                                document.getElementById('copy-messageB-{i}').style.display = 'none';
                            }}, 1500);
                        }});
                    }}
                    </script>
                    """,
                    height=38,
                )
                
            st.download_button(
                label=f"動画{i+1}をダウンロード",
                data=video_bytes,
                file_name=output_file,
                mime="video/mp4"
            )
            
            output_files.append(output_file)
        else:
            msg.empty()
            st.error(f"動画{i+1}の生成に失敗")
    notification("全ての動画生成が完了しました！")
    return output_files

# GPT出力からJSON抽出
def extract_json(gpt_output):
    match = re.search(r"(\[\s*{.*}\s*\])", gpt_output, re.DOTALL)
    if not match:
        st.error("JSONブロックが見つかりませんでした")
        st.write(gpt_output)
        return None
    raw_json = match.group(1)
    cleaned_json = (
        raw_json.replace("“", '"').replace("”", '"')
        .replace("‘", "'").replace("’", "'").strip()
    )
    try:
        return json.loads(cleaned_json)
    except json.JSONDecodeError as e:
        st.error("JSONのパースエラー")
        st.write(cleaned_json)
        return None

# JSON部分だけ抽出
def extract_json(gpt_output):
    match = re.search(r"(\[\s*{.*}\s*\])", gpt_output, re.DOTALL)
    if not match:
        return None
    raw_json = match.group(1)
    cleaned_json = (
        raw_json
        .replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
        .strip()
    )
    try:
        return json.loads(cleaned_json)
    except json.JSONDecodeError:
        return None

# ここからメイン
def main():
    USER_CREDENTIALS = st.secrets["USER_CREDENTIALS"]
    api_key = ""
    gpt_model = "gpt-4.1"
    uploaded_file = None
    temp_video_path = None
    video_configs = None

    st.set_page_config(page_title="動画切り取りアプリ",page_icon="🎬", layout="wide")
    st.title("動画切り取りアプリ✂️")

    # セッションにログイン状態を保持
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    
    try:
        msg = st.sidebar.empty()
        msg2 = st.empty()
        
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
                        api_key = st.session_state.api_key
                        login_area.empty() # ログインフォームを消す
                        msg.success("ログインに成功しました")
                        time.sleep(2)
                        msg.empty()
                        st.rerun() # ログイン状態を反映するために再実行
                    elif (not user_info) or (not user_info["password"]):
                        st.error("ユーザー名・パスワードどちらも入力してください")
                    else:
                        st.error("ユーザー名またはパスワードが間違っています")
        else:
            # ログイン後に表示
            user_info = USER_CREDENTIALS[st.session_state.username]
            loginmessage = f"👤 **{st.session_state.username}**としてログイン中"
            st.sidebar.markdown(loginmessage)
            notification(loginmessage)
            api_key = st.session_state.api_key
            if st.sidebar.button("ログアウト"):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.api_key = ""
                st.rerun()  # ログアウト後に画面を更新

        # --- 動画アップロード ---
        if not st.session_state.logged_in:
            st.warning("👈まずはログインしてください")
        if st.session_state.logged_in:
            st.header("■動画ファイルをアップロード")
            msg2.success("動画をドラッグアンドドロップで読み込みできます！")
            uploaded_file = st.file_uploader(
                "ここに動画ファイルをドラッグ＆ドロップ、またはクリックして選択",
                type=["mp4"],
                accept_multiple_files=False
            )
            if uploaded_file is None:
                st.warning("動画ファイルをアップロードしてください")
                st.stop()
            else:
                # アップロード時刻でキャッシュ管理
                prev_upload_time = st.session_state.get("upload_time")
                msg3 = st.empty()
                # 新しい動画がアップロードされた場合だけキャッシュリセット
                now_upload_time = str(int(time.time()))  # 秒単位のタイムスタンプ（文字列化）
                if not prev_upload_time or st.session_state.get("uploaded_file_obj") != uploaded_file:
                    st.session_state["upload_time"] = now_upload_time
                    st.session_state["uploaded_file_obj"] = uploaded_file
                    st.session_state["video_configs"] = None
                    st.session_state["transcript"] = None
                msg2.empty()
                msg3.success("アップロードが完了しました！")
                video_configs = None
                base_file_name = os.path.splitext(os.path.basename(uploaded_file.name))[0]
                base_file_name_short = base_file_name[:50]
                output_file_name = f"{base_file_name_short}_{st.session_state['upload_time']}_"
                temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                temp_video.write(uploaded_file.getbuffer())
                temp_video_path = temp_video.name
                temp_video.close()
        
                # ファイルが変わったらキャッシュクリア
                if (
                    "uploaded_file_name" not in st.session_state or
                    st.session_state.uploaded_file_name != uploaded_file.name
                ):
                    st.session_state.uploaded_file_name = uploaded_file.name
                    st.session_state.transcript = None  # キャッシュクリア
    
            if "transcript" not in st.session_state or st.session_state.transcript is None:
                # Whisperで音声抽出＆認識
                audio_tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                video = VideoFileClip(temp_video_path)
                video.audio.write_audiofile(audio_tmp.name, logger=None)
                audio_tmp.close()
                msg3.empty()
                with st.spinner("文字起こし中…しばらくお待ちください"):
                    client = openai.OpenAI(api_key=api_key)
                    with open(audio_tmp.name, "rb") as audio_file:
                        transcript = client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file,
                            response_format="verbose_json",
                            language="ja"
                        )
                    os.remove(audio_tmp.name)
                    st.session_state.transcript = transcript
            else:
                transcript = st.session_state.transcript
    
            # テキスト表示
            texts = ""
            for i, segment in enumerate(transcript.segments):
                texts += f"{segment.text}\n"
            with st.expander("音声認識結果を表示（クリックで開閉）", expanded=False):
                st.text_area("", texts, height=250)
            st.markdown("---")
        
        # 各セグメントをテキストにまとめる
        segment_texts = ""
        for i, segment in enumerate(transcript.segments):
            start = segment.start
            end = segment.end
            text = segment.text
        
            segment_texts += (f"[Segment {i}] {start:.2f}s - {end:.2f}s\n")
            segment_texts += (f"Text: {text}\n")
            segment_texts += ("\n")
        
        # ChatGPTで切り出し案生成
        with st.spinner("AIが切り出し箇所を考え中…🤔"):
            prompt = """
以下のルールに従って、与えられた音声認識結果から動画の構成を自動生成してください。

【概要】
長尺の動画に視聴者を誘導するためのShort動画を作成します。
1分以内の“予告編動画”を意識して、動画を切り取る箇所を決めてください。
なるべくたくさん分割し、見やすい動画を意識します。

【生成内容】
①headline
- 見出しとなる文を日本語で2つ生成
- どちらも13文字程度で作成
- 「続きが見たくなりそうな見出し」を意識する
※「**とは…」「なぜ**？」のような文末が続きが見たくなりそうな見出し。
- 2つの見出しに共通の単語や同じ意味の言葉は使用しない
- “漢字のみ”の見出しは避ける
- 絵文字や特殊文字は使用禁止
- 記号は全角のものを使用する
- 数字・アルファベット・空白は半角のものを使用する
- 音声認識結果に誤字があると判断した場合は正しい字に直して出力する（例：「ドーミン」＝「道民」,「寝上げ」＝「値上げ」 など）
例1：["“とっさに蹴り”で反撃", "空手家が遭遇したのは…"]
例2：["ダブル双子ママに密着", "忙しい朝 乗り切れる？"]
②segments
- 動画のIN点とOUT点を決める
- 1つでも、複数入っても良い
- segmetのtextの途中で切ることは避ける
- 疑問を投げかける形のセリフで終わると良い
- 違うセグメントのテキストを繋げて1つの文章にしてはいけない
- 1秒未満のカットは選ばないようにする
- 結合した際の合計時間は50秒以内に収める
- 聞きやすいように無声部分も数秒入れて余裕をもった時間設定にする
- 一番最後のセグメントは、1秒程度余裕を持たせる。ただし、次の音声に入ってしまう場合はギリギリで切る。
例1：[{"start": 10.5, "end": 20.8}]
例2：[{"start": 63, "end": 70.2}, {"start": 81.2, "end": 90.3}, ...]
③font_colors
- "red", "orange", "yellow", "green", "cyan", "magenta", "lime", "white"の中から2色を指定
- 文字の背景は真っ黒になることを想定したうえで、読みやすさを考慮する
- 1色目は基本的に"red"にする(ただし、内容によって他の色がいいと判断した場合は変更してよい)
- 2色目は基本的に"white"にする
- 同じ組み合わせの動画が複数できても構わない

【出力のルール】
- 出力はPythonのlist[dict]形式のJSON構造で出力してください（key順は headline → segments → font_colors）
- マークダウンのコードブロック記号は出力しないでください
- headlineはそれぞれ10文字以上14文字以内の日本語で必ず2つ入れてください
- segments は start, end の秒数を float型で小数第1位までで指定し、音声に基づいて内容の切れ目を適切に設定してください
- 出力以外のテキストは禁止。JSON以外の出力（説明文、補足、コードブロックの外など）は一切含めないでください
- リストの中身の数（最終的な動画の数）は5つ以上としてください
- 同じ場面を違う切り口で切り出して数を増やしても良い

【出力形式】
[
  {
    "headline": ["ヘッドライン1-1", "ヘッドライン1-2"],
    "segments": [{"start": 秒数, "end": 秒数}, {"start": 秒数, "end": 秒数}, ...],
    "font_colors": ["色1-1", "色1-2"]
  },
  {
    "headline": ["ヘッドライン2-1", "ヘッドライン2-2"],
    "segments": [{"start": 秒数, "end": 秒数}, {"start": 秒数, "end": 秒数}, ...],
    "font_colors": ["色2-1", "色2-2"]
  },
  …（3つ以上続いても良い）
]

【音声認識結果】
""" + segment_texts

            client = openai.OpenAI(api_key=api_key)
            if st.session_state.get("video_configs") is None:
                response = client.chat.completions.create(
                    model=gpt_model,
                    messages=[
                        {"role": "system", "content": "あなたはテレビ局でニュース動画をネット配信するプロのディレクターです。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                gpt_output = response.choices[0].message.content
    
                video_configs = extract_json(gpt_output)
                st.session_state["video_configs"] = video_configs
            else:
                video_configs = st.session_state["video_configs"]
            
            if not video_configs:
                st.error("JSON構造が見つかりませんでした。もう一度やり直してください。")
                st.stop()
    
            # 候補が決まったら
            st.session_state["video_configs"] = video_configs
            msg4 = st.empty()
        if "video_configs" in st.session_state:
            video_configs = st.session_state["video_configs"]
            num_videos = len(video_configs)
            msg4.success(f"{num_videos}本の候補が生成されました。動画を切り出します。")

            # 案の内容を確認
            for i, config in enumerate(video_configs):
                with st.expander(f"候補 {i+1}: {config['headline'][0]} ／ {config['headline'][1]}", expanded=False):
                    st.markdown("**切り出し区間（秒）**")
                    for seg in config['segments']:
                        st.markdown(
                            f"- ⏱️ **{seg['start']:.1f}** ～ **{seg['end']:.1f}**"
                        )
    
            with st.spinner("動画を切り出し中…"):
                process_multiple_videos(
                    video_configs, temp_video_path, output_file_name
                )
                msg4.empty()
            st.success("動画が完成しました！")
            st.rerun()

    except Exception as e:
        err_msg = str(e)
        if "incorrect api key" in err_msg.lower() or "invalid_api_key" in err_msg.lower():
            st.error("設定されたAPIキーが正しくありません。ログインしなおしてください。")
        elif "insufficient_quota" in err_msg.lower():
            st.error("登録されたAPIキーの利用上限を超えました。Usage/Billing画面で残高をご確認ください。")
        elif "'invalid_request_error', 'param': None" in err_msg.lower():
            st.error("ページ更新後、ログインしなおしてください")
        else:
            if st.session_state.logged_in:
                st.error(f"予期しないエラーが発生しました: {e}")

if __name__ == '__main__':
    main()
