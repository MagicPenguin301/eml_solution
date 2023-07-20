import email
import base64

def decode_base64(encoded_string):
    try:
        decoded_bytes = base64.b64decode(encoded_string)
        decoded_string = decoded_bytes.decode('utf-8')
        return decoded_string
    except Exception as e:
        print("Error decoding base64: ", e)
        return None

def parse_email(email_content):
    try:
        msg = email.message_from_string(email_content)

        # 获取邮件主体部分，这里假设你希望解析的内容在邮件的正文中
        main_body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    main_body = part.get_payload(decode=True).decode('utf-8')
                    break
        else:
            main_body = msg.get_payload(decode=True).decode('utf-8')

        # 假设你希望解析的内容是以base64编码的字符串
        base64_encoded_content = main_body

        # 对base64编码的内容进行解码
        decoded_content = decode_base64(base64_encoded_content)

        if decoded_content:
            print("Decoded content:")
            print(decoded_content)
        else:
            print("Failed to decode the content.")
    except Exception as e:
        print("Error parsing email: ", e)

if __name__ == "__main__":
    # 假设这是你的带有base64编码内容的邮件
    f = open("Re_ New Account.eml",'r',encoding='utf-8')
    content = f.read()
    parse_email(content)
    f.close()
