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


  


  

[image1]: <data:image/png;base64,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>