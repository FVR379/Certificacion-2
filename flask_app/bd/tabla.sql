-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema certificaion-2
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema certificaion-2
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `certificaion-2` DEFAULT CHARACTER SET utf8 ;
USE `certificaion-2` ;

-- -----------------------------------------------------
-- Table `certificaion-2`.`usuarios`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `certificaion-2`.`usuarios` (
  `id` INT ZEROFILL NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(255) NULL,
  `apellido` VARCHAR(255) NULL,
  `e-mail` VARCHAR(255) NULL,
  `password` VARCHAR(255) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `certificaion-2`.`viajes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `certificaion-2`.`viajes` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `destino` VARCHAR(255) NULL,
  `fecha_inicio` DATETIME NULL,
  `fecha_fin` DATETIME NULL,
  `Itinerario` VARCHAR(255) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  `usuarios_id` INT ZEROFILL NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_viajes_usuarios_idx` (`usuarios_id` ASC) VISIBLE,
  CONSTRAINT `fk_viajes_usuarios`
    FOREIGN KEY (`usuarios_id`)
    REFERENCES `certificaion-2`.`usuarios` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `certificaion-2`.`viajes_usuarios` (
  `viaje_id` INT NOT NULL,
  `usuario_id` INT ZEROFILL NOT NULL,
  `created_at` DATETIME NULL,
  PRIMARY KEY (`viaje_id`, `usuario_id`),
  INDEX `fk_viajes_usuarios_usuario_idx` (`usuario_id` ASC),
  CONSTRAINT `fk_viajes_usuarios_viaje`
    FOREIGN KEY (`viaje_id`)
    REFERENCES `certificaion-2`.`viajes` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_viajes_usuarios_usuario`
    FOREIGN KEY (`usuario_id`)
    REFERENCES `certificaion-2`.`usuarios` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;