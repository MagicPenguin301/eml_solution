import os
import zipfile
import streamlit as st
import MailGetter
import MailProcesser
import shutil
import pandas as pd
import re


def find_prices_and_cases(text):
    # 正则表达式用于匹配价格的字符串
    price_pattern = r'\$\d+(\.\d{2})?'  # 匹配$后面跟整数或小数点后两位的数字
    # 正则表达式用于匹配包含"case"或"cases"的字符串（不区分大小写）
    cases_pattern = r'\bcase(?:s)?\b'  # 匹配单词"case"或"cases"，忽略大小写
    # 统计价格和"case"、"cases"出现的次数
    price_count = len(re.findall(price_pattern, text))
    cases_count = len(re.findall(cases_pattern, text, re.IGNORECASE))
    return price_count, cases_count
@st.cache_data
def mail_dict_from_zip(uploaded_zip):
    save_folder = 'save_folder'
    if uploaded_zip is not None:
        with zipfile.ZipFile(uploaded_zip, "r") as zip_ref:
            # 获取ZIP文件中的文件列表
            file_list = zip_ref.namelist()
            # 解压缩文件到临时目录
            os.makedirs(save_folder)
            zip_ref.extractall(save_folder)
        possible_mails = []
        mail_dict = {}
        meta_mails = []
        for name in zip_ref.namelist():
            if name.lower().endswith('.eml'):
                path = os.path.join(save_folder, name)
                metamail = MailGetter.read_eml(path)
                metamail[0]['file_name'] = name
                meta_mails.append((metamail[0],f'{metamail[1]}'))
        sorted_meta_mails = MailProcesser.sorted_mail(meta_mails)
        sorted_name_list = []
        for i, mail in enumerate(sorted_meta_mails):
            meta_text = f"``file name:{mail[0]['file_name']}``\n\nfrom: {mail[0]['from']}\n\nto: {mail[0]['to']}\n\ndate: {mail[0]['date'].strftime('%Y/%m/%d, %H:%M:%S %Z')}\n"
            sorted_name_list.append(mail[0]['file_name'])
            text = mail[1]
            mail_dict[i+1] = meta_text + "\n\n" + text
            if find_prices_and_cases(text)[0]+find_prices_and_cases(text)[1]>=2:
                possible_mails.append(i+1)
        st.write(f'``以下页码可能比较重要:\n {possible_mails}``')
        shutil.rmtree(save_folder)
        return mail_dict, sorted_name_list

def render_columns(mail_dict):
    col1, col2 = st.columns(2)
    with col1:
        # st.markdown(result_with_br, unsafe_allow_html=True)
        st.markdown(mail_dict[st.session_state.current_page])
    # 显示 ABCD 四个值的表单
    with col2:
        for key in st.session_state.result_dict:
            st.session_state.result_dict[key][st.session_state.current_page-1] = \
                st.text_input(f"填写{key}的值#{key}{st.session_state.current_page}",
                              key=f"{key}{st.session_state.current_page}",
                              value=st.session_state.result_dict[key][st.session_state.current_page-1])

def render_page_btn(total_pages,key):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.session_state.current_page = int(st.text_input('输入跳转',value=st.session_state.current_page,key=key))
        st.write(f'{st.session_state.current_page}/{total_pages}')
    with col1:
        if st.session_state.current_page > 1:
            if st.button("上一页",key=f'up{key}'):
                st.session_state.current_page -= 1
                st.experimental_rerun() # This is Magic
    with col3:
        if st.session_state.current_page < total_pages:
            if st.button("下一页",key=f'down{key}'):
                st.session_state.current_page += 1
                st.experimental_rerun() # This is also Magic

def check_downloadable(total_pages):
    if True:
        if st.button("点击下载目前的进度"):
            # 将 ABCD 四个值保存到 CSV 文件中
            df = pd.DataFrame(st.session_state.result_dict)
            st.dataframe(df)
            st.download_button(
                label="点击下载CSV文件",
                data=df.to_csv("ABCD_values.csv",index=False,encoding='utf-8'),
                file_name="ABCD_values.csv",
                mime="text/csv")
        if st.button("清除所有记录"):
            st.session_state.result_dict = {
            'File Name': [''] * total_pages,
            'A': ['']*total_pages,
            'B': ['']*total_pages,
            'C': ['']*total_pages,
            'D': ['']*total_pages
        }

def main():
    st.title("在线解压并处理ZIP文件")
    uploaded_file = st.file_uploader("请选择要上传的ZIP文件", type=["zip"])
    if uploaded_file is not None:
        mail_dict,sorted_name_list = mail_dict_from_zip(uploaded_file)
        total_pages = len(mail_dict)
        st.write(f'total: {total_pages}')
        current_page = st.session_state.get("current_page", 1)
        st.session_state.current_page = current_page
        null_dict = {
            'File Name':sorted_name_list,
            'A': ['']*total_pages,
            'B': ['']*total_pages,
            'C': ['']*total_pages,
            'D': ['']*total_pages
        }
        result_dict = st.session_state.get('result_dict',null_dict)
        st.session_state.result_dict = result_dict

        render_page_btn(total_pages,1)
        render_columns(mail_dict)
        render_page_btn(total_pages,2)
        check_downloadable(total_pages)

if __name__ == "__main__":
    main()