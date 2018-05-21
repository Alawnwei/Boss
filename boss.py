__author__ = "woody"

# -*- coding: utf-8 -*-
# !/usr/bin/python

import json
import sys
import time

import requests
import yagmail
from aip import AipOcr
from bs4 import BeautifulSoup


class Boss(object):
    latest_msg = None
    user_id = None
    mail = False
    mid = None
    resume_dict = {}

    def __init__(self):
        try:
            with open("./config.json", encoding="utf-8") as config:
                self.conf = json.load(config)
            # 检查关键key是否存在
            keys = ["app_id", "user", "password", "api_key", "secret_key",
                    "login_url", "host", "login_json", "msg_page"]
            if set(keys) & set(self.conf.keys()) != set(keys):
                raise Exception("配置文件缺少关键参数, 请检查!")
            self.session = requests.Session()  # 创建新session
        except Exception as e:
            print("解析配置文件出错, 请检查config.json! ERROR: {}".format(str(e)))
            sys.exit(-1)  # 程序自动退出

    def run(self):
        self.login()
        self.listen()

    def listen(self):
        while True:
            self.get_msg()
            time.sleep(self.conf["delay"] * 60)

    def get_msg(self):
        self.mail = False
        r = self.session.get(self.conf["msg_page"])
        data = self.get_latest_info(r.json().get("data", []))
        if not data:
            print("您当前没有新消息, 持续监听中!")
            return
        # 获取最新消息
        newest = data[0]
        bossId = newest['uid']
        job_info = self.get_job_info(bossId)
        his_msg = self.get_latest_msg(job_info["encryptBossId"])
        info = "公司: {}\n沟通人姓名: {}\n沟通人职位:{}\n薪资范围: {}\n聊天记录:\n{}\n职位名称: {}\n" \
               "Base: {}\n学历要求: {}\n经验要求: {}\n职位描述: {}\n职位要求: {}\n".format(
            job_info["company"], newest["name"], newest["title"], job_info["rate"],
            his_msg, job_info["pos"], job_info["loc"], job_info["degree"],
            job_info["exp"], job_info["posDesc"]
        )
        if self.mail:
            mail_info = "您有Boss/未来领导/猎头勾搭啦!!!~~~~~~\n" + info
            self.send_mail(mail_info, bossId)
            print("发送邮件成功!")
        print("您的最新消息为: \n{}".format(info))

    def send_resume(self, bossId):
        if self.conf["auto_resume"] and not self.resume_dict.get(bossId, False) and self.mail:
            r = self.session.get(self.conf["resume_url"], params=dict(bossId=bossId))
            if r.json()["rescode"] == 1:
                # 发送简历成功
                self.resume_dict[bossId] = True
                msg = "简历发送成功!"
            else:
                msg = "自动发送简历失败! Msg: {}".format(r.json()["resmsg"])
        else:
            msg = "未开启自动发送简历功能或已发送给该Boss~~"
        return msg

    def send_mail(self, mail_info, bossId):
        try:
            yag = yagmail.SMTP(user=self.conf["sender"], password=self.conf["sender_pwd"],
                               host='smtp.126.com')
            yag.send(self.conf["receiver"], '有Boss给您发消息啦!!!状态: {}'.format(self.send_resume(bossId)),
                     mail_info.split("\n"))
        except Exception as e:
            print("发送邮件失败, 原因: {}".format(str(e)))

    def get_latest_msg(self, bossId):
        r = self.session.get(self.conf["his_msg"], params=dict(bossId=bossId, maxMsgId=0, c=5, page=1, loading=True))
        mes = r.json().get("messages", [])
        if mes:
            if mes[-1]["from"]["uid"] != self.user_id and self.mid is not None \
                    and mes[-1]["mid"] != self.mid:
                self.mail = True  # 只有当最后一条消息不是自己发送才发邮件
            self.mid = mes[-1]["mid"]

        mes = [m.get("pushText", "") for m in mes][::-1]
        mes.remove("")
        return "\n".join(mes)

    def get_job_info(self, bossId):
        # 解析job信息通过jobId
        r = self.session.get(self.conf["job_json"], params=dict(bossId=bossId))
        data, job = r.json()["data"], r.json()["job"]
        return {
            "company": data.get("companyName"),
            "encryptBossId": data.get("encryptBossId"),
            "degree": job.get("degreeName"),
            "exp": job.get("experienceName"),
            "loc": job.get("locationName"),
            "rate": "{}K-{}K".format(job.get("lowSalary"), job.get("highSalary")),
            "pos": job.get("positionName"),
            "posDesc": job.get("postDescription")
        }

    def get_latest_info(self, d):
        # 获取最新消息
        return sorted([dict(jobId=x.get("jobId"), lastTime=x.get("lastTime"), name=x.get("name"), uid=x.get("uid"),
                            lastMsg=x.get("lastMsg"), company=x.get("companyName"), title=x.get("title"))
                       for x in d if x.get("name") not in self.conf["black_list"]], key=lambda y: y.get("lastTime"),
                      reverse=True)

    def verify_code(self, base_code):
        client = AipOcr(self.conf["app_id"], self.conf["api_key"], self.conf["secret_key"])
        options = dict(language_type="ENG")
        code = client.basicGeneral(base_code, options)
        words = code.get("words_result", [])
        if words:
            code = words[0]["words"]
            code = code.replace(" ", "")
            if len(code) == 4:
                return code
            else:
                print("百度API识别验证码为{}, 重新尝试...".format(code))
        return None

    def login(self):
        while True:
            session = self.session
            r = session.get(self.conf["login_url"])
            soup = BeautifulSoup(r.text, "html5lib")
            random_key = soup.select(".sign-pwd .randomkey")
            image = soup.select(".sign-pwd .row-code img")
            if random_key and image:
                rm_key = random_key[0].get("value")
                code_url = self.conf["host"] + image[0].get('src')
                r = requests.get(code_url)
                code = self.verify_code(r.content)
                if code is None:
                    print("等待{}秒, 如需修改请在config.json配置retry字段...".format(self.conf["retry"]))
                    time.sleep(self.conf["retry"])  # N秒后重试
                    continue
                else:
                    data = {
                        "pk": "cpc_user_sign_up",
                        "regionCode": "+86",
                        "account": self.conf["user"],
                        "password": self.conf["password"],
                        "captcha": code,
                        "randomKey": rm_key
                    }
                    r = self.session.post(url=self.conf["login_json"], data=data)
                    if r.json().get("rescode") == 1:  # 登录成功
                        print("恭喜您登录成功!")
                        self.user_id = r.json()["userId"]
                        break
                    else:
                        print("登录失败, Msg: {}".format(r.json().get("resmsg")))
                        if r.json().get("rescode") == 7:
                            print("请在config.json重新设置您的用户密码!")
                            sys.exit(-1)


if __name__ == "__main__":
    bs = Boss()
    bs.run()
