--Lấy all ticket của DVKH xử lý trong 2025 ko lấy các gian hàng test
            select DISTINCT
                tro.ticketid as ticket_id,
                tro.ticket_no,
                tro.title,
                cf.cf_total_work_types,
                crm.status,
                crm.description,
                crm.version,
                from_utc_timestamp(crm.createdtime, 'Asia/Ho_Chi_Minh') created_time,
                MONTH(crm.createdtime) as created_month,
                from_utc_timestamp(crm.modifiedtime, 'Asia/Ho_Chi_Minh') modifiedtime,
                cf.cf_ticket_type,
                crm.smcreatorid,
                user2.last_name as smcreatorid_name,
                crm.smownerid,
                user1.last_name as smownerid_name,
                user2.source,
                SPLIT(work.worktype , '\\|')[0] AS worktype,
                crm.retailer_id,
                IFNULL(cf_total_process_time/60, 9999) AS process_time,
                ra.*
            from kvcrm_warehouse.vtiger_crmentity_fact crm
            join kvcrm_warehouse.vtiger_troubleticket_dim tro               on tro.ticketid = crm.crmid
            join kvcrm_warehouse.vtiger_ticketcf_dim cf                     ON tro.ticketid = cf.ticketid
            join kvcrm_warehouse.ticket_work_type_dim work                  ON work.ticketid = cf.ticketid
            left join kvcrm_mart.user_team  user1 on user1.userid = crm.smownerid
            left JOIN kvcrm_mart.user_team user2 on user2.userid = crm.smcreatorid
            left join kvcrm_mart.customer_service_month_kpi kpi on kpi.user_id = crm.smownerid
            left join  kv_master.retailer_active ra on ra.real_key = crm.retailer_id
            where 1 = 1
                and work.status not in ('Rejected','Duplicate')
                and cast(left(user1.last_name, 2) as int) in ('81','82','83','84','86','88')
                and crm.createdtime >= '2025-01-01'
                and crm.deleted = 0
                and crm.retailer_id not in (0,500339831 , 200105647, 200048962)