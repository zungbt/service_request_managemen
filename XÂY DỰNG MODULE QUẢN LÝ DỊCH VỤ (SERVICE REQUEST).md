ODOO 17  
XÂY DỰNG MODULE QUẢN LÝ DỊCH VỤ (SERVICE REQUEST) 

## **Mục tiêu**

Xây dựng module quản lý yêu cầu dịch vụ nội bộ, có các chức năng:

* Tạo yêu cầu (giống báo giá nhẹ)  
* Theo dõi trạng thái  
* In PDF  
* Gửi email  
* Nhắc việc tự động

1\. Tên module (service\_request\_management)

# 2\. Chức năng chính

## 2.1 Model chính: service.request

### Các field cơ bản:

* name (Char) – Mã yêu cầu (auto sequence)  
* customer\_id (Many2one → res.partner)  
* service\_type (Selection)  
  * repair  
  * consulting  
  * installation  
* description (Text)  
* request\_date (Datetime)  
* deadline (Datetime)  
* state (Selection)  
  * draft  
  * submitted  
  * approved  
  * done  
  * cancelled  
* assigned\_to (Many2one → res.users)  
* amount\_estimate (Float)  
* note (Text)  
    
  


  ## 2.2 Workflow (trạng thái)

  ## Draft → Submitted → Approved → Done

  ## Có thể Cancel bất kỳ lúc nào

  ## 👉 Yêu cầu:

  ## Tạo button chuyển trạng thái

  ## Có validation:

  ## Không submit nếu chưa có customer

  ## Không approve nếu chưa có assigned\_to

  ## 2.3 Sequence

  ## Tự động sinh mã: (vd: SR0001, SR0002,...)

# 3\. In PDF (QWeb Report)

## **Yêu cầu:**

* Tạo report: (Service Request Report)  
* Nội dung gồm:  
  * Mã yêu cầu  
  * Khách hàng  
  * Loại dịch vụ  
  * Mô tả  
  * Người phụ trách  
  * Deadline  
  * Chi phí dự kiến  
* Thêm logo công ty  
* Format header, footer giống báo giá  
  


# 4\. Gửi Email

## **Khi nào gửi:**

* Khi **Submit request**  
* Khi **Approved**

  ## **Nội dung email:**

* Tiêu đề: \[Service Request\] SR0001 đã được tạo

  Nội dung:

* Thông tin request  
* Link tới record

5\. Reminder (Scheduled Action)

## **Yêu cầu:**

Tạo cron job:

* Chạy mỗi ngày  
* Gửi email nhắc khi:  
  * Deadline còn 1 ngày  
  * State chưa phải done  
     Nội dung email: (Bạn có 1 yêu cầu dịch vụ sắp đến hạn)  
    

6\. Giao diện (Views)

## **6.1 Tree view**

* name  
* customer  
* service\_type  
* state  
* deadline

  ## **6.2 Form view**

* Header: buttons \+ statusbar  
* Group thông tin:  
  * Thông tin khách hàng  
  * Thông tin dịch vụ  
  * Deadline \+ assigned  
  * Có chatter

7\. Phân quyền (Security)

## **Tạo 2 nhóm:**

* Service User  
* Service Manager  
  ![][image1]


  


  
