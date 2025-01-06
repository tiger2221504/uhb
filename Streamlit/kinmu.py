import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import numpy as np
import random
pd.set_option('future.no_silent_downcasting', True)

# 初期生成用の関数
def create_main(df):
  kiso_table = df.copy().iloc[:, 7:]

  # ==泊まり勤務==

  # 泊16・泊22
  list = []
  for i in range(len(role)):
    if role["泊22"][i]=="TRUE":
      list.append(i)
  n = np.random.randint(0,len(list)+1)
  for i in range(len(kiso_table.columns)):
    if data_kyuuzitsu.iloc[0, i]==0:
      if n%(len(list)+1)==len(list):
        for j in range(i,i+4):
          for k in range(100):
            x = np.random.randint(0,len(kiso_table))
            if role["泊16"][x]=="TRUE" and kiso_table.iloc[x, j] =="":
              kiso_table.iloc[x, j] = "泊16"
              if j<days:
                kiso_table.iloc[x, j+1] = "明"
                if j<days-1:
                  kiso_table.iloc[x, j+2] = "休"
              break
      else:
        x = list[n%(len(list)+1)]
        if i<days:
          kiso_table.iloc[x, i] = "泊22"
          if i<days-1:
            kiso_table.iloc[x, i+1] = "泊22"
            if i<days-2:
                kiso_table.iloc[x, i+2] = "泊22"
                if i<days-3:
                  kiso_table.iloc[x, i+3] = "泊22"
                  if i<days-4:
                    kiso_table.iloc[x, i+4] = "明"
      n += 1


  # 管理泊
  list = []
  for i in range(len(role)):
    if role["管理泊"][i]=="TRUE":
      list.append(i)
  random.shuffle(list)
  for i in range(len(kiso_table.columns)):
    if data_kyuuzitsu.iloc[0, i]==6:
      for j in range(100):
        x = list.pop(0)
        list.append(x)
        if role["管理泊"][x]=="TRUE" and kiso_table.iloc[x, i] =="":
          kiso_table.iloc[x, i] = "泊22"
          if j<days and kiso_table.iloc[x, i+1] =="":
            kiso_table.iloc[x, i+1] = "明"
            if j<days-1 and kiso_table.iloc[x, j+2] =="":
              kiso_table.iloc[x, i+2] = "休"
          break

  # ==デスク系==

  # 編長
  for i in range(len(kiso_table.columns)):
    if data_kyuuzitsu.iloc[0, i] in [0, 1, 2, 3, 4]:
      for n in range(100):
        x = np.random.randint(0,len(kiso_table))
        if role["編長"][x]=="TRUE" and kiso_table.iloc[x, i] =="":
          kiso_table.iloc[x, i] = "編長"
          break

  # Bデスク
  for i in range(len(kiso_table.columns)):
    if data_kyuuzitsu.iloc[0, i] in [0, 1, 2, 3, 4]:
      for n in range(100):
        x = np.random.randint(0,len(kiso_table))
        if role["B"][x]=="TRUE" and kiso_table.iloc[x, i] =="":
          kiso_table.iloc[x, i] = "B"
          break

  # Cデスク
  for i in range(len(kiso_table.columns)):
    if data_kyuuzitsu.iloc[0, i] in [0, 1, 2, 3, 4]:
      for n in range(100):
        x = np.random.randint(0,len(kiso_table))
        if role["C"][x]=="TRUE" and kiso_table.iloc[x, i] =="":
          kiso_table.iloc[x, i] = "C"
          break

  # 土デスク
  for i in range(len(kiso_table.columns)):
    if data_kyuuzitsu.iloc[0, i]==5:
      for n in range(100):
        x = np.random.randint(0,len(kiso_table))
        if role["土D"][x]=="TRUE" and kiso_table.iloc[x, i] =="":
          kiso_table.iloc[x, i] = "土D"
          break

  # 日デスク
  for i in range(len(kiso_table.columns)):
    if data_kyuuzitsu.iloc[0, i]==6:
      for n in range(100):
        x = np.random.randint(0,len(kiso_table))
        if role["日D"][x]=="TRUE" and kiso_table.iloc[x, i] =="":
          kiso_table.iloc[x, i] = "日D"
          break

  # 特殊休日デスク
  for i in range(len(kiso_table.columns)):
    if data_kyuuzitsu.iloc[0, i]==7:
      for n in range(100):
        x = np.random.randint(0,len(kiso_table))
        if (role["土D"][x]=="TRUE" or role["日D"][x]=="TRUE") and kiso_table.iloc[x, i] =="":
          kiso_table.iloc[x, i] = "D"
          break

  # Nデスク
  for i in range(len(kiso_table.columns)):
    if data_kyuuzitsu.iloc[0, i] in [0, 1, 2, 3, 4]:
      for n in range(100):
        x = np.random.randint(0,len(kiso_table))
        if role["N"][x]=="TRUE" and kiso_table.iloc[x, i] =="":
          kiso_table.iloc[x, i] = "N"
          break

  # ==記者系==

  # 早勤務
  for i in range(len(kiso_table.columns)):
    if data_kyuuzitsu.iloc[0, i] in [0, 1, 2, 3, 4]:
      for n in range(100):
        x = np.random.randint(0,len(kiso_table))
        if role["早"][x]=="TRUE" and kiso_table.iloc[x, i] =="":
          kiso_table.iloc[x, i] = "早"
          break

  # 昼勤務
  for i in range(len(kiso_table.columns)):
    if data_kyuuzitsu.iloc[0, i] in [0, 1, 2, 3, 4]:
      for n in range(100):
        x = np.random.randint(0,len(kiso_table))
        if role["昼"][x]=="TRUE" and kiso_table.iloc[x, i] =="":
          kiso_table.iloc[x, i] = "昼"
          break

  # 遅勤務
  for i in range(len(kiso_table.columns)):
    if data_kyuuzitsu.iloc[0, i] in [0, 1, 2, 3]:
      for n in range(100):
        x = np.random.randint(0,len(kiso_table))
        if role["遅"][x]=="TRUE" and kiso_table.iloc[x, i] =="":
          kiso_table.iloc[x, i] = "遅"
          break

  # 深夜勤務
  for i in range(len(kiso_table.columns)):
    if data_kyuuzitsu.iloc[0, i] in [4, 5]:
      for n in range(100):
        x = np.random.randint(0,len(kiso_table))
        if role["深夜"][x]=="TRUE" and kiso_table.iloc[x, i] =="":
          kiso_table.iloc[x, i] = "深夜"
          break

  # 日勤務
  for i in range(len(kiso_table.columns)):
    if data_kyuuzitsu.iloc[0, i]==6:
      for n in range(100):
        x = np.random.randint(0,len(kiso_table))
        if role["日"][x]=="TRUE" and kiso_table.iloc[x, i] =="":
          kiso_table.iloc[x, i] = "日"
          break

  # 日①勤務
  for i in range(len(kiso_table.columns)):
    if data_kyuuzitsu.iloc[0, i]==6:
      for n in range(100):
        x = np.random.randint(0,len(kiso_table))
        if role["日①"][x]=="TRUE" and kiso_table.iloc[x, i] =="":
          kiso_table.iloc[x, i] = "日①"
          break

  # 日②勤務
  for i in range(len(kiso_table.columns)):
    if data_kyuuzitsu.iloc[0, i]==6:
      for n in range(100):
        x = np.random.randint(0,len(kiso_table))
        if role["日②"][x]=="TRUE" and kiso_table.iloc[x, i] =="":
          kiso_table.iloc[x, i] = "日②"
          break

  # ==休み==
  henkou_list = []
  for i in range(len(kiso_table)):
    for x in range(days):
      if (kiso_table.loc[i] == "休").sum() < int(holiday.iloc[i]):
        if kiso_table.iloc[i, x] == "" and data_kyuuzitsu.iloc[0, x]in[5, 6, 7]:
          kiso_table.iloc[i, x] = "休"
    k=0
    while (kiso_table.loc[i] == "休").sum() < int(holiday.iloc[i]) and k<10000:
      if (kiso_table.loc[i] == "").sum()>0:
        x = np.random.randint(days)
        if role["編長"][i]=="TRUE" and data_kyuuzitsu.iloc[0, x]==2:
          continue
        if kiso_table.iloc[i, x] == "":
          kiso_table.iloc[i, x] = "休"
      else:
        x = np.random.randint(days)
        if kiso_table.iloc[i, x] not in ["休", "1"]:
          henkou_list.append([x, kiso_table.iloc[i, x]])
          kiso_table.iloc[i, x] = "休"
      if (kiso_table.loc[i] == "休").sum() == days:
        break
      k += 1

  # 消えた役職を復活させる
  for n in henkou_list:
    d = n[0]
    r = n[1]
    if r in role.columns:
      for k in range(1000):
        x = np.random.randint(len(kiso_table))
        if role[r][x]=="TRUE" and kiso_table.iloc[x, d]:
          kiso_table.iloc[x, d] = r
          break

  # 役職ない人は空白を0で埋める
  for j in range(len(kiso_table)):
    if (role.loc[j] == "TRUE").sum()==0:
      for i in range(days):
        if kiso_table.iloc[j, i] == "":
          kiso_table.iloc[j, i] = "0"

  return kiso_table

from itertools import count
# 評価関数

# 記者：週末の勤務は月２回まで
def check_weekend(df):
  score = 0
  diff = 0
  for i in range(len(df)):
    count = 0
    if role["早"][i]=="TRUE" or role["昼"][i]=="TRUE" or role["遅"][i]=="TRUE" or role["深夜"][i]=="TRUE":
      for j in range(len(df.columns)):
        if (df.iloc[i, j] not in ["休","1"]) and (data_kyuuzitsu.iloc[0, j] in [5, 6, 7]):
          count += 1
      if count>2:
        diff += 1
        score += count**2
  # print(f"check_weekend:{score}")
  return score, diff

# 記者：２週連続で土日勤務はNG
def check_donitikinmu(df):
  df_all = data_kakuteibi.copy()
  df_all.iloc[:, 7:] = df
  df_all = df_all.replace('', 0)
  df_all = df_all.replace('休', 1)
  df_all = df_all.astype(str).replace(to_replace=r'[^1]', value=0, regex=True)
  score = 0
  count = 0
  for i in range(len(df_all)):
    list = []
    if role["早"][i]=="TRUE" or role["昼"][i]=="TRUE" or role["遅"][i]=="TRUE" or role["深夜"][i]=="TRUE":
      for j in range(len(df.columns)):
        if kyuuzitsu_all.iloc[0, j] in [5, 6, 7]:
          list.append(str(df_all.iloc[i, j]))
      x = "".join(list)
      x = x.split("1")
      for s in x:
        if len(s)>=3:
          count += 1
          score += (len(s))**2
        elif len(s)==2:
          count += 1
          score += 2
  # print(f"check_donitikinmu:{score}")
  return score, count

# ７連勤以上にならないように
def check_7renkin(df):
  df_all = data_kakuteibi.copy()
  df_all.iloc[:, 7:] = df
  df_all = df_all.replace('', 0)
  df_all = df_all.replace('休', 1)
  df_all = df_all.astype(str).replace(to_replace=r'[^1]', value=0, regex=True)
  score = 0
  count = 0
  for i in range(len(df_all)):
    list = []
    for j in range(len(df.columns)):
      list.append(str(df_all.iloc[i, j]))
    x = "".join(list)
    x = x.split("1")
    for s in x:
      if len(s)>=7:
        count += 1
        score += (len(s))**2
  # print(f"check_7renkin:{score}")
  return score, count

# 編集長・B・C・N…月～金で１人
def check_heizitsudesk(df):
  score = 0
  diff = 0
  for i in range(len(df.columns)):
    count_B = 0
    count_C = 0
    count_N = 0
    count_h = 0
    if data_kyuuzitsu.iloc[0, i] in [0, 1, 2, 3, 4]:
      for j in range(len(df)):
        if df.iloc[j, i] == "B":
          count_B += 1
        elif df.iloc[j, i] == "C":
          count_C += 1
        elif df.iloc[j, i] == "N":
          count_N += 1
        elif df.iloc[j, i] == "編長":
          count_h += 1
      if count_B!=1:
        diff += 1
        score += abs(count_B-1)*20
      if count_C!=1:
        diff += 1
        score += abs(count_C-1)*20
      if count_N!=1:
        diff += 1
        score += abs(count_N-1)*20
      if count_h!=1:
        diff += 1
        score += abs(count_h-1)*20
  # print(f"check_heizitsudesk:{score}")
  return score, diff

# 土日デスク…各1人
def check_donitidesk(df):
  score = 0
  diff = 0
  for i in range(len(df.columns)):
    count_SAT = 0
    count_SUN = 0
    if data_kyuuzitsu.iloc[0, i] ==5:
      for j in range(len(df)):
        if df.iloc[j, i] == "土D":
          count_SAT += 1
      if count_SAT!=1:
        diff += 1
        score += abs(count_SAT-1)*20
    if data_kyuuzitsu.iloc[0, i] ==6:
      for j in range(len(df)):
        if df.iloc[j, i] == "日D":
          count_SUN += 1
      if count_SUN!=1:
        diff += 1
        score += abs(count_SUN-1)*20
  # print(f"check_donitidesk:{score}")
  return score, diff

# 正月デスク…1人
def check_shougatsudesk(df):
  score = 0
  diff = 0
  for i in range(len(df.columns)):
    count = 0
    if data_kyuuzitsu.iloc[0, i]==7:
      for j in range(len(df)):
        if df.iloc[j, i] == "D":
          count += 1
      if count!=1:
        diff += 1
        score += abs(count-1)*20
  # print(f"check_shougatsudesk:{score}")
  return score, diff

# デスク：月～金は、編集長・Cも合わせて４名以上勤務者がいるように（B勤務、喜多は除く）
def check_heizitsu(df):
  score = 0
  diff = 0
  for i in range(len(df.columns)):
    count = 0
    if data_kyuuzitsu.iloc[0, i] in [0, 1, 2, 3, 4]:
      for j in range(len(df)):
        if role["編長"][j]=="TRUE" or role["B"][j]=="TRUE" or role["C"][j]=="TRUE" or role["日D"][j]=="TRUE":
          if str(df.iloc[j, i]) not in ["B", "休", "1"]:
            count += 1
      if count<5:
        diff += 1
        score += (10-count)**2
  # print(f"check_heizitsu:{score}")
  return score, diff

# 同一人物でC→BはNG
def check_CB(df):
  df_all = data_kakuteibi.copy()
  df_all.iloc[:, 7:] = df
  df_all = df_all.replace('', 0)
  df_all = df_all.replace('休', 1)
  score = 0
  count = 0
  for i in range(len(df_all)):
    list = []
    for j in range(len(df.columns)):
      list.append(str(df_all.iloc[i, j]))
    x = "".join(list)
    x = x.split("CB")
    if len(x)>=2:
      count += 1
      score += (len(x))**2
  # print(f"check_CB:{score}")
  return score, count

# 同一人物でN→BはNG
def check_NB(df):
  df_all = data_kakuteibi.copy()
  df_all.iloc[:, 7:] = df
  df_all = df_all.replace('', 0)
  df_all = df_all.replace('休', 1)
  score = 0
  count = 0
  for i in range(len(df_all)):
    list = []
    for j in range(len(df.columns)):
      list.append(str(df_all.iloc[i, j]))
    x = "".join(list)
    x = x.split("NB")
    if len(x)>=2:
      count += 1
      score += (len(x))**2
  # print(f"check_NB:{score}")
  return score, count

# 記者：早・昼勤務…月～金で１人
def check_kisya1(df):
  score = 0
  count_all = 0
  for i in range(len(df.columns)):
    count1 = 0
    count2 = 0
    if data_kyuuzitsu.iloc[0, i] in [0, 1, 2, 3, 4]:
      for j in range(len(df)):
        if df.iloc[j, i] == "早":
          count1 += 1
        elif df.iloc[j, i] == "昼":
          count2 += 1
      if count1!=1:
        count_all += 1
        score += abs(count1-1)*10
      if count2!=1:
        count_all += 1
        score += abs(count2-1)*10
  # print(f"check_kisya1:{score}")
  return score, count_all

# 記者：遅勤務…月～木で、安野・林・鎌田が泊りの週
def check_kisya2(df):
  score = 0
  diff = 0
  for i in range(len(df.columns)):
    count = 0
    if data_kyuuzitsu.iloc[0, i] in [0, 1, 2, 3]:
      for j in range(len(df)):
        if df.iloc[j, i] == "遅":
          count += 1
      if count!=1:
        diff += 1
        score += abs(count-1)*10
  # print(f"check_kisya2:{score}")
  return score, diff

# 記者：深夜勤務…金曜、土曜で１人
def check_kisya3(df):
  score = 0
  diff = 0
  for i in range(len(df.columns)):
    count = 0
    if data_kyuuzitsu.iloc[0, i] in [4, 5]:
      for j in range(len(df)):
        if df.iloc[j, i] == "深夜":
          count += 1
      if count!=1:
        diff += 1
        score += abs(count-1)*10
  # print(f"check_kisya3:{score}")
  return score, diff

# 月～金のうち 社会班３名/政経班２名は勤務
def check_syakaiseikei(df):
  score = 0
  diff = 0
  for i in range(len(df.columns)):
    count_syakai = 0
    count_seikei = 0
    if data_kyuuzitsu.iloc[0, i] in [0, 1, 2, 3, 4]:
      youbi = data_kyuuzitsu.iloc[0, i]
      for j in range(len(df)):
        if (df.iloc[j, i] not in ["休","1"]):
          if role["社会"][j]=="TRUE":
            count_syakai += 1
          if role["政経"][j]=="TRUE":
            count_seikei += 1
      if count_syakai<3:
        diff += 1
        score += (10-count_syakai)**2
      if count_seikei<2:
        diff += 1
        score += (10-count_seikei)**2
  # print(f"check_syakaiseikei:{score}")
  return score, diff

# 同一人物で、遅勤務（深夜勤務）→早勤務（日、日①）はNG
def check_renzoku(df):
  df_all = data_kakuteibi.copy()
  df_all.iloc[:, 7:] = df
  df_all = df_all.replace('', 0)
  df_all = df_all.replace('休', 1)
  score = 0
  diff = 0
  for i in range(len(df_all)):
    list = []
    for j in range(len(df.columns)):
      list.append(str(df_all.iloc[i, j]))
    x = "".join(list)
    x = x.split("深夜日")
    if len(x)>=2:
      diff += 1
      score += (len(x))**2
  # print(f"check_renzoku:{score}")
  return score, diff

  # 飛び石連休
def check_tobiishi(df):
  df_all = data_kakuteibi.copy()
  df_all.iloc[:, 7:] = df
  df_all = df_all.replace('', 0)
  df_all = df_all.replace('休', 1)
  df_all = df_all.astype(str).replace(to_replace=r'[^1]', value=0, regex=True)
  score = 0
  count = 0
  for i in range(len(df_all)):
    list = []
    for j in range(len(df.columns)):
      list.append(str(df_all.iloc[i, j]))
    x = "".join(list)
    x = x.split("101")
    if len(x)>1:
      count += 1
      score += (len(x)-1)
  # print(f"check_tobiishi:{score}")
  return score, count

# 休暇数の調整
def kyuukasuu(df):
  score = 0
  diff = 0
  for i in range(len(df)):
    count = 0
    for j in range(len(df.columns)):
      if df.iloc[i, j] == "休":
        count += 1
    if count!=int(holiday.iloc[i]):
      diff += 1
      score += ((abs(count-int(holiday.iloc[i])))*5)**2
  # print(f"kyuukasuu:{score}")
  return score, diff

# すべての評価
def check_ALL(df):
  df = df.astype(str)
  score_sum = 0
  list = []
  score, count = check_weekend(df)
  score_sum += score
  list.append(count)
  score, count = check_donitikinmu(df)
  score_sum += score
  list.append(count)
  score, count = check_7renkin(df)
  score_sum += score
  list.append(count)
  score, diff = check_heizitsudesk(df)
  score_sum += score
  list.append(diff)
  score, diff = check_donitidesk(df)
  score_sum += score
  list.append(diff)
  score, diff = check_shougatsudesk(df)
  score_sum += score
  list.append(diff)
  score, diff = check_heizitsu(df)
  score_sum += score
  list.append(diff)
  score, count = check_CB(df)
  score_sum += score
  list.append(count)
  score, count = check_NB(df)
  score_sum += score
  list.append(count)
  score, count_all = check_kisya1(df)
  score_sum += score
  list.append(count_all)
  score, diff = check_kisya2(df)
  score_sum += score
  list.append(diff)
  score, diff = check_kisya3(df)
  score_sum += score
  list.append(diff)
  score, diff = check_syakaiseikei(df)
  score_sum += score
  list.append(diff)
  score, diff = check_renzoku(df)
  score_sum += score
  list.append(diff)
  score, count = check_tobiishi(df)
  score_sum += score
  list.append(count)
  score, diff = kyuukasuu(df)
  score_sum += score
  list.append(diff)

  score_sum = -score_sum

  text = (
      f"**修正できていない箇所**\n  "
      f"- 記者：週末の勤務は月２回まで:{list[0]}\n  "
      f"- 記者：２週連続で土日勤務:{list[1]}\n  "
      f"- ７連勤以上:{list[2]}\n  "
      f"- 編集長・B・C・N…月～金で１人:{list[3]}\n  "
      f"- 土日デスク…各1人:{list[4]}\n  "
      f"- 正月デスク…1人:{list[5]}\n  "
      f"- デスク：月～金は４名以上:{list[6]}\n  "
      f"- 同一人物でC→BはNG:{list[7]}\n  "
      f"- 同一人物でN→BはNG:{list[8]}\n  "
      f"- 記者：早・昼勤務…月～金で１人:{list[9]}\n  "
      f"- 記者：遅勤務…月～木:{list[10]}\n  "
      f"- 記者：深夜勤務…金曜、土曜で１人:{list[11]}\n  "
      f"- 月～金のうち 社会班３名/政経班２名は勤務:{list[12]}\n  "
      f"- 同一人物で、遅勤務（深夜勤務）→早勤務（日、日①）はNG:{list[13]}\n  "
      f"- 飛び石連休:{list[14]}\n  "
      f"- 休暇数:{list[15]}"
  )

  return score_sum, text

# セッション状態を初期化
if "x" not in st.session_state:
    st.session_state.x = None
if "display_text" not in st.session_state:
    st.session_state.display_text = ""
if "best_score" not in st.session_state:
  st.session_state.best_score = None

st.title('勤務表生成システムβ')

# 入力フォーム
SPREADSHEET_URL = st.text_input("スプレッドシートのURLを入力")
generate_length = st.number_input("生成回数を入力", min_value=1, value=50, step=1)
start_button = st.button("スタート")

# ==メインの処理==
if start_button and st.session_state.x is None:
  try:
    st.info("処理を開始しました")
    progress_text = "処理中です. しばらくお待ちください."
    my_bar = st.progress(0, text=progress_text) # プログレスバー
    
    # ==スプレッドシートの準備==
    
    # サービスアカウントキーのパスを指定
    SERVICE_ACCOUNT_FILE = './pythongs-405212-dee426556119.json'
    # 2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
    scope = [
       'https://www.googleapis.com/auth/spreadsheets',
       'https://www.googleapis.com/auth/drive'
       ]
    # サービスアカウント認証情報を生成
    creds = Credentials.from_service_account_file("./Streamlit/pythongs-405212-dee426556119.json", scopes=scope)
    # gspreadで認証
    gc = gspread.authorize(creds)
    # スプレッドシート（ブック）を開く
    workbook = gc.open_by_url(SPREADSHEET_URL)
    
    worksheet_kakuteibi = workbook.worksheet('確定日')
    data_kakuteibi = pd.DataFrame(worksheet_kakuteibi.get_all_values())
    # data_kakuteibiを整える
    data_kakuteibi = data_kakuteibi.iloc[:, 1:]
    data_kakuteibi = data_kakuteibi.drop(0)
    data_kakuteibi = data_kakuteibi.drop(1)
    data_kakuteibi = data_kakuteibi.drop(2)
    data_kakuteibi.reset_index(drop=True, inplace=True)
    data_kakuteibi.iloc[:, 0:7] = data_kakuteibi.iloc[:, 0:7].replace('', 0)
    data_kakuteibi.columns = [i-6 for i in range(len(data_kakuteibi.columns))]
    # data_kakuteibi
    
    worksheet_kyuuzitsu = workbook.worksheet('休日設定')
    data_kyuuzitsu = pd.DataFrame(worksheet_kyuuzitsu.get_all_values())
    # data_kyuuzitsuを整える
    data_kyuuzitsu = data_kyuuzitsu.iloc[:, 1:]
    data_kyuuzitsu.loc[2, data_kyuuzitsu.loc[1].str.contains(r'月', na=False) & (data_kyuuzitsu.loc[2] == "FALSE")] = 0
    data_kyuuzitsu.loc[2, data_kyuuzitsu.loc[1].str.contains(r'火', na=False) & (data_kyuuzitsu.loc[2] == "FALSE")] = 1
    data_kyuuzitsu.loc[2, data_kyuuzitsu.loc[1].str.contains(r'水', na=False) & (data_kyuuzitsu.loc[2] == "FALSE")] = 2
    data_kyuuzitsu.loc[2, data_kyuuzitsu.loc[1].str.contains(r'木', na=False) & (data_kyuuzitsu.loc[2] == "FALSE")] = 3
    data_kyuuzitsu.loc[2, data_kyuuzitsu.loc[1].str.contains(r'金', na=False) & (data_kyuuzitsu.loc[2] == "FALSE")] = 4
    data_kyuuzitsu.loc[2, data_kyuuzitsu.loc[1].str.contains(r'土', na=False) & (data_kyuuzitsu.loc[2] == "FALSE")] = 5
    data_kyuuzitsu.loc[2, data_kyuuzitsu.loc[1].str.contains(r'日', na=False) & (data_kyuuzitsu.loc[2] == "FALSE")] = 6
    data_kyuuzitsu.loc[2, data_kyuuzitsu.loc[2] == "TRUE"] = 7
    data_kyuuzitsu = data_kyuuzitsu.drop(0)
    data_kyuuzitsu = data_kyuuzitsu.drop(1)
    data_kyuuzitsu.reset_index(drop=True, inplace=True)
    # data_kyuuzitsu
    
    # kyuuzitsu_allも作成
    kyuuzitsu_all = data_kyuuzitsu.copy()
    kyuuzitsu_new = pd.DataFrame(worksheet_kakuteibi.get_all_values()).iloc[:, 1:].drop(0).drop(1).iloc[:, :7]
    kyuuzitsu_new = kyuuzitsu_new[:1]
    kyuuzitsu_new = kyuuzitsu_new.replace({
        '(月)': "0",
        '(火)': "1",
        '(水)': "2",
        '(木)': "3",
        '(金)': "4",
        '(土)': "5",
        '(日)': "6"
    }, regex=False)
    kyuuzitsu_new = kyuuzitsu_new.reset_index(drop=True, inplace=True)
    kyuuzitsu_all = pd.concat([kyuuzitsu_new, kyuuzitsu_all], axis=1)
    kyuuzitsu_all.columns = [i-6 for i in range(len(kyuuzitsu_all.columns))]
    
    worksheet_member = workbook.worksheet('メンバーリスト')
    data_member = pd.DataFrame(worksheet_member.get_all_values())
    # data_memberを整える
    data_member.columns = data_member.iloc[0]
    data_member = data_member.drop(0)
    data_member.reset_index(drop=True, inplace=True)
    member = data_member.iloc[:, 0:2].reset_index(drop=True)
    holiday = data_member.iloc[:, 2].reset_index(drop=True)
    holiday.columns = ['休暇月計']
    role = data_member.iloc[:, 3:].reset_index(drop=True)
    # member
    # holiday
    # role
    
    worksheet_setting = workbook.worksheet('設定')
    data_setting = pd.DataFrame(worksheet_setting.get_all_values())
    # data_settingから必要な情報を取得
    # data_setting
    st.session_state.YEAR = data_setting.iloc[0,1]
    st.session_state.MONTH = data_setting.iloc[1,1]
    HOLIDAYS = data_setting.iloc[2,1]
    # print(f"年：{YEAR}")
    # print(f"月：{MONTH}")
    # print(f"休日数：{HOLIDAYS}")
    
    # 1か月の日数
    days = len(data_kakuteibi.columns)-7
    # days
    my_bar.progress(1/(generate_length+1), text=progress_text)
    
    list = []
    for i in range(generate_length):
      my_bar.progress((i+1)/(generate_length+1), text=progress_text)
      parent = create_main(data_kakuteibi)
      score, text = check_ALL(parent)
      list.append([score, parent, text])
      print(f"score{i+1}={score}")
    
    # 点数で並び替え
    parents = sorted(list, key=lambda x: -x[0])
    st.session_state.top = parents[0]
    
    # 最強個体の保存
    st.session_state.x = st.session_state.top[1]
    st.session_state.x = st.session_state.x.replace("1", "休")
    st.session_state.x = st.session_state.x.replace("0", "")
    st.session_state.x.index = member["勤務者"].values
    
    st.success("処理が完了しました！")
    my_bar.empty()
    st.session_state.best_score = st.session_state.top[0]
    st.session_state.display_text = st.session_state.top[2]

  except Exception as e:
    st.error("失敗しました")
    st.write(e)

if st.session_state.best_score:
  st.write(f"score={st.session_state.best_score}")
if st.session_state.display_text:
  st.markdown(st.session_state.display_text)
if st.session_state.x is not None:
  st.write("")
  st.subheader(f"{st.session_state.YEAR}年{st.session_state.MONTH}月の勤務表")
  st.dataframe(st.session_state.x)

  csv1 = st.session_state.x.to_csv(index=False, header=False).encode("utf-8_sig")
  st.download_button(
     label="CSV(インデックスなし)",
     data=csv1,
     file_name="勤務表(コピー用).csv",
     mime="text/csv",
    )
  csv2 = st.session_state.x.to_csv(index=True, header=True).encode("utf-8_sig")
  st.download_button(
     label="CSV(インデックスあり)",
     data=csv2,
     file_name="勤務表.csv",
     mime="text/csv",
    )
