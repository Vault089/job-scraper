import json, urllib.request, base64, time

API_KEY = "am_us_inbox_8d3e0b8acef9ca812ff124ad7d1b9de4cdaf66d7ac8d1efbf1e065b747ba5412"
INBOX = "ford-hermes@agentmail.to"
COVER_DIR = "/home/amrba/job_scraper/cover_letters"
DOC_DIR = "/home/amrba/job_scraper/documents"

def encode_file(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def send_email(to, subject, text, attachments):
    payload = {
        "to": [to],
        "cc": ["amrbadr15@gmail.com"],
        "subject": subject,
        "text": text,
        "attachments": attachments
    }
    req = urllib.request.Request(
        f"https://api.agentmail.to/v0/inboxes/{INBOX}/messages/send",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode()).get("message_id", "unknown")

applications = [
    ("📋 REVIEW 1/6: Middle School English Teacher @ Beijing Yingcai Dingsheng (Zhongshan)", "info@ycditals.com", "1_Beijing Yingcai Ding_Middle School English Teacher.docx", """📋 REVIEW COPY — NOT YET SENT TO RECRUITER

Recipient: info@ycditals.com | Position: Middle School English Teacher | Company: Beijing Yingcai Dingsheng Education Technology Co., Ltd.
Location: Zhongshan | Salary: 23000-27000 CNY/month

---

Hi,

Hope you're well. I'm applying for the Middle School English Teacher position at Beijing Yingcai Dingsheng Education Technology Co., Ltd. in Zhongshan.

I bring 6+ years of teaching experience across Business, Economics, and exam preparation (IGCSE, IB, A-Level), with a PGCE from Liverpool John Moores, an MA in Education, and an MA in AI for Business. I'm particularly focused on Business English and have worked extensively with students across Asia who need to master Business and Economics concepts in a non-native English environment.

Currently ready to relocate wherever the right opportunity takes me. Happy to share my CV or jump on a call.

Best,
Ford
+84 898091337
WeChat: Ford1702"""),
    ("📋 REVIEW 2/6: English Teachers @ Beijing Academy (Beijing) — 25000-35000 CNY", "zhaopin@baisonghua.com", "4_Beijing Academy Inte_English Teachers for Beijing A.docx", """📋 REVIEW COPY — NOT YET SENT TO RECRUITER

Recipient: zhaopin@baisonghua.com | Position: English Teachers for Beijing Academy | Company: Beijing Academy International Division
Location: Beijing | Salary: 25000-35000 CNY/month

---

Hi,

Hope you're well. I'm applying for the English Teachers for Beijing Academy position at Beijing Academy International Division in Beijing.

I bring 6+ years of teaching experience across Business, Economics, and exam preparation (IGCSE, IB, A-Level), with a PGCE from Liverpool John Moores, an MA in Education, and an MA in AI for Business. I'm particularly focused on Business English and have worked extensively with students across Asia who need to master Business and Economics concepts in a non-native English environment.

Currently ready to relocate wherever the right opportunity takes me. Happy to share my CV or jump on a call.

Best,
Ford
+84 898091337
WeChat: Ford1702"""),
    ("📋 REVIEW 3/6: English Teachers Needed @ Beijing Academy (Beijing) — 25000-38000 CNY", "zhaopin@baisonghua.com", "5_Beijing Academy Inte_English Teachers Needed  Beiji.docx", """📋 REVIEW COPY — NOT YET SENT TO RECRUITER

Recipient: zhaopin@baisonghua.com | Position: English Teachers Needed Beijing | Company: Beijing Academy International Division
Location: Beijing | Salary: 25000-38000 CNY/month

---

Hi,

Hope you're well. I'm applying for the English Teachers Needed position at Beijing Academy International Division in Beijing.

I bring 6+ years of teaching experience across Business, Economics, and exam preparation (IGCSE, IB, A-Level), with a PGCE from Liverpool John Moores, an MA in Education, and an MA in AI for Business. I'm particularly focused on Business English and have worked extensively with students across Asia who need to master Business and Economics concepts in a non-native English environment.

Currently ready to relocate wherever the right opportunity takes me. Happy to share my CV or jump on a call.

Best,
Ford
+84 898091337
WeChat: Ford1702"""),
    ("📋 REVIEW 4/6: Shanghai University English Teacher @ New Peak Recruitment", "Info@newpeakrecruitment.com", "6_New Peak Recruitment_Shanghai University English Te.docx", """📋 REVIEW COPY — NOT YET SENT TO RECRUITER

Recipient: Info@newpeakrecruitment.com | Position: Shanghai University English Teacher | Company: New Peak Recruitment
Location: Shanghai | Salary: 16000-18000 CNY/month

---

Hi,

Hope you're well. I'm applying for the Shanghai University English Teacher position via New Peak Recruitment in Shanghai.

I bring 6+ years of teaching experience across Business, Economics, and exam preparation (IGCSE, IB, A-Level), with a PGCE from Liverpool John Moores, an MA in Education, and an MA in AI for Business. I'm particularly focused on Business English and have worked extensively with students across Asia who need to master Business and Economics concepts in a non-native English environment.

Currently ready to relocate wherever the right opportunity takes me. Happy to share my CV or jump on a call.

Best,
Ford
+84 898091337
WeChat: Ford1702"""),
    ("📋 REVIEW 5/6: College Oral English Teacher @ Wuhan Karla Business (Xingtai)", "hr@karlaedu.cn", "7_Wuhan Karla Business_College Oral English Teacher n.docx", """📋 REVIEW COPY — NOT YET SENT TO RECRUITER

Recipient: hr@karlaedu.cn | Position: College Oral English Teacher needed-Sep | Company: Wuhan Karla Business Information Consulting Co. Ltd
Location: Xingtai | Salary: 15000-19000 CNY/month

---

Hi,

Hope you're well. I'm applying for the College Oral English Teacher position at Wuhan Karla Business Information Consulting Co. Ltd in Xingtai.

I bring 6+ years of teaching experience across Business, Economics, and exam preparation (IGCSE, IB, A-Level), with a PGCE from Liverpool John Moores, an MA in Education, and an MA in AI for Business. I'm particularly focused on Business English and have worked extensively with students across Asia who need to master Business and Economics concepts in a non-native English environment.

Currently ready to relocate wherever the right opportunity takes me. Happy to share my CV or jump on a call.

Best,
Ford
+84 898091337
WeChat: Ford1702"""),
    ("📋 REVIEW 6/6: A-Level English Teacher @ Guangzhou Elite Education (Guangzhou) — ⚠️ guessed email", "gz.elite.edu@gmail.com", "2_Guangzhou Elite Educ_A-Level English Teacher.docx", """📋 REVIEW COPY — NOT YET SENT TO RECRUITER

⚠️ WARNING: No corporate email found for Guangzhou Elite Education. Sending to gz.elite.edu@gmail.com (best-effort guess). Please verify before I fire to recruiter.

Recipient: gz.elite.edu@gmail.com | Position: A-Level English Teacher | Company: Guangzhou Elite Education Co., Ltd.
Location: Guangzhou | Salary: 25000-33000 CNY/month

---

Hi,

Hope you're well. I'm applying for the A-Level English Teacher position at Guangzhou Elite Education Co., Ltd. in Guangzhou.

I bring 6+ years of teaching experience across Business, Economics, and exam preparation (IGCSE, IB, A-Level), with a PGCE from Liverpool John Moores, an MA in Education, and an MA in AI for Business. I'm particularly focused on Business English and have worked extensively with students across Asia who need to master Business and Economics concepts in a non-native English environment.

Currently ready to relocate wherever the right opportunity takes me. Happy to share my CV or jump on a call.

Best,
Ford
+84 898091337
WeChat: Ford1702"""),
]

sent_ids = []
for i, (subject, recruiter, cover_file, body) in enumerate(applications, 1):
    try:
        attachments = [
            {"filename": "Amro_Badr_CV_May26.pdf", "content": encode_file(f"{DOC_DIR}/Amro_Badr_CV_May26.pdf"), "contentType": "application/pdf"},
            {"filename": "Amro_photo.png", "content": encode_file(f"{DOC_DIR}/Amro_photo.png"), "contentType": "image/png"},
            {"filename": cover_file, "content": encode_file(f"{COVER_DIR}/{cover_file}"), "contentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
        ]
        msg_id = send_email("amrbadr15@gmail.com", subject, body, attachments)
        sent_ids.append(msg_id)
        print(f"✅ {i}/6 sent — {subject[:70]}")
        print(f"   Message ID: {msg_id}")
        time.sleep(1.5)
    except Exception as e:
        print(f"❌ {i}/6 FAILED: {e}")

print(f"\n{'='*50}")
print(f"RESULT: {len(sent_ids)}/6 review emails sent to amrbadr15@gmail.com")