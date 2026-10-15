-- Migración 001: tabla `ahorros` (flujo "Registrar ahorro" de la app).
-- Es idempotente: se puede ejecutar sobre una base que ya tiene datos (no borra nada).
--   mysql -u <usuario> -p <base> < db/migraciones/001_ahorros.sql
-- Una base nueva ya la trae en db/schema.sql. Ya incluye el método REDONDEO; las bases donde se aplicó
-- una versión anterior de este archivo usan 002_ahorros_metodo_redondeo.sql.

CREATE TABLE IF NOT EXISTS `ahorros` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `usuario_id` int unsigned NOT NULL,
  `categoria` enum('CUENTA','CDT','FONDO_INVERSION','PROGRAMADO','ALCANCIA','OTRO') NOT NULL COMMENT 'Categoría elegida en "Registrar ahorro"',
  `subtipo` varchar(30) NOT NULL COMMENT 'Subtipo dentro de la categoría (p. ej. EFECTIVO, VIAJE en OTRO)',
  `nombre` varchar(100) NOT NULL,
  `descripcion` varchar(200) DEFAULT NULL,
  `monto_actual` decimal(15,2) NOT NULL DEFAULT '0.00',
  `moneda` char(3) NOT NULL DEFAULT 'COP',
  `es_meta` tinyint(1) NOT NULL DEFAULT '0',
  `meta_nombre` varchar(100) DEFAULT NULL,
  `monto_objetivo` decimal(15,2) DEFAULT NULL,
  `fecha_objetivo` date DEFAULT NULL,
  `metodo` enum('MANUAL','PROGRAMADO','REDONDEO','AUTOMATICO') NOT NULL DEFAULT 'MANUAL',
  `estado` enum('ACTIVA','CUMPLIDA','CANCELADA') NOT NULL DEFAULT 'ACTIVA',
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_ahorros_usuario_estado` (`usuario_id`,`estado`),
  CONSTRAINT `fk_ahorros_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_ahorros_actual` CHECK ((`monto_actual` >= 0)),
  CONSTRAINT `chk_ahorros_objetivo` CHECK (((`monto_objetivo` is null) or (`monto_objetivo` > 0)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
