-- Migración 002: el método de ahorro "REDONDEO" (alcancía: ahorrar el cambio de los gastos).
-- Es idempotente: se puede ejecutar más de una vez y no toca los datos.
--   mysql -u <usuario> -p <base> < db/migraciones/002_ahorros_metodo_redondeo.sql
-- Requiere haber aplicado antes 001_ahorros.sql. Una base nueva ya la trae en db/schema.sql.

ALTER TABLE `ahorros`
  MODIFY COLUMN `metodo` enum('MANUAL','PROGRAMADO','REDONDEO','AUTOMATICO') NOT NULL DEFAULT 'MANUAL';
