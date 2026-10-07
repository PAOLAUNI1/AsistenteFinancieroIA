-- Esquema de la base `asistente_financiero` (MySQL 8).
-- Generado desde la base de desarrollo. Se ejecuta sobre una base vacía ya creada:
--   mysql -u <usuario> -p <base> < db/schema.sql
-- Después se cargan los catálogos con db/seed.sql.

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
DROP TABLE IF EXISTS `aportes_meta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `aportes_meta` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `meta_id` int unsigned NOT NULL,
  `monto` decimal(15,2) NOT NULL COMMENT 'Negativo = retiro',
  `fecha` date NOT NULL DEFAULT (curdate()),
  `observacion` varchar(200) DEFAULT NULL,
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_aportes_meta_fecha` (`meta_id`,`fecha`),
  CONSTRAINT `fk_aportes_meta` FOREIGN KEY (`meta_id`) REFERENCES `metas_ahorro` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_aportes_monto` CHECK ((`monto` <> 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `categorias_gasto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias_gasto` (
  `id` tinyint unsigned NOT NULL AUTO_INCREMENT,
  `codigo` varchar(30) NOT NULL,
  `nombre` varchar(60) NOT NULL,
  `grupo` enum('HOGAR','FAMILIA_EDUCACION','PERSONAL') NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_categorias_gasto_codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `compras_tarjeta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `compras_tarjeta` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `deuda_id` int unsigned NOT NULL COMMENT 'Debe apuntar a una deuda tipo TARJETA',
  `descripcion` varchar(150) NOT NULL,
  `monto` decimal(15,2) NOT NULL,
  `fecha_compra` date NOT NULL,
  `numero_cuotas` smallint unsigned NOT NULL DEFAULT '1',
  `cuotas_pagadas` smallint unsigned NOT NULL DEFAULT '0',
  `genera_intereses` tinyint(1) NOT NULL DEFAULT '1',
  `tasa_interes` decimal(7,4) DEFAULT NULL,
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_compras_tarjeta_fecha` (`deuda_id`,`fecha_compra`),
  CONSTRAINT `fk_compras_tarjeta_deuda` FOREIGN KEY (`deuda_id`) REFERENCES `deuda_tarjeta` (`deuda_id`) ON DELETE CASCADE,
  CONSTRAINT `chk_compras_cuotas` CHECK (((`numero_cuotas` >= 1) and (`cuotas_pagadas` <= `numero_cuotas`))),
  CONSTRAINT `chk_compras_monto` CHECK ((`monto` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `deuda_educativo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deuda_educativo` (
  `deuda_id` int unsigned NOT NULL,
  `institucion` varchar(120) DEFAULT NULL,
  `programa` varchar(120) DEFAULT NULL,
  `modalidad` varchar(80) DEFAULT NULL COMMENT 'Ej.: ICETEX, crédito directo con la universidad',
  `beneficiario` varchar(100) DEFAULT NULL COMMENT 'Usuario o hijo que estudia',
  PRIMARY KEY (`deuda_id`),
  CONSTRAINT `fk_deuda_educativo_deuda` FOREIGN KEY (`deuda_id`) REFERENCES `deudas` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `deuda_otro`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deuda_otro` (
  `deuda_id` int unsigned NOT NULL,
  `tipo_credito` varchar(40) NOT NULL,
  PRIMARY KEY (`deuda_id`),
  CONSTRAINT `fk_deuda_otro_deuda` FOREIGN KEY (`deuda_id`) REFERENCES `deudas` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `deuda_tarjeta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deuda_tarjeta` (
  `deuda_id` int unsigned NOT NULL,
  `cupo_total` decimal(15,2) NOT NULL,
  `dia_corte` tinyint unsigned NOT NULL,
  `dia_pago` tinyint unsigned NOT NULL,
  `franquicia` varchar(30) DEFAULT NULL COMMENT 'Visa, Mastercard, etc.',
  `ultimos_digitos` char(4) DEFAULT NULL COMMENT 'Solo los 4 últimos, nunca el número completo',
  PRIMARY KEY (`deuda_id`),
  CONSTRAINT `fk_deuda_tarjeta_deuda` FOREIGN KEY (`deuda_id`) REFERENCES `deudas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_tarjeta_corte` CHECK ((`dia_corte` between 1 and 31)),
  CONSTRAINT `chk_tarjeta_cupo` CHECK ((`cupo_total` > 0)),
  CONSTRAINT `chk_tarjeta_pago` CHECK ((`dia_pago` between 1 and 31))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `deuda_vehiculo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deuda_vehiculo` (
  `deuda_id` int unsigned NOT NULL,
  `tipo_vehiculo` enum('AUTOMOVIL','MOTOCICLETA','CAMIONETA','OTRO') NOT NULL DEFAULT 'AUTOMOVIL',
  `marca` varchar(50) DEFAULT NULL,
  `modelo` varchar(50) DEFAULT NULL,
  `anio` smallint unsigned DEFAULT NULL,
  `placa` varchar(10) DEFAULT NULL,
  `valor_vehiculo` decimal(15,2) DEFAULT NULL,
  `cuota_inicial` decimal(15,2) DEFAULT NULL,
  PRIMARY KEY (`deuda_id`),
  CONSTRAINT `fk_deuda_vehiculo_deuda` FOREIGN KEY (`deuda_id`) REFERENCES `deudas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_vehiculo_anio` CHECK (((`anio` is null) or (`anio` between 1950 and 2100))),
  CONSTRAINT `chk_vehiculo_valor` CHECK (((`valor_vehiculo` is null) or (`valor_vehiculo` > 0)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `deudas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deudas` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `usuario_id` int unsigned NOT NULL,
  `tipo_deuda_id` tinyint unsigned NOT NULL,
  `entidad` varchar(100) NOT NULL COMMENT 'Entidad financiera o prestamista (préstamo personal)',
  `nombre` varchar(100) DEFAULT NULL,
  `monto_inicial` decimal(15,2) DEFAULT NULL COMMENT 'NULL en tarjeta: se usa cupo_total',
  `saldo_actual` decimal(15,2) NOT NULL,
  `tiene_intereses` tinyint(1) NOT NULL DEFAULT '1',
  `tasa_interes` decimal(7,4) DEFAULT NULL,
  `periodicidad_tasa` enum('EA','MENSUAL') DEFAULT NULL,
  `tipo_tasa` enum('FIJA','VARIABLE') DEFAULT NULL,
  `plazo_meses` smallint unsigned DEFAULT NULL COMMENT 'años*12 + meses (lo calcula el backend)',
  `valor_cuota` decimal(15,2) DEFAULT NULL,
  `proxima_cuota` smallint unsigned DEFAULT NULL COMMENT 'Número de la próxima cuota a pagar',
  `fecha_proximo_pago` date DEFAULT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `descripcion` varchar(200) DEFAULT NULL,
  `estado` enum('ACTIVA','PAGADA','CANCELADA') NOT NULL DEFAULT 'ACTIVA',
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_deudas_usuario_estado` (`usuario_id`,`estado`),
  KEY `idx_deudas_proximo_pago` (`fecha_proximo_pago`),
  KEY `fk_deudas_tipo` (`tipo_deuda_id`),
  CONSTRAINT `fk_deudas_tipo` FOREIGN KEY (`tipo_deuda_id`) REFERENCES `tipos_deuda` (`id`),
  CONSTRAINT `fk_deudas_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_deudas_cuota` CHECK (((`valor_cuota` is null) or (`valor_cuota` > 0))),
  CONSTRAINT `chk_deudas_entidad` CHECK ((char_length(trim(`entidad`)) > 0)),
  CONSTRAINT `chk_deudas_monto` CHECK (((`monto_inicial` is null) or (`monto_inicial` > 0))),
  CONSTRAINT `chk_deudas_plazo` CHECK (((`plazo_meses` is null) or (`plazo_meses` > 0))),
  CONSTRAINT `chk_deudas_prox_cuota` CHECK (((`proxima_cuota` is null) or ((`proxima_cuota` >= 1) and ((`plazo_meses` is null) or (`proxima_cuota` <= `plazo_meses`))))),
  CONSTRAINT `chk_deudas_saldo` CHECK ((`saldo_actual` >= 0)),
  CONSTRAINT `chk_deudas_saldo_monto` CHECK (((`monto_inicial` is null) or (`saldo_actual` <= `monto_inicial`))),
  CONSTRAINT `chk_deudas_tasa` CHECK ((((`tiene_intereses` = false) and ((`tasa_interes` is null) or (`tasa_interes` = 0))) or ((`tiene_intereses` = true) and ((`tasa_interes` is null) or (`tasa_interes` > 0)))))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `gastos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gastos` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `usuario_id` int unsigned NOT NULL,
  `categoria_id` tinyint unsigned NOT NULL,
  `descripcion` varchar(150) DEFAULT NULL,
  `monto` decimal(15,2) NOT NULL,
  `periodicidad` enum('MENSUAL','UNICO') NOT NULL DEFAULT 'MENSUAL',
  `fecha` date NOT NULL DEFAULT (curdate()),
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_gastos_usuario_fecha` (`usuario_id`,`fecha`),
  KEY `fk_gastos_categoria` (`categoria_id`),
  CONSTRAINT `fk_gastos_categoria` FOREIGN KEY (`categoria_id`) REFERENCES `categorias_gasto` (`id`),
  CONSTRAINT `fk_gastos_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_gastos_monto` CHECK ((`monto` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `ingresos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ingresos` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `usuario_id` int unsigned NOT NULL,
  `tipo` enum('SALARIO','OTRO') NOT NULL,
  `descripcion` varchar(150) DEFAULT NULL,
  `monto` decimal(15,2) NOT NULL,
  `periodicidad` enum('MENSUAL','UNICO') NOT NULL DEFAULT 'MENSUAL',
  `fecha` date NOT NULL DEFAULT (curdate()),
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_ingresos_usuario_fecha` (`usuario_id`,`fecha`),
  CONSTRAINT `fk_ingresos_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_ingresos_monto` CHECK ((`monto` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `metas_ahorro`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `metas_ahorro` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `usuario_id` int unsigned NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `tipo` enum('FONDO_EMERGENCIA','META') NOT NULL DEFAULT 'META',
  `monto_objetivo` decimal(15,2) NOT NULL,
  `monto_actual` decimal(15,2) NOT NULL DEFAULT '0.00',
  `fecha_objetivo` date DEFAULT NULL,
  `estado` enum('ACTIVA','CUMPLIDA','CANCELADA') NOT NULL DEFAULT 'ACTIVA',
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_metas_usuario_estado` (`usuario_id`,`estado`),
  CONSTRAINT `fk_metas_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_metas_actual` CHECK ((`monto_actual` >= 0)),
  CONSTRAINT `chk_metas_objetivo` CHECK ((`monto_objetivo` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `pagos_deuda`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pagos_deuda` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `deuda_id` int unsigned NOT NULL,
  `fecha_pago` date NOT NULL,
  `monto` decimal(15,2) NOT NULL,
  `numero_cuota` smallint unsigned DEFAULT NULL,
  `abono_capital` decimal(15,2) DEFAULT NULL,
  `intereses` decimal(15,2) DEFAULT NULL,
  `saldo_despues` decimal(15,2) DEFAULT NULL COMMENT 'Saldo de la deuda tras este pago',
  `observacion` varchar(200) DEFAULT NULL,
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_pagos_deuda_fecha` (`deuda_id`,`fecha_pago`),
  CONSTRAINT `fk_pagos_deuda` FOREIGN KEY (`deuda_id`) REFERENCES `deudas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_pagos_monto` CHECK ((`monto` > 0)),
  CONSTRAINT `chk_pagos_saldo` CHECK (((`saldo_despues` is null) or (`saldo_despues` >= 0)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `tipos_deuda`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipos_deuda` (
  `id` tinyint unsigned NOT NULL AUTO_INCREMENT,
  `codigo` varchar(30) NOT NULL,
  `nombre` varchar(60) NOT NULL,
  `icono` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_tipos_deuda_codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `correo` varchar(150) NOT NULL,
  `contrasena_hash` varchar(255) DEFAULT NULL COMMENT 'Hash (bcrypt/argon2), nunca texto plano',
  `cantidad_hijos` tinyint unsigned NOT NULL DEFAULT '0',
  `acepto_terminos_en` datetime DEFAULT NULL,
  `acepto_tratamiento_datos_en` datetime DEFAULT NULL,
  `estado` enum('ACTIVO','INACTIVO') NOT NULL DEFAULT 'ACTIVO',
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_usuarios_correo` (`correo`),
  CONSTRAINT `chk_usuarios_nombre` CHECK ((char_length(trim(`nombre`)) > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
