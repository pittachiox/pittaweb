# pittaweb
สรุปโค้ดเว็บ To-Do List โทนหวานๆ 🎀 (ใช้ Flask + CSS Framework)

เว็บนี้เป็น To-Do List ที่มี โทนสีชมพู น่ารัก 💖 และใช้ Flask เป็น Backend รองรับการลงทะเบียน, ล็อกอิน, จัดการ Task และอัปโหลดไฟล์ พร้อมกับ CSS Framework (เช่น Bootstrap) เพื่อให้ UI ดูดี  เหมาะกับคนที่ชอบเว็บโทนหวานๆ ใช้จัดการงานส่วนตัว! 🎀

โครงสร้างหลักของเว็บ
1️. ระบบล็อกอิน/สมัครสมาชิก (Flask-Login)
✅ /register – ผู้ใช้สมัครสมาชิก และบันทึกข้อมูลในฐานข้อมูล
✅ /login – ผู้ใช้เข้าสู่ระบบ
✅ /logout – ออกจากระบบ
✅ @login_required – ป้องกันไม่ให้เข้าถึงบางหน้าโดยไม่ล็อกอิน
💡 เมื่อเข้าสู่ระบบสำเร็จ → ไปหน้า /introduce (แนะนำเว็บ)

2️. หน้าหลัก (Dashboard) – /
✅ ดึง Task ของผู้ใช้มาแสดง (เรียงตาม Due Date)
✅ แสดงสถานะงาน (Pending / Completed)

3️. จัดการ Task
📝 /tasks/create – เพิ่ม Task ใหม่
✏️ /tasks/<task_id>/update – แก้ไข Task
✅ /tasks/<task_id>/complete – เปลี่ยนสถานะ Task เป็น Completed
🔄 /tasks/<task_id>/toggle_complete – สลับสถานะ Pending / Completed
❌ /tasks/<task_id>/delete – ลบ Task
📌 ใช้ Flask Form (TaskForm) จัดการข้อมูล Task

4️. โปรไฟล์ผู้ใช้ (UserProfile)
👤 /detail – ดูโปรไฟล์
🔧 /update_profile – แก้ไขโปรไฟล์ (เพิ่มชื่อเล่น, คณะ, อิโมจิ ฯลฯ)

5. ปฏิทินเลือกวัน (calendar.html)
📅 /calendar – แสดงปฏิทินให้เลือก Due Date
เมื่อเลือกวันแล้ว → ไปหน้า /tasks/create พร้อมกำหนดวันที่

🎨 การใช้ CSS Framework (Bootstrap) ตกแต่ง UI

✅ ปรับปุ่ม, ตาราง และ Layout ให้ดูน่ารัก
✅ ใช้สีชมพู-ขาวโทนพาสเทล
✅ ปรับแต่ง Hover Effect และ Animation