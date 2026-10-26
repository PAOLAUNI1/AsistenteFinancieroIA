-- Migración 003: ahorro programado (flujo "Registrar ahorro programado" de la app).
-- Agrega el método de ahorro "RECORDATORIO" y la tabla de detalle `ahorro_programado` (1:1 con `ahorros`):
-- cuánto se ahorra por periodo, cada cuánto y desde qué fecha.
-- Es idempotente: se puede ejecutar más de una vez y no toca los datos.
--   mysql -u <usuario> -p <base> < db/migraciones/003_ahorro_programado.sql
-- Requiere haber aplicado antes 001_ahorros.sql (y 002 si 001 era la versión anterior, sin REDONDEO).
-- Una base nueva ya lo trae en db/schema.sql.

ALTER TABLE `ahorros`
  MODIFY COLUMN `metodo` enum('MANUAL','PROGRAMADO','REDONDEO','AUTOMATICO','RECORDATORIO') NOT NULL DEFAULT 'MANUAL';

CREATE TABLE IF NOT EXISTS `ahorro_programado` (
  `ahorro_id` int unsigned NOT NULL,
  `monto_periodo` decimal(15,2) NOT NULL COMMENT 'Cuánto se ahorra en cada periodo',
  `periodicidad` enum('SEMANAL','QUINCENAL','MENSUAL') NOT NULL,
  `fecha_inicio` date NOT NULL,
  PRIMARY KEY (`ahorro_id`),
  CONSTRAINT `fk_ahorro_programado_ahorro` FOREIGN KEY (`ahorro_id`) REFERENCES `ahorros` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_ahorro_programado_monto` CHECK ((`monto_periodo` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
