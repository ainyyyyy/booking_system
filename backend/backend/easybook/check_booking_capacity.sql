-- Ограничивает суммарное количество бронирований (quantity) на интервале
-- до значения capacity, определяемого:
--   1) по таблице capacity_window (если есть пересечение);
--   2) иначе по resource.max_capacity.
--
-- При превышении лимита вызывается exception

CREATE OR REPLACE FUNCTION check_booking_capacity()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    effective_capacity integer;
    capacity_row       record;
BEGIN
    -- Определяем ёмкость на рассматриваемом промежутке
    SELECT cw.capacity
      INTO capacity_row
      FROM easybook_capacitywindow cw
     WHERE cw.resource_id = NEW.resource_id
       AND cw.timerange && NEW.timerange
     ORDER BY cw.capacity 
     LIMIT 1;

    IF capacity_row IS NULL THEN
        SELECT max_capacity
          INTO effective_capacity
          FROM easybook_resource
         WHERE id = NEW.resource_id;
    ELSE
        effective_capacity := capacity_row.capacity;
    END IF;

    -- Считаем, сколько уже занято (исключая текущую строку)
    SELECT COALESCE(SUM(quantity), 0)
      INTO STRICT capacity_row
      FROM easybook_booking b
     WHERE b.resource_id = NEW.resource_id
       AND b.timerange && NEW.timerange
       AND (TG_OP = 'INSERT' OR b.id <> NEW.id);

    IF capacity_row.sum + NEW.quantity > effective_capacity THEN
        RAISE EXCEPTION
          USING MESSAGE = format(
                'Not enough capacity: requested %s, already used %s, limit %s',
                NEW.quantity,
                capacity_row.sum,
                effective_capacity
            ),
                ERRCODE = 'integrity_constraint_violation';
    END IF;

    RETURN NEW;
END;
$$;


DROP TRIGGER IF EXISTS prevent_overbooking ON easybook_booking;

CREATE TRIGGER prevent_overbooking
BEFORE INSERT OR UPDATE ON easybook_booking
FOR EACH ROW
EXECUTE FUNCTION check_booking_capacity();
