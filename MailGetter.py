import eml_parser
import email
import re
import streamlit as st

def extract_text_from_eml(eml_path):
    with open(eml_path, 'r', encoding='utf-8') as eml_file:
        # 解析EML文件
        msg = email.message_from_file(eml_file)

        # 初始化正文内容
        body = ""
        # 查找第一个文本部分
        def find_text_part(message):
            if message.is_multipart():
                for part in message.walk():
                    if part.get_content_type() == "text/plain":
                        return part.get_payload(decode=True).decode('utf-8', errors='ignore')
            else:
                return message.get_payload(decode=True).decode('utf-8', errors='ignore')

        # 查找回复分隔符
        def find_reply_separator(text):
            separators = ["-----Original Message-----", "--- 原始邮件 ---", "> On", "在 .*写道：", "在.*发送的邮件中：",">On","|On","| On","---- Replied Message ----","→ ---- Replied Message ----"]
            for separator in separators:
                if separator in text:
                    return separator
            return None

        def filter_text(text):
            # 删除重复信息
            filtered_content = []
            lines = text.splitlines()
            ignore_lines = ["Phone:", "Email:", "Website:", "Company:", "Address:",
                            "*Join our email list for the latest hobby info","<https://blowoutcards.us3.list-manage.com/subscribe/post?u=7d75c38d7aca46cbe27ec4ebc&id=9741f07c16>"]
            ignore_next_line = False
            for line in lines:
                if any(substring in line for substring in ignore_lines):
                    ignore_next_line = True
                elif ignore_next_line:
                    ignore_next_line = False
                else:
                    filtered_content.append(line)
            filtered_text = "\n".join(filtered_content)
            return filtered_text

        def escape_markdown(text):
            return text.replace('$','\$')

        text_content = find_text_part(msg)
        reply_separator = find_reply_separator(text_content)

        if reply_separator:
            # 提取回复内容
            body = text_content.split(reply_separator, 1)[0]
        else:
            body = text_content


        return filter_text(escape_markdown(body.strip()))


def extract_metadata(path):
    with open(path, 'rb') as fhdl:
        raw_email = fhdl.read()
    ep = eml_parser.EmlParser()
    parsed_eml = ep.decode_email_bytes(raw_email)["header"]
    st.write(parsed_eml['header']['from'])
    return {"from":parsed_eml['from'],"to":parsed_eml['to'][0] if len(parsed_eml['to'])==1 else parsed_eml['to'], "date":parsed_eml['date']}

def read_eml(path):
    metadata = extract_metadata(path)
    message_text = extract_text_from_eml(path)
    return metadata, message_text
