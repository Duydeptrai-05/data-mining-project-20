-- 00-init-roles.sql | Chủ: B | Chạy MỘT LẦN bằng user có quyền tạo role (superuser).
-- Nếu dùng Docker theo README thì user dm đã là superuser nên chạy được luôn.
-- Chỉ tạo role + quyền kết nối. Quyền đọc schema mart được cấp ở CUỐI 05-mart-views.sql
-- (vì 05 dựng lại các đối tượng trong mart mỗi lần chạy).

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'superset_ro') THEN
    CREATE ROLE superset_ro LOGIN PASSWORD 'superset_ro';
  END IF;
END
$$;

DO $$
BEGIN
  EXECUTE 'GRANT CONNECT ON DATABASE ' || quote_ident(current_database()) || ' TO superset_ro';
END
$$;
